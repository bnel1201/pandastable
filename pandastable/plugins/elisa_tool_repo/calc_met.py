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
import copy
import elisa_tool_repo.approx_met as am

def max_concentration(res_sam_mat, std_mat):
    """
    The function implemented to return the maximal known concentration from the whole data set for appropriate plotting.
    """
    std=std_mat
    max_std= max(std)   
    if(not res_sam_mat):
        max_conc = max_std
    else:
        max_res_sam=max(res_sam_mat)
        max_conc = 0.0
        if max_res_sam > max_std:
            max_conc = max_res_sam
        else:
            max_conc = max_std
    """returns the value of maximal titer concentration"""    
    return max_conc

def min_concentration(res_sam_mat, std_mat):
    """
    The function implemented to return the minimal known concentration from the whole data set for appropriate plotting.
    """
    std = std_mat
    min_std = min(std)      
    if(not res_sam_mat):
        min_conc = min_std
    else:
        min_res_sam = min(res_sam_mat)
        min_conc = 0.0
        if min_res_sam < min_std:
            min_conc = min_res_sam
        else:
            min_conc = min_std
    """
    returns the value of minimal titer concentration
    """    
    return min_conc 

def theor_X(res_sam_mat, std_mat):
    """
    The function implemented for theoretical curve X values generating.
    """
    maxconc = max_concentration(res_sam_mat=res_sam_mat, std_mat=std_mat)
    minconc = min_concentration(res_sam_mat=res_sam_mat, std_mat=std_mat)
    delta = (maxconc - minconc)/500
    X_t = np.arange(minconc, maxconc, delta)
    #returns list of titer concentration valuesfor further calculations of theoretical curve
    return X_t
    
def data_st_to_print(imp_data_rw, imp_data_map, data_std_rw, rep):
    """
    The function used to generate an ordered DataFrame with initial measuremnt results.
    """
    df_local = pd.DataFrame(columns=['std_name', 'samples_nb', 'absorbance', 'abs_std', 
                                     'conc', 'abs_std_var', 'Errors'])
    df_losam = pd.DataFrame(columns=['sam_name', 'samples_nb', 'absorbance', 'abs_sam', 
                                     'conc', 'abs_std_var', 'conc_std_up', 'conc_std_dow', 
                                     'Errors'])
    df_local.set_index('std_name', inplace=True)  
    df_losam.set_index('sam_name', inplace=True)  
    
    if((rep == 'ln_ln') or (rep == 'ln_lin')):
        #imp_data = imp_data_rw.apply(np.log)
        imp_data = np.log(imp_data_rw.astype(np.float64))
    else: 
        imp_data = imp_data_rw.copy()
    if((rep == 'ln_ln') or (rep == 'lin_ln')):
        data_standards = data_std_rw.copy()
        data_standards['values_conc'] = np.log(data_std_rw['values_conc'])
    else: 
        data_standards = data_std_rw.copy()

    for i in range(0, len(imp_data_map.index)):
        for j in range(0, len(imp_data_map.columns)):
            is_string = imp_data_map.values[i,j]
            is_concen = imp_data.values[i,j]
            if(("std" in is_string) and (not isinstance(is_concen, str))):
                if(df_local.index.isin([is_string]).any()):   
                    """If YES then add to this position"""
                    df_local.abs_std[is_string].append(is_concen)
                    df_local.loc[is_string]['samples_nb'] +=  1
                else:
                    """If NO then append to DataFrame new record"""
                    tmp_df = pd.DataFrame([[[is_concen], 1]], columns=['abs_std', 'samples_nb'], index=[is_string])
                    df_local = df_local.append(tmp_df, ignore_index=False)
            if(("sam" in is_string) and (not isinstance(is_concen, str))):
                if(df_losam.index.isin([is_string]).any()):   
                    df_losam.abs_sam[is_string].append(is_concen)
                    df_losam.loc[is_string]['samples_nb'] +=  1
                else:
                    tmp_df = pd.DataFrame([[[is_concen], 1]], columns=['abs_sam', 'samples_nb'], index=[is_string])
                    df_losam = df_losam.append(tmp_df, ignore_index=False)
            if(("zeroall" in is_string) and (not isinstance(is_concen, str))):
                if(df_losam.index.isin([is_string]).any()):   
                    df_losam.abs_sam[is_string].append(is_concen)
                    df_losam.loc[is_string]['samples_nb'] +=  1
                else:
                    tmp_df = pd.DataFrame([[[is_concen], 1]], columns=['abs_sam', 'samples_nb'], index=[is_string])
                    df_losam = df_losam.append(tmp_df, ignore_index=False)
            if(("zerosam" in is_string) and (not isinstance(is_concen, str))):
                if(df_losam.index.isin([is_string]).any()):   
                    df_losam.abs_sam[is_string].append(is_concen)
                    df_losam.loc[is_string]['samples_nb'] +=  1
                else:
                    tmp_df = pd.DataFrame([[[is_concen], 1]], columns=['abs_sam', 'samples_nb'], index=[is_string])
                    df_losam = df_losam.append(tmp_df, ignore_index=False)
            if(("zerostd" in is_string) and (not isinstance(is_concen, str))):
                if(df_losam.index.isin([is_string]).any()):   
                    df_losam.abs_sam[is_string].append(is_concen)
                    df_losam.loc[is_string]['samples_nb'] +=  1
                else:
                    tmp_df = pd.DataFrame([[[is_concen], 1]], columns=['abs_sam', 'samples_nb'], index=[is_string])
                    df_losam = df_losam.append(tmp_df, ignore_index=False)

    for index, row in df_local.iterrows():
        row['absorbance'] = sum(row['abs_std'])/row['samples_nb']
        row["abs_std_var"] = np.std(row["abs_std"])
        row['conc'] = data_standards.values_conc[index]

    for index, row in df_losam.iterrows():
        row['absorbance'] = sum(row['abs_sam'])/row['samples_nb']
        row["abs_std_var"] = np.std(row["abs_sam"])
    
    df_local.reset_index(inplace=True)
    df_local.rename(columns={'index':'std_name'}, inplace=True)
    df_local.set_index(['std_name'], inplace=True)
    df_local.sort_values(by=['std_name'], inplace=True)
    df_losam.reset_index(inplace=True)
    df_losam.rename(columns={'index':'sam_name'}, inplace=True)
    df_losam.set_index(['sam_name'], inplace=True)
    df_losam.sort_values(by=['sam_name'], inplace=True)
    
    """returns DataFrame with extended table of data about calibration standards: (std_name,concentration, abs_ave) """
    return df_local, df_losam

