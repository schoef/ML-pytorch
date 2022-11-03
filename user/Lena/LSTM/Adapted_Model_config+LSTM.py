import torch
import uproot
import numpy as np
from matplotlib import pyplot as plt
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
import torch.nn as nn
import os

###################### general parameters #############################
import config_lstm as config
content_list = config.content_list
samples = config.samples
directory = config.directory
batches = 10000
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
learning_rate = 0.001
n_epochs= 1
input_size = len(content_list) 
hidden_size = 2*input_size
hidden_size2 = input_size + 5
output_size = len(samples)
LSTM = config.lstm

if (LSTM):
    vector_branches = ["mva_Jet_%s" % varname for varname in config.lstm_jetVarNames]
    max_timestep = config.lstm_jets_maxN
    input_size_lstm = len(vector_branches)
    hidden_size_lstm = 10 #!!! tensorflow
    num_layers = 2

######################### import training data ########################
x = { sample: uproot.concatenate( os.path.join( directory, "{sample}/{sample}.root".format(sample=sample))) for sample in samples }
x = { sample: np.array( [ getattr( array, branch ) for branch in content_list ] ).transpose() for sample, array in x.items() }

# weight wrt to largest sample
n_max_events= max(map( len, x.values() ))
w = {sample:n_max_events/len(x[sample]) for sample in samples}

y = {sample:i_sample*np.ones(len(x[sample])) for i_sample, sample in enumerate(samples)}
# Note to myself: y... "TTTT":0,0,0..., "TTbb":1,1,1... 

# make weights. This wastes some memory, but OK.
samples_weight = np.concatenate([ [w[sample]]*len(x[sample]) for sample in samples]) 
sampler = WeightedRandomSampler(samples_weight, len(samples_weight))

#It is time to concatenate
X = torch.Tensor(np.concatenate( [x[sample] for sample in samples] ))
y = torch.Tensor(np.concatenate( [y[sample] for sample in samples] ))
Y = torch.zeros( (len(X), len(samples)))
for i_sample in range(len(samples)):
    Y[:,i_sample][y.int()==i_sample]=1

V = np.zeros((len(Y)))

#############################################################################
if (LSTM):
    vec_br_f  = {}

    for i_training_sample, training_sample in enumerate(samples):
        upfile_name = os.path.join(os.path.expandvars(directory), training_sample, training_sample+'.root')
        with uproot.open(upfile_name) as upfile:
            vec_br_f[i_training_sample]   = {}
            for name, branch in upfile["Events"].arrays(vector_branches, library = "np").items():
                for i in range (branch.shape[0]):
                    branch[i]=np.pad(branch[i][:max_timestep], (0, max_timestep - len(branch[i][:max_timestep])))
                vec_br_f[i_training_sample][name] = branch
                print(name)

    vec_br = {name: np.concatenate( [vec_br_f[i_training_sample][name] for i_training_sample in range(len(samples))] ) for name in vector_branches}

    # put columns side by side and transpose the innermost two axis
    V           = np.column_stack( [np.stack(vec_br[name]) for name in vector_branches] ).reshape( len(Y), len(vector_branches), max_timestep).transpose((0,2,1))
    V = np.nan_to_num(V)

V = torch.Tensor(V)

class NewDataset(Dataset):

    def __init__(self, X,V,Y):
        self.x = X
        self.v = V
        self.y = Y
        self.n_samples = len(Y)
            
    def __getitem__(self, index):
        return self.x[index],self.v[index], self.y[index]

    def __len__(self):
        return self.n_samples
    
    def __givey__(self):
        return self.y

dataset = NewDataset(X,V,Y)
train_loader = DataLoader(dataset=dataset,
                          batch_size=batches,
                          sampler = sampler,
                          num_workers=0)

