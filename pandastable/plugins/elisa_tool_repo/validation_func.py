#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on January 2019
@author:  Marek Bawiec, Grzegorz Banach
The ELISA tool plugin: module for validation functions of approximation models.
"""

__author__ = "Marek Bawiec, Grzegorz Banach"
__copyright__ = "Copyright 2019, Physiolution Polska"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Grzegorz Banach"
__email__ = "g.banach@physiolution.pl"
__status__ = "Production"

import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
import elisa_tool_repo.approx_met as am

def plot_init():
    '''
    Prepear all for plots
    #####################
    input: none
    output: handle for figure
    '''
    paperheight = 8.4
    paperwidth = 16.8
    margin = 1.0
    unitName = 'a.u.'
    chartName = "Absorption"
    fig = plt.figure(figsize=(paperwidth - 2*margin, paperheight - 2*margin))
    plt.grid(True)
    plt.xlabel('C [a.u.]', fontsize='x-small')
    plt.ylabel('%s [%s]' % (chartName, unitName), fontsize='x-small')
    return (fig)

def validation_LIN(noise_par, x_val40):    
    param_val=[ 0.55, 1.22]
    config={"A":[0.0,20.0],	"B":[0.0,20.0]}

    y_val = am.linear_func(X_data=x_val40, param=param_val)
    np.random.seed(1729)
    y_noise = noise_par * np.random.normal(size=x_val40.size)
    y_val40 = y_val + y_noise
    
    par_model_val = am.linear_func_par_opt(Y_st=y_val40, X_st=x_val40, st_r=config)
    param_val_new = [par_model_val['A_par1'], par_model_val['B_par1']]
    y_val40res = am.linear_func(X_data=x_val40, param=param_val_new)

    return y_val40, y_val40res, param_val_new

def validation_LN(noise_par, x_val40):    
    param_val=[ 0.55, 1.22]
    config={"A":[0.0,20.0],	"B":[0.0,20.0]}

    y_val = am.ln_func(X_data=x_val40, param=param_val)
    np.random.seed(1729)
    y_noise = noise_par * np.random.normal(size=x_val40.size)
    y_val40 = y_val + y_noise
    
    par_model_val = am.ln_func_par_opt(Y_st=y_val40, X_st=x_val40, st_r=config)
    param_val_new = [par_model_val['B_par1'], par_model_val['A_par1']]
    y_val40res = am.ln_func(X_data=x_val40, param=param_val_new)

    return y_val40, y_val40res, param_val_new

def validation_cfLIN(noise_par, x_val40):    
    param_val=[ 0.55, 1.22]
    config={"A":[0.0,20.0],	"B":[0.0,20.0]}

    y_val = am.linear_func(X_data=x_val40, param=param_val)
    np.random.seed(1729)
    y_noise = noise_par * np.random.normal(size=x_val40.size)
    y_val40 = y_val + y_noise
    
    par_model_val = am.linear_func_curve_fit(Y_st=y_val40, X_st=x_val40, st_r=config)
    param_val_new = [par_model_val['A_par1'], par_model_val['B_par1']]
    y_val40res = am.linear_func(X_data=x_val40, param=param_val_new)

    return y_val40, y_val40res, param_val_new

def validation_cfLN(noise_par, x_val40):    
    param_val=[ 0.55, 1.22]
    config={"A":[0.0,20.0],	"B":[0.0,20.0]}

    y_val = am.ln_func(X_data=x_val40, param=param_val)
    np.random.seed(1729)
    y_noise = noise_par * np.random.normal(size=x_val40.size)
    y_val40 = y_val + y_noise
    
    par_model_val = am.ln_func_curve_fit(Y_st=y_val40, X_st=x_val40, st_r=config)
    param_val_new = [par_model_val['B_par1'], par_model_val['A_par1']]
    y_val40res = am.ln_func(X_data=x_val40, param=param_val_new)

    return y_val40, y_val40res, param_val_new

def validation_4PL(noise_par, x_val40):    
    param_val=[ 1.0, 0.001, 4.5, 0.5]
    config={"A":[0.0,10.0],	"B":[0.0,10.0], "C":[0.0,30.0], "D":[0.0,20.0]}

    y_val = am.logit_4PL_func(X_data=x_val40, param=param_val)
    np.random.seed(1729)
    y_noise = noise_par * np.random.normal(size=x_val40.size)
    y_val40 = y_val + y_noise
    
    par_model_val = am.logit_4PL_par_opt(Y_st=y_val40, X_st=x_val40, st_r=config)
    param_val_new = [par_model_val['D_par1'], par_model_val['A_par1'], par_model_val['B_par1'], par_model_val['C_par1']]
    y_val40res = am.logit_4PL_func(X_data=x_val40, param=param_val_new)

    return y_val40, y_val40res, param_val_new

def validation_cf4PL(noise_par, x_val40):    
    param_val=[ 1.0, 0.001, 4.5, 0.5]
    #config={"A":[0.0,10.0],	"B":[0.0,10.0], "C":[0.0,30.0], "D":[0.0,20.0]}
    config = {"A":[-1.0,5.0],"B":[-1.0,12.0], "C":[0.0,12.0], "D":[0.0,6.0]}
    y_val = am.logit_4PL_func(X_data=x_val40, param=param_val)
    np.random.seed(1729)
    y_noise = noise_par * np.random.normal(size=x_val40.size)
    y_val40 = y_val + y_noise

    par_model_val = am.logit_4PL_curve_fit(Y_st=y_val40, X_st=x_val40, st_r=config)
    param_val_new = [par_model_val['D_par1'], par_model_val['A_par1'], par_model_val['B_par1'], par_model_val['C_par1']]
    y_val40res = am.logit_4PL_func(X_data=x_val40, param=param_val_new)

    return y_val40, y_val40res, param_val_new

def validation_5PL(noise_par, x_val40):    
    param_val=[ 1.0, 0.001, 4.5, 0.5, 2.4]
    config={"A":[0.0,10.0],	"B":[0.0,30.0], "C":[0.0,30.0], "D":[0.0,20.0], "E":[0.0,10.0]}   
    
    y_val = am.logit_5PL_func(X_data=x_val40, param=param_val)
    np.random.seed(1729)
    y_noise = noise_par * np.random.normal(size=x_val40.size)
    y_val40 = y_val + y_noise
    
    par_model_val = am.logit_5PL_par_opt(Y_st=y_val40, X_st=x_val40, st_r=config)
    print("1@par_model_val: ", par_model_val)

    param_val_new = [par_model_val['D_par1'], par_model_val['A_par1'], par_model_val['B_par1'],
                     par_model_val['C_par1'], par_model_val['E_par1']]
    y_val40res = am.logit_5PL_func(X_data=x_val40, param=param_val_new)

    return y_val40, y_val40res, param_val_new

def validation_cf5PL(noise_par, x_val40):    
    param_val=[ 1.0, 0.001, 4.5, 0.5, 2.4]
    config={"A":[-1.0,5.0],	"B":[-1.0,12.0], "C":[0.0,12.0], "D":[0.0,6.0], "E":[0.0,8.0]}
     
    y_val = am.logit_5PL_func(X_data=x_val40, param=param_val)
    np.random.seed(1729)
    y_noise = noise_par * np.random.normal(size=x_val40.size)
    y_val40 = y_val + y_noise
    
    par_model_val = am.logit_5PL_curve_fit(Y_st=y_val40, X_st=x_val40, st_r=config)
    print("2@par_model_val: ", par_model_val)
    param_val_new = [par_model_val['D_par1'], par_model_val['A_par1'], par_model_val['B_par1'],
                     par_model_val['C_par1'], par_model_val['E_par1']]
    y_val40res = am.logit_5PL_func(X_data=x_val40, param=param_val_new)

    return y_val40, y_val40res, param_val_new
