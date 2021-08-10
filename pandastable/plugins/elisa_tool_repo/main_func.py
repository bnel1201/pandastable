#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on January 2019
@author:  Edward Maievskij, Marek Bawiec, Grzegorz Banach
The ELISA tool plugin: module contains high-level functions which combine all of the data flows in the program.
"""

__author__ = "Marek Bawiec, Grzegorz Banach, Edward Maievskij"
__copyright__ = "Copyright 2019, Physiolution Polska"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Grzegorz Banach"
__email__ = "g.banach@physiolution.pl"
__status__ = "Production"

#import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import elisa_tool_repo.calc_met as cm
import elisa_tool_repo.report_pdf as rp
import elisa_tool_repo.approx_met as am
import elisa_tool_repo.repres_sys as rs
import elisa_tool_repo.et_parse_func as epf
import elisa_tool_repo.validation_func as vf

def main_calc(repres_run, examp_run, path_rd, path_st, res_fol, start_range, 
              lic_info, logo_path, errorsDictionary):
    """
    Main calculation function of ET plugin
    """
    """ df for printing only """
    df = pd.DataFrame()
    try:
        (raw_data_df, map_rw_df, data_std_df, data_sam_df, exep_list_df, legend, specific, err) = \
            epf.read_input_data(Fpath_tekan = path_rd, Fpath_config = path_st, data_rep=repres_run)
        """err: no. 10-20"""
        x_std = data_std_df.conc.values
        y_std = data_std_df.absorbance.values  
        print("@x_std: ",x_std)
        print("@y_std: ",y_std)
    except EOFError:
        print("Something goes wrong:")

    #print("1@data_std_df: ", data_std_df)
    df_std_norm, df_sam_norm, err_list, flag = cm.recognition_exp(d_st=data_std_df, \
                                                                  d_sm=data_sam_df, err_list=exep_list_df)
    #print("2@df_std_norm: ", df_std_norm)
    """         0         1               2               3                 4           5           6
    Work in progress, output: (df_local, flag) - DF with data samples, std and other, 
    flag - recognized experiment: STD (standard ELISA), SPC -JS exp., Zero, ZeroSam, ZeroStd
    """                  
    start_time = time.time()
    param_dic, err_list, err = rs.choose_met(data_exp = df_std_norm, ax_order = examp_run, 
                                   st_range = start_range, df_error = err_list)
    """err: no. 50-56"""

    end_time = time.time()
    calc_time = end_time - start_time
    if((err == 0) or (err > 150)):
        """Calculation without errors."""
        (x_theor, y_theor, df_sam, df_sam_bad, df_std) = rs.collect_results(aprox_order = examp_run, param = param_dic, 
                                                              data_std_for_rep = df_std_norm, df_sam_for_rep = df_sam_norm, 
                                                              df_error = err_list, rep_run = repres_run)
        x_sam = df_sam['conc'].tolist()
        y_sam = df_sam['absorbance'].tolist()
        x_std = df_std.conc.values
        y_std = df_std.absorbance.values 
        print("@@Main: x_theor:", x_theor)    
        rs.make_report(x_th = x_theor, y_th = y_theor, param = param_dic, res_folder = res_fol, 
                       r_name = 'Raport_', meas_res = raw_data_df, data_map = map_rw_df, 
                       specification = specific, pdf_leg = legend, licence_notice = lic_info,
                       order_model = examp_run, cal_time = calc_time, sam_mod = df_sam, 
                       sam_bad = df_sam_bad, std_mod = df_std, rep_run=repres_run, st_range = start_range)

        status_info = "completed"
        error_info = "completed"

        df['x_theor'] = pd.Series(x_theor)
        df['y_theor'] = pd.Series(y_theor)
        df['x_std'] = pd.Series(x_std)
        df['y_std'] = pd.Series(y_std)
        df['x_sam'] = pd.Series(x_sam)
        df['y_sam'] = pd.Series(y_sam)
    else:
        """Error in calculation. Send a warrinig."""
        error_info = errorsDictionary[str(err)]        # long error info for figure       
        status_info = "err: check *error.csv"          # short error info for status
        rp.csv_error_create(rep_name='Raport_', p_folder=res_fol , param=param_dic, 
                            order=examp_run, error_text=error_info, 
                            repres_run=repres_run, st_ran = start_range)
        df['x_theor'] = 0
        df['y_theor'] = 0
        if ("data warning" in error_info) or ("method warning" in error_info):
            df['x_std'] = pd.Series(x_std)
            df['y_std'] = pd.Series(y_std)           
        else:
            df['x_std'] = 0
            df['y_std'] = 0
        df['x_sam'] = 0
        df['y_sam'] = 0

    return df, error_info, status_info

def check_function(Fpath_tekan, Fpath_config):
    """
    The function implemented for "parse and check" button.
    Function input:
    Fpath_tekan, Fpath_config - filepaths to raw data from TEKAN measuremnt system and excel_config file respectively
    """
    err = 0
    text_output="Appropriate data set"
    control_1 = epf.tekan_data_check(filepath=Fpath_tekan)
    if control_1 is True:
        text_output="Initial data was not marked. Inappropriate data style or file format." 
    else:
        control_2 = epf.config_data_check_0(filepath=Fpath_config)
        if control_2 is True:
            text_output=text_output="Data presented in xlsx-config file was not marked. Inappropriate xlsx-configurational data style or file format."
        else:
            control_3 = epf.config_data_check_1(filepath=Fpath_config)
            if control_3 is True:
                text_output=text_output="Configurational template for footers and headers is absent or has inappropriate form."

    std_info = pd.DataFrame()
    try:
        #data_rep = 'lin_lin'
        data_std_df, err = epf.parse_input_data(Fpath_tekan, Fpath_config, 'lin_lin')
        if(err != 0):
            text_output = "Inconsistent definition of standards in map file"
            std_info['x_std'] = [0]
            std_info['y_std'] = [0]
        else:
            std_info['x_std'] = data_std_df.conc.values
            std_info['y_std'] = data_std_df.absorbance.values   
            
    except EOFError:
        print("Something goes wrong:")
            
    """         0         1               2               3                 4           5           6
    output: (blk_raw_data_df, map_rw_df, data_std_df, exep_list_df, pdf_leg, specification)
    """   
    """returns text output for the info field of GUI"""        
    return text_output, std_info

def validation_eng(option, noise, points, val_report):
    x_theor = np.linspace(0.0, 1.0, 20*points)
    x_val = np.linspace(0.00001, 1.0, points)

    if option=="4PL curve_fit-val":
       y_val, y_res, par_model = vf.validation_cf4PL(noise_par=noise, x_val40=x_val)
       y_theor = am.logit_4PL_func(X_data=x_theor, param=par_model)
       no_param = 4
    if option=="5PL curve_fit-val":
       y_val, y_res, par_model = vf.validation_cf5PL(noise_par=noise, x_val40=x_val)
       y_theor = am.logit_5PL_func(X_data=x_theor, param=par_model)
       no_param = 5
    if option=="LN curve_fit-val":
       y_val, y_res, par_model = vf.validation_cfLN(noise_par=noise, x_val40=x_val)
       y_theor = am.ln_func(X_data=x_theor, param=par_model)
       no_param = 2
    if option=="LIN curve_fit-val":
       y_val, y_res, par_model = vf.validation_cfLIN(noise_par=noise, x_val40=x_val)
       y_theor = am.linear_func(X_data=x_theor, param=par_model)
       no_param = 2
    if option=="4PL diff_evol-val":
       y_val, y_res, par_model = vf.validation_4PL(noise_par=noise, x_val40=x_val)
       y_theor = am.logit_4PL_func(X_data=x_theor, param=par_model)
       no_param = 4
    if option=="5PL diff_evol-val":
       y_val, y_res, par_model = vf.validation_5PL(noise_par=noise, x_val40=x_val)
       y_theor = am.logit_5PL_func(X_data=x_theor, param=par_model)
       no_param = 5
    if option=="LN diff_evol-val":
       y_val, y_res, par_model = vf.validation_LN(noise_par=noise, x_val40=x_val)
       y_theor = am.ln_func(X_data=x_theor, param=par_model)
       no_param = 2
    if option=="LIN diff_evol-val":
       y_val, y_res, par_model = vf.validation_LIN(noise_par=noise, x_val40=x_val)
       y_theor = am.linear_func(X_data=x_theor, param=par_model)
       no_param = 2

    val_export_csv = pd.DataFrame()
    #data = {'x_std': x_val, 'y_std': y_val, 'x_sam': x_val, 'y_sam': y_res, 'x_theor': x_theor, 'y_theor': y_theor}
    val_export_csv['x_theor'] = pd.Series(x_theor)
    val_export_csv['y_theor'] = pd.Series(y_theor)
    val_export_csv['x_std'] = pd.Series(x_val)
    val_export_csv['y_std'] = pd.Series(y_val)
    val_export_csv['x_sam'] = pd.Series(x_val)
    val_export_csv['y_sam'] = pd.Series(y_res)
    
    error_bound = 0
    param_dic = am.stat_param(y_val, y_res, error_bound, no_param)

    file_name = val_report + "/validation_" + option + str(noise) + "_" + str(points)

    fig = vf.plot_init()
    sub_text = "Validation for " + option + " (noise=" + str(noise) + " , no_point= " + str(points) + ")"
    plt.plot(x_val, y_val, 'o', color='tab:orange', alpha=0.6, label='Exp points')
    plt.plot(x_val, y_res, 'x', color='tab:green', alpha=0.6, linewidth=2, label='Calc points')
    plt.plot(x_theor, y_theor, '-', color='tab:blue', alpha=0.6, linewidth=2, label='Calc func')     
    plt.legend()
    fig.suptitle(sub_text)
    plt.savefig(file_name + '.png', dpi=150)
    plt.close()               

    val_export_csv.to_csv(file_name + '.csv', index=False, sep=",")
    log_file = open(file_name + '.txt', "w")
    log_file.write('Validation parameters: \n  ')
    log_file.write('Noise = %f, Number points = %d \n' %(noise, points))
    log_file.write('\n')
    log_file.write('Model parameters: \n  ')
    if ((option=="5PL curve_fit-val") or (option=="5PL diff_evol-val")):
        log_file.write('Absorbance=D+((A-D)/(1+(Conc/C)^B)^E) \n')
        log_file.write('A=%f, B=%f, C=%f, D=%f, E=%f \n' %(par_model[1], par_model[2], par_model[3], par_model[0], par_model[4]))
        RSS = am.logit_5PL_resid(par_model, y_val, x_val)/len(x_val)
    if ((option=="4PL curve_fit-val") or (option=="4PL diff_evol-val")):
        log_file.write('Absorbance=D+((A-D)/(1+(Conc/C)^B) \n')
        log_file.write('A=%f, B=%f, C=%f, D=%f \n' %(par_model[1], par_model[2], par_model[3], par_model[0]))
        RSS = am.logit_4PL_resid(par_model, y_val, x_val)/len(x_val)
    if ((option=="LN curve_fit-val") or (option=="LN diff_evol-val")):
        log_file.write('Absorbance=A*ln(Conc)+B \n ')
        log_file.write('A=%f, B=%f \n' %(par_model[0], par_model[1]))
        RSS = am.ln_resid(par_model, y_val, x_val)/len(x_val)
    if ((option=="LIN curve_fit-val") or (option=="LIN diff_evol-val")):
        log_file.write('Absorbance=A*Conc+B \n ')
        log_file.write('A=%f, B=%f \n' %(par_model[0], par_model[1]))
        RSS = am.linear_resid(par_model, y_val, x_val)/len(x_val)    
    log_file.write('\n')
    log_file.write('Model diagnostics: \n')
    log_file.write('  The Residual Sum of Squares RSS    = %f; \n' %(RSS))
    log_file.write('  Coefficient of Determination R^2   = %f; \n' %(param_dic['R_squ']))
    log_file.write('  Akaike Information Criterion AIC   = %f; \n' %(param_dic['AIC_crit']))
    log_file.write('  Bayesian Information Criterion BIC = %f; \n' %(param_dic['BIC_crit']))
    log_file.write('  Coefficient of Correlation r       = %f; \n' %(param_dic['R_corre']))
    log_file.close()

    err_info = "completed"

    return val_export_csv, err_info