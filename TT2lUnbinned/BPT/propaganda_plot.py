#!/usr/bin/env python

# Standard imports
import ROOT
import numpy as np
import random
import cProfile
import time
import os, sys
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

from math import log, exp, sin, cos, sqrt, pi
import copy
import pickle
import itertools

dir_path = os.path.dirname(os.path.realpath(__file__))
ROOT.gROOT.LoadMacro(os.path.join( dir_path, "../../tools/scripts/tdrstyle.C"))
ROOT.setTDRStyle()

from   tools import helpers
import tools.syncer as syncer

from BPT.BoostedParametricTree import BoostedParametricTree

# User
import tools.user as user

# Parser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--plot_directory",     action="store",      default="BPT",                 help="plot sub-directory")
argParser.add_argument("--version",            action="store",      default="",                 help="Which version?")
argParser.add_argument("--model",              action="store",      default="analytic",                 help="Which model?")
argParser.add_argument("--modelDir",          action="store",      default="models",                 help="Which model directory?")
argParser.add_argument("--variation",          action="store",      default=None, type=str,  help="variation")
argParser.add_argument("--era",                action="store",      default="RunII", choices = ["RunII", "Summer16_preVFP", "Summer16", "Fall17", "Autumn18"], type=str,  help="variation")
argParser.add_argument("--nTraining",          action="store",      default=50000,       type=int,  help="number of training events")
argParser.add_argument('--feature',         action='store',      default="tr_ttbar_pt", help="Which feature?")
#argParser.add_argument('--auto_clip',          action='store',      default=None, type=float, help="Remove quantiles of the training variable?")

args, extra = argParser.parse_known_args(sys.argv[1:])

def parse_value( s ):
    try:
        r = int( s )
    except ValueError:
        try:
            r = float(s)
        except ValueError:
            r = s
    return r

extra_args = {}
key        = None
for arg in extra:
    if arg.startswith('--'):
        # previous no value? -> Interpret as flag
        #if key is not None and extra_args[key] is None:
        #    extra_args[key]=True
        key = arg.lstrip('-')
        extra_args[key] = True # without values, interpret as flag
        continue
    else:
        if type(extra_args[key])==type([]):
            extra_args[key].append( parse_value(arg) )
        else:
            extra_args[key] = [parse_value(arg)]
for key, val in extra_args.items():
    if type(val)==type([]) and len(val)==1:
        extra_args[key]=val[0]

# import the model
exec('import %s.%s as model'%( args.modelDir, args.model)) 

print("Set model era to:", args.era)
model.set_era( args.era )

cfg = model.bpt_cfg
cfg.update( extra_args )

feature_names = model.feature_names

# directory for plots
plot_directory = os.path.join( user.plot_directory, args.plot_directory,
    args.version, args.era, 
    args.model
        + ("_"+args.variation if args.variation is not None else "")
    )

if not os.path.isdir(plot_directory):
    try:
        os.makedirs( plot_directory )
    except IOError:
        pass

training_data_filename = os.path.join(user.data_directory, args.version, args.era, args.model+("_"+args.variation if args.variation is not None else ""), "training_%i"%args.nTraining)+'.pkl'

with open( training_data_filename, 'rb') as _file:
    training_data = pickle.load( _file )
    total_size    =  sum([len(s['features']) for s in training_data.values() if 'features' in s ])
    print ("Loaded training data from ", training_data_filename, "with size", total_size)

# Text on the plots
def drawObjects( offset=0 ):
    tex1 = ROOT.TLatex()
    tex1.SetNDC()
    tex1.SetTextSize(0.05)
    tex1.SetTextAlign(11) # align right

    tex2 = ROOT.TLatex()
    tex2.SetNDC()
    tex2.SetTextSize(0.04)
    tex2.SetTextAlign(11) # align right

    line1 = ( 0.15+offset, 0.95, "Boosted Param Trees" )
    return [ tex1.DrawLatex(*line1) ]#, tex2.DrawLatex(*line2) ]

nominal_base_point_index = np.where(np.all(np.array(model.base_points)==np.array(model.nominal_base_point),axis=1))[0][0] 

postfix = ("_"+args.version if args.version != "" else "") + ("_"+args.era if args.era != "RunII" else "")
if args.variation == None:
    bpt_name = "BPT_%s_nTraining_%i_nTrees_%i"%(args.model+postfix, args.nTraining, cfg["n_trees"])
else:
    bpt_name = "BPT_%s_%s_nTraining_%i_nTrees_%i"%(args.model+postfix, args.variation, args.nTraining, cfg["n_trees"])