def data_std_format(imp_data, imp_data_map, data_standards):
    """
    The function implemented to extract, clean and order calibration standards for further ln-model fitting.
    """
    g1 = imp_data_map.stack()
    g2 = set(g1)
    for g in g2:
        vars()[g] = []
        
    imp_columns = list(imp_data.columns.values)
    imp_index = list(imp_data.index.values)
    
    for c_name in imp_columns:
        for r_name in imp_index:
            vars()[imp_data_map.loc[r_name][c_name]].append(imp_data.loc[r_name][c_name])
            
    X_st = []
    Y_st = []
    
    for g in g2:
        vars()[g]=sum(vars()[g]) / float(len(vars()[g]))
        if ('std' in g):
            X_st.append(data_standards.loc[g]['values_conc'])
            Y_st.append(vars()[g])
            continue
        else:
            continue
    """ 
    Remove zero value from concentration - unphysical and denger for logharitm
    """        
    X_st1=copy.deepcopy(X_st)
    Y_st1=copy.deepcopy(Y_st)
    N=0
    lenX=len(X_st1)
    N_of_del=0
    while N< lenX:
        if X_st1[N-N_of_del]==0:
            del(X_st1[N-N_of_del])
            del(Y_st1[N-N_of_del])
            N_of_del=N_of_del+1
            N=N+1
            continue
        else:
            N=N+1
            continue
    """returns the tuple of two arrays"""    
    return(X_st1, Y_st1)
    