######################## set up nn ##########################################
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, hidden_size2, output_size, input_size_lstm, hidden_size_lstm, num_layers):
        super(NeuralNet, self).__init__()
        self.batchn = nn.BatchNorm1d(input_size)
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(hidden_size, hidden_size2)
        self.softm = nn.Softmax(dim = 1)
        
        if (LSTM):
            self.num_layers = num_layers
            self.hidden_size_lstm = hidden_size_lstm
            #self.batchn2 = nn.BatchNorm2d(input_size_lstm)
            self.lstm = nn.LSTM(input_size_lstm, hidden_size_lstm, num_layers, batch_first=True)
            self.linear3 = nn.Linear(hidden_size2+hidden_size_lstm, output_size)
        else:
            self.linear3 = nn.Linear(hidden_size2, output_size)    
        
        
        
    def forward(self, x, y):
        #Linear nn
        x1 = self.batchn(x)
        x1 = self.linear1(x1)
        x1 = self.relu(x1)
        x1 = self.linear2(x1)
        
        #LSTM
        if (LSTM):
            h0 = torch.zeros(self.num_layers, y.size(0), self.hidden_size_lstm).to(device) 
            c0 = torch.zeros(self.num_layers, y.size(0), self.hidden_size_lstm).to(device) 
            x2 = self.relu(y)
            x2, _ = self.lstm(x2, (h0,c0))
            x2 = x2[:, -1, :]        
            x1 = torch.cat([x1, x2], dim=1)          
        x1 = self.relu(x1)
        x1 = self.linear3(x1)
        x1 = self.softm(x1)        
        return x1


if (LSTM==False):    
    model = NeuralNet(input_size, hidden_size,hidden_size2, output_size, input_size_lstm=0, hidden_size_lstm=0, num_layers=0).to(device)    
else:
    model = NeuralNet(input_size, hidden_size, hidden_size2, output_size, input_size_lstm, hidden_size_lstm, num_layers).to(device) 
    
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate) 
losses = []

dir_name = 'Results'
if (LSTM): dir_name = dir_name +  '_LSTM'
results_dir = './'+dir_name+'/'
if not os.path.exists( results_dir ): 
    os.makedirs( results_dir )


############################## training the model #############################
for epoch in range(n_epochs):
    print("		epoch: ", epoch+1 , " of ", n_epochs)
    for i, data in enumerate(train_loader):
        inputs1,inputs2, labels = data
        z = model(inputs1, inputs2)
        loss=criterion(z,labels)
        losses.append(loss.data)
        print(loss.data)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        #print(loss.data)
        
    with torch.no_grad():
        z = model(X, V)
        y_testpred = torch.max(z.data, 1).indices.numpy() 
        y_testtrue = torch.max(Y.data,1).indices.numpy()
        hist1 = []; hist2 = []; hist3 = []; hist4 = []
        bins = [0, 1, 2, 3, 4]
        for j in range (Y.size(0)):
            if (y_testtrue[j] == 0): hist1.append(y_testpred[j])
            if (y_testtrue[j] == 1): hist2.append(y_testpred[j])
            if (y_testtrue[j] == 2): hist3.append(y_testpred[j])
            if (y_testtrue[j] == 3): hist4.append(y_testpred[j])
        fig, az = plt.subplots(figsize = (7,7))
        plt.xticks([])
        plt.hist([hist1, hist2, hist3, hist4], bins, stacked = True,label = ["TTTT", "TTLep_bb","TTLep_cc","TTLep_other"]) 
        plt.legend()
        lab = "epoch = "+str(epoch)
        plt.title(lab)
        sample_file_name = "epoch="+str(epoch+1)+".png"
        plt.savefig(results_dir + sample_file_name)
        
        
fig, ay = plt.subplots()        
plt.plot(losses)
plt.title("Losses over epoch")
sample_file_name = "losses.png"
plt.savefig(results_dir + sample_file_name)

############################### test the model #####################################
with torch.no_grad():
    x = X[0,:].reshape(1,len(content_list))
    if (LSTM):
        v = V[0,:,:].reshape(1, max_timestep, len(vector_branches))
        name = "./model_lstm.onnx"
    else: 
        v = V[0].reshape(1,1)
        name = "./model.onnx"       
    torch.onnx.export(model,args=(x, v),f=name,input_names=["input1", "input2"],output_names=["output1"]) 
  