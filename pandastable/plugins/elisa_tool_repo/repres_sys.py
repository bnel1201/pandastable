#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on January 2019
@author:  Edward Maievskij, Marek Bawiec, Grzegorz Banach
The ELISA tool plugin: module contains basic calculating functions.
"""

__author__ = "Marek Bawiec, Grzegorz Banach, Edward Maievskij"
__copyright__ = "Copyright 2019, Physiolution Polska"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Grzegorz Banach"
__email__ = "g.banach@physiolution.pl"
__status__ = "Production"

import numpy as np
import pandas as pd
import elisa_tool_repo.plot_func as pf
import elisa_tool_repo.approx_met as am
import elisa_tool_repo.calc_met as cm
import elisa_tool_repo.report_pdf as pdf


def choose_met(data_exp, ax_order, st_range, df_error):
    g_i = data_exp.absorbance.values  
    x_i = data_exp.conc.values
    empty_df = pd.DataFrame()
    err = 0
    if((ax_order == "LIN curve_fit") or (ax_order == "LIN diff_evol")):
        if(len(x_i) < 2):
            param_local = empty_df
            err = 51 # data error, not enough data for 2 parameter calculation
        else: 
            if(ax_order == "LIN diff_evol"):
                param_local = am.linear_func_par_opt(Y_st=g_i, X_st=x_i, st_r=st_range)        
            else:
                param_local = am.linear_func_curve_fit(Y_st=g_i, X_st=x_i, st_r=st_range)

    if((ax_order == "LN curve_fit") or (ax_order == "LN diff_evol")):
        for index, row in data_exp.iterrows():
            if (row['conc']<=0): 
                df_error = df_error.append({'blq_name': 'conc<=0  for LN', 'sample_name': index}, ignore_index=True)
                data_exp.drop(index, inplace=True)
                err = 150  #data warning, unacceptable value for conc in LN method
        """Assain again the same or shorter arrays """
        g_i = data_exp.absorbance.values  
        x_i = data_exp.conc.values
        if(len(x_i) < 2):
            param_local = empty_df
            err = 52 # data error, not enough data for 2 parameter calculation
        else: 
            if(ax_order == "LN diff_evol"):
                param_local = am.ln_func_par_opt(Y_st=g_i, X_st=x_i, st_r=st_range)
                print("@@choose_met: g_i:", g_i)    
                print("@@choose_met: x_i:", x_i)    
            else:
                param_local = am.ln_func_curve_fit(Y_st=g_i, X_st=x_i, st_r=st_range)

    if((ax_order == "4PL curve_fit") or (ax_order == "4PL diff_evol")):
        for index, row in data_exp.iterrows():
            if (row['absorbance']<0): 
                df_error = df_error.append({'blq_name': 'absorbance<0  for 4PL', 'sample_name': index}, ignore_index=True)
                data_exp.drop(index, inplace=True)
                err = 151  #data warning, unacceptable value for conc in 4PL method
        """Assain again the same or shorter arrays """
        g_i = data_exp.absorbance.values  
        x_i = data_exp.conc.values
        if(len(x_i) < 4):
            param_local = empty_df
            err = 54 # data error, not enough data for 4 parameter calculation
        else: 
            if(ax_order == "4PL diff_evol"):
                param_local = am.logit_4PL_par_opt(Y_st=g_i, X_st=x_i, st_r=st_range)
            else:
                param_local = am.logit_4PL_curve_fit(Y_st=g_i, X_st=x_i, st_r=st_range)

    if((ax_order == "5PL curve_fit") or (ax_order == "5PL diff_evol")):
        for index, row in data_exp.iterrows():
            if (row['absorbance']<0): 
                df_error = df_error.append({'blq_name': 'absorbance<0  for 5PL', 'sample_name': index}, ignore_index=True)
                data_exp.drop(index, inplace=True)
                err = 152  #data warning, unacceptable value for conc in 5PL method
        """Assain again the same or shorter arrays """
        if(len(x_i) < 5):
            param_local = empty_df
            err = 55 # data error, not enough data for 5 parameter calculation
        else: 
            if(ax_order == "5PL diff_evol"):
                param_local = am.logit_5PL_par_opt(Y_st=g_i, X_st=x_i, st_r=st_range)
            else:
                param_local = am.logit_5PL_curve_fit(Y_st=g_i, X_st=x_i, st_r=st_range)

    if(param_local['Error'] != 0):
        # check parameter acording curve bounds: err 56 parameter not found, equal bound value
        err = 56
    if(param_local['RSS'] > 0.3):
        # check parameter acording to fitting: err 57 RSS to big
        err = 57
    if(param_local['R_squ'] < 0.55):
        # check parameter acording to fitting: err 57 R^2 to small
        err = 58
        
    return param_local, df_error, err

def abosrp_repres(meas_aborp, data_standards_for_rep, rep_run):
    x_std = data_standards_for_rep.conc.values
    y_std = data_standards_for_rep.absorbance.values  

    if(rep_run == 'lin_lin'):
        meas_aborp_rec = meas_aborp
        data_std_rep = data_standards_for_rep
    if(rep_run == 'lin_ln'):
        meas_aborp_rec = meas_aborp
        data_std_rep = data_standards_for_rep
        data_std_rep['conc'] = np.log(x_std)       
    if(rep_run == 'ln_lin'):
        meas_aborp_rec = meas_aborp.apply(np.log) 
        data_std_rep = data_standards_for_rep
        data_std_rep['absorbance'] = np.log(y_std)
    if(rep_run == 'ln_ln'):
        meas_aborp_rec = meas_aborp.apply(np.log) 
        data_std_rep = data_standards_for_rep.apply(np.log)
    
    return meas_aborp_rec, data_std_rep

def restore_lin_res(x_theor, y_theor, result_model, df_std, rep_run):
    if(rep_run == 'lin_lin'):
        x_theor_lin = x_theor.copy()
        y_theor_lin = y_theor.copy()
        result_model_sam = result_model      
        df_std_l = df_std.copy()
    if(rep_run == 'lin_ln'):
        x_theor_lin = np.exp(x_theor)
        y_theor_lin = y_theor.copy()
        result_model_sam = result_model.copy()
        result_model_sam['conc'] = np.exp(result_model['conc'].astype(np.float64))
        df_std_l = df_std.copy()
        df_std_l['conc'] = np.exp(df_std['conc'].astype(np.float64))
    if(rep_run == 'ln_lin'):
        x_theor_lin = x_theor.copy()
        y_theor_lin = np.exp(y_theor)      
        result_model_sam = result_model.copy()
        result_model_sam['absorbance'] = np.exp(result_model['absorbance'].astype(np.float64))
        df_std_l = df_std.copy()
        df_std_l['absorbance'] = np.exp(df_std['absorbance'].astype(np.float64))
    if(rep_run == 'ln_ln'):
        x_theor_lin = np.exp(x_theor)
        y_theor_lin = np.exp(y_theor)      
        result_model_sam = result_model.copy()
        result_model_sam['conc'] = np.exp(result_model['conc'].astype(np.float64))
        result_model_sam['absorbance'] = np.exp(result_model['absorbance'].astype(np.float64))
        df_std_l = df_std.copy()
        df_std_l['conc'] = np.exp(df_std['conc'].astype(np.float64))
        df_std_l['absorbance'] = np.exp(df_std['absorbance'].astype(np.float64))
   
    return x_theor_lin, y_theor_lin, result_model_sam, df_std_l


def collect_results( aprox_order, param, data_std_for_rep, df_sam_for_rep, df_error, rep_run):
    
    df_sam, error_list = cm.samples_conc(df_std=data_std_for_rep, df_local=df_sam_for_rep, 
                                         df_error=df_error, params=param, 
                                         ordered=aprox_order)
    theor_model_X_axis = cm.theor_X(res_sam_mat=df_sam['conc'].tolist(), 
                                    std_mat=data_std_for_rep['conc'].tolist())
    
    print("@@collect_results1: res_sam_mat:", df_sam['conc'].tolist())    
    print("@@collect_results2: data_std_for_rep:", data_std_for_rep['conc'].tolist())    

    print("@@collect_results3: theor_model_X_axis:", theor_model_X_axis)
    
    if ((aprox_order=="LIN diff_evol") or (aprox_order=="LIN curve_fit")):
        para_val = [param['A_par1'], param['B_par1']]
        theor_model_Y_axis=am.linear_func(X_data=theor_model_X_axis, param = para_val)
         
    if ((aprox_order=="LN diff_evol") or (aprox_order=="LN curve_fit")):
        para_val = [param['B_par1'], param['A_par1']]
        theor_model_Y_axis=am.ln_func(X_data=theor_model_X_axis, param = para_val)
         
    if ((aprox_order=="4PL diff_evol") or (aprox_order=="4PL curve_fit")):
        para_val = [param['D_par1'], param['A_par1'], param['B_par1'], param['C_par1']]
        theor_model_Y_axis=am.logit_4PL_func(X_data=theor_model_X_axis, param = para_val)
         
    if ((aprox_order=="5PL diff_evol") or (aprox_order=="5PL curve_fit")):
        para_val = [param['D_par1'], param['A_par1'], param['B_par1'], param['C_par1'], param['E_par1']]
        theor_model_Y_axis=am.logit_5PL_func(X_data=theor_model_X_axis, param = para_val)
    
    (x_theor_lin, y_theor_lin, df_sam_lin, df_std_lin) = restore_lin_res(theor_model_X_axis, theor_model_Y_axis, 
                                                                         df_sam, data_std_for_rep, rep_run)
    return x_theor_lin, y_theor_lin, df_sam_lin, error_list, df_std_lin


def make_report(x_th, y_th, param, res_folder, r_name, meas_res, data_map, 
                specification, pdf_leg, licence_notice, order_model, cal_time, 
                sam_mod, sam_bad, std_mod, rep_run, st_range):
    """
    The function used to generate pdf and csv reports for 5PL model.
    Function inputs Fpath_tekan and Fpath_config should contain filepaths to TEKAN raw data xlsx-file and standard xlsx config file respectively.
    Function input res_folder is used to provide information about destination folder for report generation opertions.
    Function input r_name is used to provide suffix for genrated reports (i.e. first part of the reports name)
    """
 
    X_std_abs = std_mod['conc'].tolist()
    Y_std_abs = std_mod['absorbance'].tolist()
    Y_std_std = std_mod['abs_std_var'].tolist()
    
    X_s_con = sam_mod['conc'].tolist()
    Y_s_abs = sam_mod['absorbance'].tolist()
    X_s_bot = sam_mod['conc_std_dow'].tolist()
    X_s_up  = sam_mod['conc_std_up'].tolist()
    Y_s_var = sam_mod['abs_std_var'].tolist()
    
    if(rep_run == 'lin_lin'):    
        pl_lin = pf.fig_lin_er(X_fun = x_th, Y_fun = y_th, 
                               X_std = X_std_abs, Y_std = Y_std_abs, Y_std_err = Y_std_std,
                               X_sam = X_s_con, Y_sam = Y_s_abs,                                                                  
                               X_sb_err = X_s_bot, X_su_err = X_s_up, Y_s_err = Y_s_var, 
                               title_s = 'Results for '+order_model+' in lin presentation', repres=rep_run)
    else:
        # tutaj do zmiany: fig_lin_pl-> fig_lin_er, ale trzeba wyliczyc
        pl_lin = pf.fig_lin_pl(X_fun = x_th, Y_fun = y_th, X_std = X_std_abs, Y_std = Y_std_abs, 
                               X_sam = X_s_con, Y_sam = Y_s_abs,                                                                  
                               title_s='Results for '+order_model+' in lin presentation', repres='lin_lin')
    print("@@pl_lin: ", pl_lin)
    if(rep_run == 'lin_ln'):
        x_th_l = np.log(x_th)
        y_th_l = y_th
        X_std_abs_l = np.log(X_std_abs)
        Y_std_abs_l = Y_std_abs
        X_s_con_l = np.log(X_s_con)
        Y_s_abs_l = Y_s_abs

        pl_lnx = pf.fig_lin_er(X_fun = x_th_l, Y_fun = y_th_l, 
                               X_std = X_std_abs_l, Y_std = Y_std_abs_l, Y_std_err = Y_std_std,
                               X_sam = X_s_con_l, Y_sam = Y_s_abs_l,                                                                  
                               X_sb_err = X_s_bot, X_su_err = X_s_up, Y_s_err = Y_s_var, 
                               title_s='Results for '+order_model+' in lnx presentation', repres=rep_run)
    else:
        pl_lnx = pf.fig_lnx_pl(X_fun = x_th, Y_fun = y_th, X_std = X_std_abs, Y_std = Y_std_abs, 
                               X_sam = X_s_con, Y_sam = Y_s_abs,                                                                  
                               title_s='Results for '+order_model+' in lnx presentation', repres='lin_ln')
    print("@@pl_lnx: ", pl_lnx)

    if(rep_run == 'ln_lin'):
        # zlogarytmuj ponowie Y_i, odchylenie powinny być we włsciwych jednostkach, ale rysujemy lini-lin
        x_th_l = x_th
        y_th_l = np.log(y_th)
        X_std_abs_l = X_std_abs
        Y_std_abs_l = np.log(Y_std_abs)
        X_s_con_l = X_s_con
        Y_s_abs_l = np.log(Y_s_abs)

        # czy wystarczy zamina na fig_lny_er->fig_lin_er?
        pl_lny = pf.fig_lin_er(X_fun = x_th_l, Y_fun = y_th_l, 
                               X_std = X_std_abs_l, Y_std = Y_std_abs_l, Y_std_err = Y_std_std,
                               X_sam = X_s_con_l, Y_sam = Y_s_abs_l,                                                                  
                               X_sb_err = X_s_bot, X_su_err = X_s_up, Y_s_err = Y_s_var, 
                               title_s='Results for '+order_model+' in lny presentation', repres=rep_run)
    else:
        pl_lny = pf.fig_lny_pl(X_fun = x_th, Y_fun = y_th, X_std = X_std_abs, Y_std = Y_std_abs, 
                               X_sam = X_s_con, Y_sam = Y_s_abs,                                                                 
                               title_s='Results for '+order_model+' in lny presentation', repres='ln_lin')
    print("@@pl_lny: ", pl_lny)
        
    if(rep_run == 'ln_ln'):      
        x_th_l = np.log(x_th)
        y_th_l = np.log(y_th)
        X_std_abs_l = np.log(X_std_abs)
        Y_std_abs_l = np.log(Y_std_abs)
        X_s_con_l = np.log(X_s_con)
        Y_s_abs_l = np.log(Y_s_abs)

        pl_lnln = pf.fig_lin_er(X_fun = x_th_l, Y_fun = y_th_l, 
                                 X_std = X_std_abs_l, Y_std = Y_std_abs_l, Y_std_err = Y_std_std,
                                 X_sam = X_s_con_l, Y_sam = Y_s_abs_l,                                                                  
                                 X_sb_err = X_s_bot, X_su_err = X_s_up, Y_s_err = Y_s_var, 
                                 title_s='Results for '+order_model+' in lnln presentation', repres=rep_run)
    else:
        pl_lnln = pf.fig_lnln_pl(X_fun = x_th, Y_fun = y_th, X_std=X_std_abs, Y_std = Y_std_abs, 
                                 X_sam = X_s_con, Y_sam = Y_s_abs,                                                                 
                                 title_s='Results for '+order_model+' in lnln presentation', repres='ln_ln')
    print("@@pl_lnln: ", pl_lnln)

    pdf.pdf_report_create(rep_name = r_name, p_folder = res_folder, D_samples = sam_mod, Y_s_bad = sam_bad, param = param,
                          i_data = meas_res, i_data_map = data_map, d_st = std_mod, legend = pdf_leg, 
                          plot_lin = pl_lin, plot_lnx = pl_lnx, plot_lny = pl_lny, plot_lnln = pl_lnln, 
                          spec = specification, notice = licence_notice, order = order_model,
                          cal_time = cal_time, repres_run = rep_run)
        
    pdf.csv_report_create(rep_name=r_name, p_folder=res_folder, D_sam=sam_mod, Y_s_bad = sam_bad, param=param, 
                          i_data=meas_res, i_data_map=data_map, d_st=std_mod, order=order_model, 
                          cal_time=cal_time, repres_run=rep_run, st_ran = st_range)
   
    return 