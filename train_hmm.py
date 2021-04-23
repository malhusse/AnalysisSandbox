import sys
import os
import ROOT as R
import glob

# Create The Keras Model(s), and save to current directory
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout

model = Sequential()
model.add(Dense(225, input_dim=15, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(100, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(2, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='Adam',
              metrics=['accuracy', ])

model.summary()
exit(1)
model.save('pyKerasModel_f.h5')

R.TMVA.Tools.Instance()
# to run PyKeras
R.TMVA.PyMethodBase.PyInitialize()
# R.gROOT.SetBatch()

files = glob.glob("ntupleFiles/*.root")
t = R.TChain("ntupledData")

for file in files:
    t.Add(file)

outname = "TMVA_Output.root"
out = R.TFile(outname, "RECREATE")

analysis = "Classification"
factory = R.TMVA.Factory(
    "factory", out,
    "!V:!Silent:Color:DrawProgressBar:Transformations=I;:AnalysisType=%s" % analysis)

dataloader = R.TMVA.DataLoader("dataset_f")

features = [
    "h_pt", "h_eta", "h_phi", "h_deta", "h_dphi", "mueta_1", "mueta_2", "ncentJets",
    "njets", "mjj_1", "mjj_2", "detajj_1", "detajj_2", "nbtagJets",
    "metpt"
]

for x in features:
    dataloader.AddVariable(x)

# dataloader.AddSpectator("h_mass")
dataloader.SetBackgroundWeightExpression("eweight")
dataloader.SetSignalWeightExpression("eweight")

dataloader.AddSignalTree(t, 1.0)
dataloader.AddBackgroundTree(t, 1.0)

# signal mclabel is negative, background is positive
sigCut = R.TCut("(h_mass > 100 && h_mass < 150) && mclabel < 0 ")
bkgCut = R.TCut("(h_mass > 100 && h_mass < 150) && mclabel > 0 ")

dataloader.PrepareTrainingAndTestTree(
    sigCut, bkgCut,
    "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=EqualNumEvents:!V")

factory.BookMethod(
    dataloader, R.TMVA.Types.kBDT, "BDT",
    "!H:!V:NTrees=1200:MinNodeSize=3%:BoostType=Grad:Shrinkage=0.10:nCuts=40:MaxDepth=5:NodePurityLimit=0.99:SeparationType=SDivSqrtSPlusB:Pray"
)


factory.BookMethod(dataloader, R.TMVA.Types.kPyKeras, "pyKeras_DNN_G",
                   '!H:!V:VarTransform=G:FilenameModel=pyKerasModel_f.h5:FilenameTrainedModel=trainedPyKerasModel_f_G.h5:NumEpochs=100:BatchSize=1000:TriesEarlyStopping=2')


factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
