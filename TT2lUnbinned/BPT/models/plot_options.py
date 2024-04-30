from math import pi
plot_options =  {
    "tr_top_pt" :{'binning':[50,0,1500], 'tex':'p_{T}(t)'},
    "tr_top_eta" :{'binning':[30,-3,3], 'tex':'#eta(t)'},
    "tr_top_f1_pt" :{'binning':[30,0,800], 'tex':'p_{T}(f(t))'},
    "tr_top_f1_eta" :{'binning':[30,-3,3], 'tex':'#eta(f_{2}(t))'},
    "tr_top_f2_pt" :{'binning':[30,0,800], 'tex':'p_{T}(f_{2} (t))'},
    "tr_top_f2_eta" :{'binning':[30,-3,3], 'tex':'#eta(f_{2}(t))'},
    "tr_top_b_pt" :{'binning':[50,0,800], 'tex':'p_{T}(b (t))'},
    "tr_top_b_eta" :{'binning':[30,-3,3], 'tex':'#eta(b(t))'},
    "tr_top_W_pt" :{'binning':[30,0,1000], 'tex':'p_{T}(W (t))'},
    "tr_top_W_eta" :{'binning':[30,-3,3], 'tex':'#eta(W(t))'},

    "tr_topBar_pt" :{'binning':[50,0,1500], 'tex':'p_{T}(#bar{t})'},
    "tr_topBar_eta" :{'binning':[30,-3,3], 'tex':'#eta(#bar{t})'},
    "tr_topBar_f1_pt" :{'binning':[30,0,800], 'tex':'p_{T}(f_{1}(#bar{t}))'},
    "tr_topBar_f1_eta" :{'binning':[30,-3,3], 'tex':'#eta(f_{1}(#bar{t}))'},
    "tr_topBar_f2_pt" :{'binning':[30,0,800], 'tex':'p_{T}(f_{2} (#bar{t}))'},
    "tr_topBar_f2_eta" :{'binning':[30,-3,3], 'tex':'#eta(f_{2}(#bar{t}))'},
    "tr_topBar_b_pt" :{'binning':[50,0,800], 'tex':'p_{T}(b (#bar{t}))'},
    "tr_topBar_b_eta" :{'binning':[30,-3,3], 'tex':'#eta(b(#bar{t}))'},
    "tr_topBar_W_pt" :{'binning':[30,0,1000], 'tex':'p_{T}(W (#bar{t}))'},
    "tr_topBar_W_eta" :{'binning':[30,-3,3], 'tex':'#eta(W(#bar{t}))'},

    "tr_topBar_pt":{'binning':[50,0,1000], 'tex':'p_{T}(t#bar{t})'},
    "tr_topBar_mass":{'binning':[50,0,2000], 'tex':'M(t#bar{t})'},
    "tr_topBar_eta":{'binning':[30,-3,3], 'tex':'#eta(t#bar{t})'},
    "tr_topBar_dEta":{'binning':[30,-3,3], 'tex':'#Delta#eta(t#bar{t})'},
    "tr_topBar_dAbsEta":{'binning':[30,-3,3], 'tex':'#Delta|#eta|(t#bar{t})'},

    "tr_cosThetaPlus_n"     :{'binning':[30,-1,1], 'tex':'cos#theta^{+}_{n}'},
    "tr_cosThetaMinus_n"    :{'binning':[30,-1,1], 'tex':'cos#theta^{-}_{n}'},
    "tr_cosThetaPlus_r"     :{'binning':[30,-1,1], 'tex':'cos#theta^{+}_{r}'},
    "tr_cosThetaMinus_r"    :{'binning':[30,-1,1], 'tex':'cos#theta^{-}_{r}'},
    "tr_cosThetaPlus_k"     :{'binning':[30,-1,1], 'tex':'cos#theta^{+}_{k}'},
    "tr_cosThetaMinus_k"    :{'binning':[30,-1,1], 'tex':'cos#theta^{-}_{k}'},
    "tr_cosThetaPlus_r_star"    :{'binning':[30,-1,1], 'tex':'cos#theta^{+*}_{n}'},
    "tr_cosThetaMinus_r_star"   :{'binning':[30,-1,1], 'tex':'cos#theta^{-*}_{n}'},
    "tr_cosThetaPlus_k_star"    :{'binning':[30,-1,1], 'tex':'cos#theta^{+*}_{k}'},
    "tr_cosThetaMinus_k_star"   :{'binning':[30,-1,1], 'tex':'cos#theta^{-*}_{k}'},
    "tr_xi_nn"              :{'binning':[30,-1,1], 'tex':'#xi_{nn}'},
    "tr_xi_rr"              :{'binning':[30,-1,1], 'tex':'#xi_{rr}'},
    "tr_xi_kk"              :{'binning':[30,-1,1], 'tex':'#xi_{kk}'},
    "tr_xi_nr_plus"         :{'binning':[30,-1,1], 'tex':'#xi_{nr}^{+}'},
    "tr_xi_nr_minus"        :{'binning':[30,-1,1], 'tex':'#xi_{nr}^{-}'},
    "tr_xi_rk_plus"         :{'binning':[30,-1,1], 'tex':'#xi_{rk}^{+}'},
    "tr_xi_rk_minus"        :{'binning':[30,-1,1], 'tex':'#xi_{rk}^{-}'},
    "tr_xi_nk_plus"         :{'binning':[30,-1,1], 'tex':'#xi_{nk}^{+}'},
    "tr_xi_nk_minus"        :{'binning':[30,-1,1], 'tex':'#xi_{nk}^{-}'},

    "tr_xi_r_star_k"        :{'binning':[30,-1,1], 'tex':'#xi_{r^{*}k}'},
    "tr_xi_k_r_star"        :{'binning':[30,-1,1], 'tex':'#xi_{kr^{*}}'},
    "tr_xi_kk_star"         :{'binning':[30,-1,1], 'tex':'#xi_{kk^{*}}'},

    "tr_cos_phi"            :{'binning':[30,-1,1], 'tex':'cos(#phi)'},
    "tr_cos_phi_lab"        :{'binning':[30,-1,1], 'tex':'cos(#phi lab)'},
    "tr_abs_delta_phi_ll_lab":{'binning':[30,0,pi], 'tex':'|#Delta(#phi(l,l))|'},

    "l1_pt"         :{'binning':[36,40,400], 'tex':'p_{T}(l_{1})'},
    "l2_pt"         :{'binning':[18,20,200], 'tex':'p_{T}(l_{2})'},
    "recoLep01_pt"         :{'binning':[36,40,400], 'tex':'p_{T}(l_{1}+l_{2})'},
    "recoLep01_mass"         :{'binning':[36,40,400], 'tex':'M(l_{1}+l_{2})'},
    "recoLep0_pt"         :{'binning':[36,40,400], 'tex':'p_{T}(l_{1})'},
    "recoLep1_pt"         :{'binning':[18,20,200], 'tex':'p_{T}(l_{2})'},
    "recoLepPos_pt"         :{'binning':[36,40,400], 'tex':'p_{T}(l_{1})'},
    "recoLepNeg_pt"         :{'binning':[18,20,200], 'tex':'p_{T}(l_{2})'},
    "jet0_pt"         :{'binning':[28,60,900], 'tex':'p_{T}(j_{0})'},
    "jet1_pt"         :{'binning':[14,30,450], 'tex':'p_{T}(j_{1})'},
    "jet2_pt"         :{'binning':[9,30,300], 'tex':'p_{T}(j_{2})'},
    "tr_ttbar_mass"   :{'binning':[(4000-350)//73,350,4000], 'tex':'M(tt)'},
    "ht"              :{'binning':[26,500,1800], 'tex':'H_{T}'},
    "nBTag"           :{'binning':[2,2,4], 'tex':'N_{b}'},
    "nJetGood"        :{'binning':[7,3,10], 'tex':'N_{jet}'},
    "nrecoJet"        :{'binning':[7,3,10], 'tex':'N_{jet}'},
    "recoLep_dAbsEta"    :{'binning':[30,-2.5,2.5], 'tex':'#Delta|#eta|(tt)'},
    "recoLep_dEta"       :{'binning':[30,-2.5,2.5], 'tex':'#Delta#eta(tt)'},

    "tr_ttbar_dAbsEta"    :{'binning':[30,-2.5,2.5], 'tex':'#Delta|#eta|(tt)'},
    "tr_ttbar_dEta"       :{'binning':[30,-2.5,2.5], 'tex':'#Delta#eta(tt)'},
    "tr_ttbar_pt"         :{'binning':[50,0,1000], 'tex':'p_{T}(tt)'},
    "overflow_counter_v1":{'binning':[7,1,8], 'tex':"Overflow"}

}