filename = os.path.join(user.model_directory, 'BPT', bpt_name)+'.pkl'

print ("Loading %s from %s"%(bpt_name, filename))
bpt = BoostedParametricTree.load(filename)

import propaganda_plot_options as plot_options

predicted_reweights = np.exp( np.dot( bpt.vectorized_predict(training_data[model.nominal_base_point]['features']), bpt.VkA.transpose() ) )

colors = [ ROOT.kRed + 2, ROOT.kRed -4,ROOT.kCyan +2, ROOT.kCyan -4, ROOT.kMagenta+2,  ROOT.kMagenta-4,  ROOT.kBlue+2,     ROOT.kBlue-4,     ROOT.kGreen+2,    ROOT.kGreen-4, ROOT.kOrange+6, ROOT.kOrange+3] 

h_truth = {}
h_pred  = {}
h_truth_shape = {}
h_pred_shape  = {}
for i_point, point in enumerate(model.base_points):

    name     = '_'.join( [ (model.parameters[i_param]+'_%3.2f'%param).replace('.','p').replace('-','m') for i_param, param in enumerate(point)])
    tex_postfix = "_{%s}"%model.tex(args.variation) if args.variation is not None else ""
    tex_name = '_'.join( [ (model.tex(model.parameters[i_param])+tex_postfix+(' = %2.1f'%param).rstrip(".0")) for i_param, param in enumerate(point)])
    is_nominal = tuple(point) == tuple(model.nominal_base_point)
    if is_nominal:
        nominal_index = i_point
        nominal_name  = name

    h_truth[tuple(point)] = {'name':name, 'tex':tex_name+" (truth)"}
    h_pred[tuple(point)]  = {'name':name, 'tex':tex_name+" (pred)"}
    h_truth_shape[tuple(point)] = {'name':name, 'tex':tex_name+" (truth)"}
    h_pred_shape[tuple(point)]  = {'name':name, 'tex':tex_name+" (pred)"}

    if args.feature not in plot_options:
        print("Feature %s not found in propaganda plot_options! Do nothing", args.feature)
        raise RuntimeError

    h_truth[tuple(point)][feature] = ROOT.TH1F(name+'_'+feature+'_nom',    name+'_'+feature, *propaganda.plot_options[feature]['binning'] )
    h_pred[tuple(point)][feature]  = ROOT.TH1F(name+'_'+feature+'_nom',    name+'_'+feature, *propaganda.plot_options[feature]['binning'] )

    binning = propaganda.plot_options[feature]['binning']

    if "weights" in training_data[model.nominal_base_point]:
        nominal_weights = training_data[model.nominal_base_point]['weights']
    else:
        nominal_weights = np.ones( len( training_data[model.nominal_base_point]['features']))

    if "weights" in training_data[tuple(point)]:
        weights = training_data[tuple(point)]['weights']
    else:
        weights = np.ones( len( training_data[tuple(point)]['features'])) 

    h_truth[tuple(point)][feature] = helpers.make_TH1F( np.histogram(
        training_data[tuple(point)]['features'][:,i_feature] if 'features' in training_data[tuple(point)] else training_data[model.nominal_base_point]['features'][:,i_feature],
        bins=np.linspace(binning[1], binning[2], binning[0]+1), weights=weights
        ))
    h_pred[tuple(point)][feature] = helpers.make_TH1F( np.histogram(
        training_data[model.nominal_base_point]['features'][:,i_feature],
        bins=np.linspace(binning[1], binning[2], binning[0]+1), weights=nominal_weights*predicted_reweights[:,i_point]
        ))

    color = colors[i_point] if not is_nominal else ROOT.kBlack
    h_truth[tuple(point)][feature].SetLineWidth(2)
    h_truth[tuple(point)][feature].SetLineColor( color )
    h_truth[tuple(point)][feature].SetLineStyle(ROOT.kDashed)
    h_truth[tuple(point)][feature].SetMarkerColor(color)
    h_truth[tuple(point)][feature].SetMarkerStyle(0)
    h_truth[tuple(point)][feature].GetXaxis().SetTitle(propaganda.plot_options[feature]['tex'])
    h_truth[tuple(point)][feature].GetYaxis().SetTitle("1/#sigma_{SM}d#sigma/d%s"%propaganda.plot_options[feature]['tex'])
    h_pred[tuple(point)][feature].SetLineWidth(2)
    h_pred[tuple(point)][feature].SetLineColor( color )
    h_pred[tuple(point)][feature].SetMarkerColor(color)
    h_pred[tuple(point)][feature].SetMarkerStyle(0)
    h_pred[tuple(point)][feature].GetXaxis().SetTitle(propaganda.plot_options[feature]['tex'])
    h_pred[tuple(point)][feature].GetYaxis().SetTitle("1/#sigma_{SM}d#sigma/d%s"%propaganda.plot_options[feature]['tex'])

    h_truth_shape[tuple(point)][feature] = h_truth[tuple(point)][feature].Clone()
    h_pred_shape[tuple(point)][feature] = h_pred[tuple(point)][feature].Clone()