def samples_conc(df_std, df_local, df_error, params, ordered):

    """Find max value of Absorption and deviation for Standard"""
    Max_ind_of_std = df_std['absorbance'].astype('float64').idxmax(skipna=True)     
    Max_val_of_std = df_std.loc[Max_ind_of_std]['absorbance']
    Max_val_of_dev = df_std.loc[Max_ind_of_std]['abs_std_var']
    Abs_max =  Max_val_of_std + Max_val_of_dev
    """Find min value of Absorption and deviation for Standard"""
    Min_ind_of_std = df_std['absorbance'].astype('float64').idxmin(skipna=True)
    Min_val_of_std = df_std.loc[Min_ind_of_std]['absorbance']
    Min_val_of_dev = df_std.loc[Min_ind_of_std]['abs_std_var']   
    Abs_min = Min_val_of_std - Min_val_of_dev

    for index, row in df_local.iterrows():
        if ('sam' in index):
            Abs_up = row["absorbance"] + row["abs_std_var"] 
            Abs_down = row["absorbance"] - row["abs_std_var"]
            if ((ordered=="LIN curve_fit") or (ordered=="LIN diff_evol")):
                if(( Abs_min <= Abs_up) and (Abs_down <= Abs_max)):
                    ave_concentr = am.linear_concentration(Y_data=row["absorbance"], param=params)
                    row["conc"] = ave_concentr
                    row["conc_std_up"] = am.linear_concentration(Y_data=Abs_up, param=params) - ave_concentr
                    row["conc_std_dow"] = ave_concentr - am.linear_concentration(Y_data=Abs_down, param=params)
                    row["Errors"] = 0
                else:
                    row["conc"] = 0.0
                    row["Errors"] = 1
            if ((ordered=="LN curve_fit") or (ordered=="LN diff_evol")):
                if((0.0 < Abs_up) and (Abs_down <= Abs_max)):
                    ave_concentr = am.ln_func_concentration(Y_data=row["absorbance"], param=params)
                    row["conc"] = ave_concentr
                    row["conc_std_up"] = am.ln_func_concentration(Y_data=Abs_up, param=params) - ave_concentr
                    row["conc_std_dow"] = ave_concentr - am.ln_func_concentration(Y_data=Abs_down, param=params)
                    row["Errors"] = 0
                else:
                    row["conc"] = 0.0
                    row["Errors"] = 1
            if ((ordered=="4PL diff_evol") or (ordered=="4PL curve_fit")): 
                if((params['A_par1'] <= Abs_up) and (Abs_down <= params['D_par1'])):
                    """ 1) bottom limit for 4PL (Y_abs+Y_std >= A_par)
                        2) upper limit for 4PL (Y_abs-Y_std <= D_par)
                    """
                    ave_concentr = am.logit_4PL_concentration(Y_data=row["absorbance"], param=params)
                    row["conc"] = ave_concentr
                    row["conc_std_up"] = am.logit_4PL_concentration(Y_data=Abs_up, param=params) - ave_concentr
                    row["conc_std_dow"] = ave_concentr - am.logit_4PL_concentration(Y_data=Abs_down, param=params)
                    row["Errors"] = 0
                else:
                    row["conc"] = 0.0
                    row["Errors"] = 1
            if ((ordered=="5PL curve_fit") or (ordered=="5PL diff_evol")):            
                if((params['A_par1'] <= Abs_up) and (Abs_down <= params['D_par1'])):
                    """ 1) bottom limit for 5PL (Y_abs+Y_std >= A_par)
                        2) upper limit for 5PL (Y_abs-Y_std <= D_par)
                    """
                    ave_concentr = am.logit_5PL_concentration(Y_data=row["absorbance"], param=params)
                    row["conc"] = ave_concentr
                    row["conc_std_up"] = am.logit_5PL_concentration(Y_data=Abs_up, param=params) - ave_concentr
                    row["conc_std_dow"] = ave_concentr - am.logit_5PL_concentration(Y_data=Abs_down, param=params)
                    row["Errors"] = 0
                else:
                    row["conc"] = 0.0
                    row["Errors"] = 1
               
    """ returns sample names, titer concentration, lower and upper boundaries of concentration standard 
        deviations and simmetrical value of absorbance standard deviation.
        returns:
       Y_s_names           - sample names, = std_names
       X_s_concentration   - titer concentration, 
       Y_s_good            - absorpcja probki zgodna z modelem aproksymujacym (np. Y_s_abs-Y_s_std => A_par and Y_s_abs+Y_s_std>D_par)
       Y_s_bad             - absorpcja probki wypadajaca poza model aproksymujacy (np. Y_s_abs-Y_s_std < A_par) string!
       X_s_conc_std_bottom - lower  boundaries of concentration standard deviations 
       X_s_conc_std_upper  - upper boundaries of concentration standard deviations  
       Y_s_abs_std         - simmetrical value of absorbance standard deviation
       X_std_abs           - concentrations of standards 
       Y_std_abs           - ave. absorption of standards 
       Y_std_std           - std of absorption of standards.
    """
    for index, row in df_local.iterrows():
        if (('sam' in index) and (row['Errors']==1)): 
            df_error = df_error.append({'blq_name': 'err1', 'sample_name': index}, ignore_index=True)
            df_local.drop(index, inplace=True)
        if ('zero' in index): 
            df_error = df_error.append({'blq_name': 'reduce', 'sample_name': index}, ignore_index=True)
            df_local.drop(index, inplace=True)

    return df_local, df_error        

        
