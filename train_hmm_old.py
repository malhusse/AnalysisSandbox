import sys, os
import ROOT as R
import glob

# Create The Keras Model(s), and save to current directory
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, BatchNormalization, Flatten
import keras.regularizers as regularizers
features = [
    "h_pt", "h_eta", "h_phi", "h_deta", "h_dphi", "mueta_1", "mueta_2", "ncentJets",
    "njets", "mjj_1", "mjj_2", "detajj_1", "detajj_2", "nbtagJets", 
    "metpt"
]

model = Sequential()
model.add(Dense(40, input_dim=len(features),activation='sigmoid',use_bias=True,kernel_initializer='glorot_normal',bias_initializer='zeros',kernel_regularizer=regularizers.l2(0.01),bias_regularizer=regularizers.l2(0.01)) )
model.add(BatchNormalization() )
model.add(Dropout(0.10))
model.add(Dense(30,activation='tanh',use_bias=True,kernel_regularizer=regularizers.l2(0.01),kernel_initializer='glorot_normal',bias_initializer='zeros'))
model.add(BatchNormalization() )
model.add(Dense(10,activation='tanh',use_bias=True,kernel_initializer='glorot_normal',bias_initializer='zeros'))
model.add(Dense(4,activation='sigmoid'))

model.compile(
        #loss='mean_squared_error',
        loss='binary_crossentropy',
        #loss=roc_area,
        optimizer='sgd',
        #optimizer='adam',
        metrics=['accuracy'])


model.save('hmumuDNN.h5')

# should implement a list that contains the created keras modelsgmu
# and is then read by tmva's BookMethod

# Run TMVA using wanted methods. 
R.TMVA.Tools.Instance()
R.TMVA.PyMethodBase.PyInitialize()
# R.gROOT.SetBatch()

files = glob.glob("ntupleFiles/*.root")
t = R.TChain("ntupledData")

for file in files:
    t.Add(file)

outname = "MVA.root"
out = R.TFile(outname, "RECREATE")

analysis = "Classification"
factory = R.TMVA.Factory(
    "factory", out,
    "!V:!Silent:Color:DrawProgressBar:Transformations=I;:AnalysisType=%s" % analysis)

dataloader = R.TMVA.DataLoader("dataset_test")




for x in features:
    dataloader.AddVariable(x)

dataloader.AddSpectator("h_mass")
dataloader.SetBackgroundWeightExpression("eweight*41860")
dataloader.SetSignalWeightExpression("eweight*41860")

dataloader.AddSignalTree(t, 1.0)
dataloader.AddBackgroundTree(t, 1.0)

# signal mclabel is negative, background is positive
sigCut = R.TCut("(h_mass > 110 && h_mass < 150) && mclabel < 0")
bkgCut = R.TCut("(h_mass > 110 && h_mass < 150) && mclabel > 0")

dataloader.PrepareTrainingAndTestTree(
    sigCut, bkgCut,
    "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V")


factory.BookMethod(
    dataloader, R.TMVA.Types.kBDT, "BDT",
    "!H:!V:NTrees=1200:MinNodeSize=3%:BoostType=Grad:Shrinkage=0.10:nCuts=40:MaxDepth=5:NodePurityLimit=0.99:SeparationType=SDivSqrtSPlusB:Pray"
)

factory.BookMethod(dataloader, R.TMVA.Types.kPyKeras, "Keras_DNN",'!H:!V:VarTransform=D,G:FilenameModel=hmumuDNN.h5:FilenameTrainedModel=trainedhmumuDNN.h5:NumEpochs=100:BatchSize=100:TriesEarlyStopping=2')


factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