assert False, ""

# make shape plots
for feature in args.propaganda:
    for i_point, point in enumerate(model.base_points):

        for logY in [False, True]:
            c1 = ROOT.TCanvas("c1")
            ROOT.gStyle.SetOptStat(0)

            l = ROOT.TLegend(0.2,0.1,0.9,0.85)
            stuff.append(l)
            l.SetNColumns(2)
            l.SetFillStyle(0)
            l.SetShadowColor(ROOT.kWhite)
            l.SetBorderSize(0)
            # feature plots

            for i_point, point in enumerate(model.base_points):
                h_truth[tuple(point)][feature].Draw("same") 
                h_pred[tuple(point)][feature].Draw("same") 
                if i_feature==0:
                    l.AddEntry(  h_truth[tuple(point)][feature],  h_truth[tuple(point)]["tex"])
                    l.AddEntry(  h_pred[tuple(point)][feature],   h_pred[tuple(point)]["tex"])

            max_ = max( map( lambda h:h.GetMaximum(), [h_truth[tuple(point)][feature] for point in model.base_points] ))
            max_ = 10**(1.5)*max_ if logY else 1.5*max_
            min_ = min( map( lambda h:h.GetMinimum(), [h_truth[tuple(point)][feature] for point in model.base_points] ))
            min_ = 0.1 if logY else (1.5*min_ if min_<0 else 0.75*min_)

            first = True
            for h in [h_pred[tuple(point)][feature] for point in model.base_points] +  [h_truth[tuple(point)][feature] for point in model.base_points]:
                if first:
                    h.Draw("h")
                    ROOT.gPad.SetLogy(logY)
                else:
                    h .Draw("hsame")
                h.GetYaxis().SetRangeUser(min_, max_)
                h .Draw("hsame")
                first=False
            c1.SetLogy(logY)

            l.Draw()

            plot_directory_ = os.path.join( plot_directory, "propaganda_plots", bpt_name, "log" if logY else "lin" )
            if not os.path.isdir(plot_directory_):
                try:
                    os.makedirs( plot_directory_ )
                except IOError:
                    pass

            helpers.copyIndexPHP( plot_directory_ )
            c1.Print( os.path.join( plot_directory_, "%s.png"%feature ) )

            for i_point, point in enumerate(model.base_points):
                h_truth_shape[tuple(point)][feature].Divide(h_truth[model.nominal_base_point][feature])
                h_pred_shape[tuple(point)][feature].Divide(h_truth[model.nominal_base_point][feature])
                h_truth_shape[tuple(point)][feature].Draw("same") 
                h_pred_shape[tuple(point)][feature].Draw("same") 

            max_ = max( map( lambda h:h.GetMaximum(), [h_truth_shape[tuple(point)][feature] for point in model.base_points] ))
            max_ = 10**(1.5)*max_ if logY else 1+1.3*(max_-1)
            min_ = min( map( lambda h:h.GetMinimum(), [h_truth_shape[tuple(point)][feature] for point in model.base_points] ))
            min_ = 0.1 if logY else 1-1.3*(1-min_)

            first = True
            for h in [h_pred_shape[tuple(point)][feature] for point in model.base_points] +  [h_truth_shape[tuple(point)][feature] for point in model.base_points]:
                if first:
                    h.Draw("h")
                    ROOT.gPad.SetLogy(logY)
                else:
                    h .Draw("hsame")
                h.GetYaxis().SetRangeUser(min_, max_)
                h .Draw("hsame")
                first=False

            c1.SetLogy(logY)

            l.Draw()

            plot_directory_ = os.path.join( plot_directory, "propaganda_plots", bpt_name, "log" if logY else "lin" )
            if not os.path.isdir(plot_directory_):
                try:
                    os.makedirs( plot_directory_ )
                except IOError:
                    pass
            helpers.copyIndexPHP( plot_directory_ )
            c1.Print( os.path.join( plot_directory_, "%s_shape.png"%feature ) )

syncer.sync()