def recognition_exp(d_st, d_sm, err_list):
    
    def func_zero(Y, param):
        local_df = Y
        for index, row in Y.iterrows():
            local_df['absorbance'] = Y.apply(lambda a: a - param)
        return local_df
    
    """Refactoring parsing_sam_and_concenration:
    DF: imp_data, imp_data_map = AHx12
    DF: d_st, d_sm = ['name', 'samples_nb', 'absorbance', 'Y_abs_sam', 'conc', 'Y_abs_std_var', 'Errors']
    """
                
    flag = 'STD'
    df_lostd = d_st
    df_losam = d_sm

    if (('nc' in d_sm.index) and ('pc' in d_sm.index)):  
        flag = 'SPC'
    if ('zeroall' in d_sm.index): 
        zero_new = d_sm[d_sm.index == 'zeroall', 'absorbance'].values
        df_losam = func_zero(d_sm, zero_new)
        df_lostd = func_zero(d_st, zero_new)
        flag = 'zeroall'
    if ('zerosam' in d_sm.index): 
        zero_new = d_sm[d_sm.index == 'zerosam', 'absorbance'].values
        df_losam = func_zero(d_sm, zero_new)
        flag = 'zerosam'
    if ('zerostd' in d_sm.index): 
        zero_new =  d_sm[d_sm.index == 'zerostd', 'absorbance'].values
        df_lostd = func_zero(d_st, zero_new)
        flag = 'zerostd'

    for index, row in d_sm.iterrows():
        if(row["absorbance"] < 0):
            """Condition1:  absorbance must always be positive for sample"""
            warning = 'After' + flag + ' Abs. less than 0'
            err_list = err_list.append({'blq_name': flag, 'sample_name': index}, ignore_index=True)
            d_sm.drop(index)
    for index, row in d_st.iterrows():
        if(row["absorbance"] < 0):
            """Condition1:  absorbance must always be positive for standard"""
            err_list = err_list.append({'blq_name': flag, 'sample_name': index}, ignore_index=True)
            d_st.drop(index)

               
    """returns:
       Y_s_names           - sample names, 
       X_s_concentration   - titer concentration, 
       Y_s_good            - absorpcja probki zgodna z modelem aproksymujacym (np. Y_s_abs-Y_s_std => A_par and Y_s_abs+Y_s_std>D_par)
       Y_s_bad             - absorpcja probki wypadajaca poza model aproksymujacy (np. Y_s_abs-Y_s_std < A_par) string!
       X_s_conc_std_bottom - lower  boundaries of concentration standard deviations 
       X_s_conc_std_upper  - upper boundaries of concentration standard deviations  
       Y_s_abs_std         - simmetrical value of absorbance standard deviation
       X_std_abs           - concentrations of standards 
       Y_std_abs           - ave. absorption of standards 
       Y_std_std           - std of absorption of standards.

    for index, row in df_local.iterrows():
        if (('sam' in index) and (row['Errors']==0)):
            Y_s_names.append(index)
            X_s_concentration.append(row["X_concentration"])
            Y_s_good.append(row["Y_ave_abs"])
            Y_s_abs_std.append(row["Y_abs_std"])
            X_s_conc_std_upper.append(row["X_s_conc_std_upper"])
            X_s_conc_std_bottom.append(row["X_s_conc_std_bottom"])
        if (('sam' in index) and (row['Errors']==1)): # develop for more error levels
            Y_s_bad.append(index)
        if (('std' in index) and (row['Errors']==100)):
            Y_std_std.append(row["Y_abs_std"])
            Y_std_abs.append(row["Y_ave_abs"])
            X_std_abs.append(row["X_concentration"])
    """
          
    return df_lostd, df_losam, err_list, flag
