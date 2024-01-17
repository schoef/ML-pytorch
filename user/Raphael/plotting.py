# This script is for plotting the results of the Training

import matplotlib.pyplot as plt
import numpy as np
import ROOT, os
import torch
import torch.nn as nn
import neural_network_pytorch as nnp

#Settings 
Plot_loss = 1
Plot_y_pred_hist=0
Plot_ratio_hist =0
Plot_weighted=1

plot_options =  {
    "met": {'binning': [20, 100, 500], 'logY': True, 'tex': r'$E_{T}^{\mathrm{miss}}$'},
    "ht": {'binning': [20, 500, 1500], 'logY': True, 'tex': r'$H_{T}$'},
    "nJetGood": {'binning': [7, 3, 10], 'logY': False, 'tex': r'$N_{\mathrm{jet}}$'},
    "jet0_pt": {'binning': [30, 0, 1000], 'logY': True, 'tex': r'$p_{T}(\mathrm{jet\ 0})$'},
    "jet1_pt": {'binning': [30, 0, 1000], 'logY': True, 'tex': r'$p_{T}(\mathrm{jet\ 1})$'},
    "jet2_pt": {'binning': [30, 0, 500], 'logY': True, 'tex': r'$p_{T}(\mathrm{jet\ 2})$'},
    "jet3_pt": {'binning': [30, 0, 500], 'logY': True, 'tex': r'$p_{T}(\mathrm{jet\ 3})$'},
    "jet4_pt": {'binning': [30, 0, 500], 'logY': True, 'tex': r'$p_{T}(\mathrm{jet\ 4})$'},
    "jet0_eta": {'binning': [30, -4, 4], 'logY': False, 'tex': r'$\eta(\mathrm{jet\ 0})$'},
    "jet1_eta": {'binning': [30, -4, 4], 'logY': False, 'tex': r'$\eta(\mathrm{jet\ 1})$'},
    "jet2_eta": {'binning': [30, -4, 4], 'logY': False, 'tex': r'$\eta(\mathrm{jet\ 2})$'},
    "jet3_eta": {'binning': [30, -4, 4], 'logY': False, 'tex': r'$\eta(\mathrm{jet\ 3})$'},
    "jet4_eta": {'binning': [30, -4, 4], 'logY': False, 'tex': r'$\eta(\mathrm{jet\ 4})$'},
}

feature_names = [ "nJetGood", "ht", "jet0_pt", "jet1_pt", "jet2_pt", "jet3_pt", "jet0_eta", "jet1_eta", "jet2_eta", "jet3_eta" ]

#Load Data
loaded_data = np.load('training_data.npz', allow_pickle=True)
loss_array=loaded_data['loss_array']
loaded_model = nnp.NeuralNetwork(nnp.n_var_flat, nnp.args.quadratic)
loaded_model.load_state_dict(torch.load('best_model.pth'))
loaded_model.eval()

generator = nnp.data_model.DataGenerator()  # Adjust maxN as needed
features, variations = generator[0]

### Plotting
output_folder = 'Plots'
os.makedirs(output_folder, exist_ok=True)

#Create Histogramm for y_pred values
if Plot_y_pred_hist:
    plt.hist(y_pred.detach().numpy(), bins=10)
    plt.title('Y Pred Values')
    plt.xlabel('Values')
    plt.ylabel('Number')
    output_path = os.path.join(output_folder, 'Histo_Pred.png')
    plt.savefig(output_path)
    plt.clf()

#Create Histogramm for Ratio values
if Plot_ratio_hist:
    plt.hist(ratio.detach().numpy(), bins=10)
    plt.title('Ratio Values')
    plt.xlabel('Values')
    plt.ylabel('Number')
    output_path = os.path.join(output_folder, 'Histo_Ratio.png')
    plt.savefig(output_path)
    plt.clf()


#Create loss plots
if Plot_loss:
    plt.xlabel('Epoch')
    plt.ylabel('Loss Value')
    plt.title('Loss Function')
    plt.plot(loss_array)
    output_path= os.path.join(output_folder, 'Loss.png')
    plt.savefig(output_path)
    plt.clf()

#Create weighted Histogramms
if Plot_weighted:
    ratio_array=[]
    unique_variations=np.unique(variations)
    nominal_features= features[(variations[:, 0] == 0)] #filter the nominal data
    nominal_features_tensor=   torch.tensor(nominal_features, dtype=torch.float32)
    nominal_features_tensor =  torch.where(torch.isnan(nominal_features_tensor), torch.tensor(0.0), nominal_features_tensor)  
    for i_variation_value, variation_value in enumerate(unique_variations):
        if variation_value ==0:
            ratio_array.append(0)
        if variation_value != 0:
            delta=loaded_model(nominal_features_tensor,variation_value)
            ratio=torch.exp(variation_value*delta)
            ratio_array.append(ratio)

    column_arrays=np.split(features,features.shape[1],axis=1)
    for i_feature, feature in enumerate(feature_names):
        binning_info = plot_options[feature]['binning']
        bins = np.linspace(binning_info[1], binning_info[2], binning_info[0] + 1)
        nominal_data = column_arrays[i_feature][variations == 0]
        n_nominal, _ = np.histogram(nominal_data, bins=bins)
        n_nominal_safe = np.where(n_nominal == 0, 1, n_nominal)     #avoid division by 0
        for i_variation_value, variation_value in enumerate(unique_variations):
            selected_data = column_arrays[i_feature][variations == variation_value]
            n, _ = np.histogram(selected_data, bins=bins) 
            normalized_histogram= n /n_nominal_safe  #Truth  
            if i_variation_value != 4:
                weights=ratio_array[i_variation_value]
                weights=weights.detach().numpy()
                weights=np.squeeze(weights, axis=1)
                n_nominal_w, _ = np.histogram(nominal_data,bins=bins, weights=weights)
                n_nominal_w_safe = np.where(n_nominal_w == 0, 1, n_nominal_w)
                normalized_histogram_w = n / n_nominal_w_safe   #Prediction
            label = f'$\sigma = {variation_value}$ (Pred)'
            color = plt.cm.viridis(i_variation_value/len(unique_variations))
            if i_variation_value != 4:
                plt.plot(bins[1:],normalized_histogram_w, drawstyle='steps', color = color, linestyle='dashed', label=label) #Prediction
            plt.plot(bins[1:],normalized_histogram, drawstyle='steps', color = color)  #Truth

        plt.xlabel(plot_options[feature]['tex'])
        plt.ylabel('Normalized events weighted')
        scale_info = plot_options[feature]['logY']
        if scale_info == True:
            plt.yscale('log')
        else:
            plt.yscale('linear')
        output_path = os.path.join(output_folder, 'weightedvariation_'+ feature + '.png')
        plt.legend(loc='best')
        plt.savefig(output_path)
        plt.clf()

