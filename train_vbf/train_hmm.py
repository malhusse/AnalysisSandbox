import sys
import os
import ROOT as R
import glob

#  Create The Keras Model(s), and save to current directory
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, BatchNormalization
import keras.regularizers as regularizers


model = Sequential()
model.add(Dense(225, input_dim=14, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(100, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64, activation='relu'))
model.add(Dense(2, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='Adam',
              metrics=['accuracy', ])

model.summary()
model.save('pyKerasModel_UI.h5')


# model2 = Sequential()
# model2.add(Dense(40, input_dim=14, activation='sigmoid',use_bias=True,kernel_initializer='glorot_normal',bias_initializer='zeros',kernel_regularizer=regularizers.l2(0.01),bias_regularizer=regularizers.l2(0.01)))
# model2.add(BatchNormalization() )
# model2.add(Dropout(0.10))
# model2.add(Dense(30,activation='tanh',use_bias=True,kernel_regularizer=regularizers.l2(0.01),kernel_initializer='glorot_normal',bias_initializer='zeros'))
# model2.add(BatchNormalization() )
# model2.add(Dense(10,activation='tanh',use_bias=True,kernel_initializer='glorot_normal',bias_initializer='zeros'))
# model2.add(Dense(2,activation='sigmoid'))

# model2.compile(loss='binary_crossentropy',
#               optimizer='sgd',
#               metrics=['accuracy', ])

# model2.save('pyKerasModel_MIT.h5')
#classifier.fit_generator(fill(8000),steps_per_epoch=100, epochs=10,callbacks=[WeightsSaver()],workers=4)

# model3 = Sequential()
# model3.add(Dense(50, input_dim=14, activation='relu'))
# model3.add(Dropout(0.2))
# model3.add(Dense(30, activation='relu'))
# model3.add(Dropout(0.2))
# model3.add(Dense(20, activation='relu'))
# model3.add(Dropout(0.2))
# model3.add(Dense(10, activation='relu'))
# model3.add(Dropout(0.2))
# model3.add(Dense(100, activation='relu'))
# model3.add(Dropout(0.2))
# model3.add(Dense(2, activation='sigmoid'))

# model3.compile(loss='binary_crossentropy',
#               optimizer='Adam',
#               metrics=['accuracy', ])

# model3.save('pyKerasModel_UCSD_CERN.h5')
# model.fit(trainx, traincy, batch_size=5000, epochs=100, shuffle=True, validation_data=(testx, testcy))



R.TMVA.Tools.Instance()
# to run PyKeras
R.TMVA.PyMethodBase.PyInitialize()
# R.gROOT.SetBatch()

files = glob.glob("/home/mo/Analysis/AnalysisTools/ntupleFiles/*.root")
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
dataloader.GetDataSetInfo().AddClass("Signal")
dataloader.GetDataSetInfo().AddClass("Background")  

features = [
    "h_pt", "h_eta", "h_deta", "h_dphi", "jeteta_1", "jeteta_2", "ncentJets",
    "njets", "mjj_1", "mjj_2", "detajj_1", "detajj_2", "nbtagJets",
    "metpt"
]

for x in features:
    dataloader.AddVariable(x)

# dataloader.AddSpectator("h_mass")
dataloader.SetBackgroundWeightExpression("eweight*41860")
dataloader.SetSignalWeightExpression("eweight*41860")

dataloader.AddSignalTree(t, 1.0)
dataloader.AddBackgroundTree(t, 1.0)

# signal mclabel is negative, background is positive
sigCut = R.TCut("(h_mass > 100 && h_mass < 150) && mclabel == -20 && Entry$%2!=0")
bkgCut = R.TCut("(h_mass > 100 && h_mass < 150) && mclabel > 0 && Entry$%2!=0")

dataloader.PrepareTrainingAndTestTree(
    sigCut, bkgCut,
    "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V")

factory.BookMethod(
    dataloader, R.TMVA.Types.kBDT, "BDT",
    "!H:!V:NTrees=500::BoostType=Grad:Shrinkage=0.1:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=5:NegWeightTreatment=Pray"
)


factory.BookMethod(dataloader, R.TMVA.Types.kPyKeras, "DNN",
                   '!H:!V:VarTransform=G:FilenameModel=pyKerasModel_UI.h5:FilenameTrainedModel=trainedpyKerasModel_UI.h5:NumEpochs=100:BatchSize=1000:TriesEarlyStopping=4')

# factory.BookMethod(dataloader, R.TMVA.Types.kPyKeras, "DNN_MIT",
#                    '!H:!V:VarTransform=G:FilenameModel=pyKerasModel_MIT.h5:FilenameTrainedModel=trainedpyKerasModel_MIT.h5:NumEpochs=100:BatchSize=1000:TriesEarlyStopping=4')

# factory.BookMethod(dataloader, R.TMVA.Types.kPyKeras, "DNN_USCD_CERN",
#                    '!H:!V:VarTransform=G:FilenameModel=pyKerasModel_UCSD_CERN.h5:FilenameTrainedModel=trainedpyKerasModel_UCSD_CERN.h5:NumEpochs=100:BatchSize=1000:TriesEarlyStopping=4')

factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
