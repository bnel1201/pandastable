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
from scipy.optimize import differential_evolution
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
#import RegscorePy as rsp
from RegscorePy import *
#import sys

def stat_param(Y_st, y_theor, error_bound, no_param):
    """Support statistical function"""
    R_squ = r2_score(y_true = Y_st, y_pred = y_theor)
    if(R_squ < 0.6):  error_bound = 1
    akaike_crit = aic.aic(y = Y_st, y_pred = y_theor, p = no_param)
    bayes_crit = bic.bic(y = Y_st, y_pred = y_theor, p = no_param)
#    akaike_crit = rsp.aic(y = Y_st, y_pred = y_theor, p = 4)
#    bayes_crit = rsp.bic(y = Y_st, y_pred = y_theor, p = 4)
    r, prob = pearsonr(Y_st, y_theor)
    #par = [('R_squ', R_squ), ('AIC_crit', akaike_crit), ('BIC_crit', bayes_crit), ('R_corre', r), ('Error', error_bound)]
    par = {'R_squ': R_squ, 'AIC_crit': akaike_crit, 'BIC_crit': bayes_crit, 
           'R_corre': r, 'Error': error_bound}
    return par

"""
Functions for linear approximation:
1. definition of function
2. fit method: curve_fit
3. fit method: differential_evolution
4. calculating the deviation of the fitted function
5. calculation based on adjusted concentration function
"""

def linear_resid(para, y, x):
    """Deviations of data from linear curve"""
    err = y - linear_func(x, para)
    return sum(err**2)

def check_linear_bounds(par, st_r, RSS):
    """Deviations of data from logit curve"""
    if(par[1] == st_r['A'][0] or par[1] == st_r['A'][1] or par[0] == st_r['B'][0] or 
       par[0] == st_r['B'][1] or RSS > 0.3):
        """ at least one of the parameters is equal to the range limit, error!"""
        err = 1
    else:
        """ the parameters in proper range, ok"""
        err = 0

    return err

def linear_func_curve_fit(Y_st, X_st, st_r):
    """
    Optimization on the base of curvr_fit function
    Returns list of tuples with optimal 4PL-model parameters and R_squ
    """
    def linear_call(X_data, A, B):       
        return B*np.array(X_data) + A
    
    par, pcov = curve_fit(linear_call, X_st, Y_st, 
                          bounds=([st_r['A'][0], st_r['B'][0]],[st_r['A'][1], st_r['B'][1]]))

    RSS = linear_resid(par, Y_st, X_st)/len(X_st)
    error_bound = check_linear_bounds(par, st_r, RSS) 
    parameters = {'A_par1': par[0], 'B_par1': par[1], 'RSS': RSS}
    y_theor = linear_func(X_st, par)
    no_param = 2
    parameters.update(stat_param(Y_st, y_theor, error_bound, no_param))
    
    return parameters

def linear_func_par_opt(Y_st, X_st, st_r):
    """
    The function implemented to calculate an optimal 4PL function parameters. The 5PL function is given below. Returns a list of tuples with the 4PL model parameters.
    Function input:
    Uses tuple or a list of two 1-D lists of calibration standards data of the same size as an input data.
    returns list of tuples with optimal 4PL-model parameters and R_squ
    """       
    bounds=[(st_r['B'][0], st_r['B'][1]), (st_r['A'][0], st_r['A'][1])]
    result = differential_evolution(linear_resid, bounds, args = (Y_st, X_st), 
                                    maxiter=750000, popsize= 45, strategy='best2bin')

    param = [result.x[0], result.x[1]]
    RSS = linear_resid(param, Y_st, X_st)/len(X_st)  
    error_bound = check_linear_bounds(param, st_r, RSS) 
    parameters={'A_par1': result.x[0], 'B_par1': result.x[1], 'RSS': RSS}
    y_theor = linear_func(X_st, param)    
    no_param = 2
    parameters.update(stat_param(Y_st, y_theor, error_bound, no_param))
    
    return parameters

def linear_func(X_data, param):
    """Linear equation."""
    #para_val = [param['A_par1'], param['B_par1']]
    return param[1]*np.array(X_data) + param[0]

def linear_concentration(Y_data, param):
    """
    The function was implemented to calculate titer concentration from absorbance and 4PL model parameters (reverse 4PL-function).
    Function inputs:
    Y_data - values of absorbance
    param - list of tuples with optimal 4PL-model parameters
    returns list of titer concentration values
    """    
    #return (Y_data - param['B_par1'])*(1.0/param['A_par1'])
    return (np.array(Y_data) - param['A_par1'])*(1.0/param['B_par1'])

###############################################################################
"""
Functions for logarithmic approximation:
1. definition of function
2. fit method: curve_fit
3. fit method: differential_evolution
4. calculating the deviation of the fitted function
5. calculation based on adjusted concentration function
"""

def ln_func(X_data, param):
    """
    Returns the values of absorbance using titer concentration and model parameters
    Function input:
    X_data - list of titer concentrations
    param - list of tuples of the optimal parameters obtained for the logarithmic model
    Returns list of calculated absorbance values
    """
    #X_data.astype(np.float64).apply(np.log10) #!!! this is quriozum!!!
    #np.log(X_data.astype(np.float64))
    return param[1]*np.log(X_data.astype(np.float64)) + param[0] 
    #return param[1]*np.log(np.array(X_data)) + param[0] 

def ln_resid(par, y, x):
    """Deviations of data from log curve"""
    err = y - ln_func(x, par)
    return sum(err**2)

def check_ln_bounds(par, st_r, RSS):
    """Deviations of data from logit curve"""
    if(par[1] == st_r['A'][0] or par[1] == st_r['A'][1] or par[0] == st_r['B'][0] or 
       par[0] == st_r['B'][1] or RSS > 0.3):
        """ at least one of the parameters is equal to the range limit, error!"""
        err = 1
    else:
        """ the parameters in proper range, ok"""
        err = 0

    return err

def ln_func_curve_fit(Y_st, X_st, st_r):
    """
    Optimization on the base of curvr_fit function. Returns list of tuples with optimal 
    4PL-model parameters and R_squ
    """    
    def ln_call(X_data, A, B):       
        return A*np.log(X_data) + B

    par_cv, pcov = curve_fit(ln_call, X_st, Y_st, 
                          bounds=([st_r['B'][0], st_r['A'][0]],[st_r['B'][1], st_r['A'][1]]))
    # curve_fit has oposit order of parameters than differential_evolution! par = [par_cv[1], par_cv[0]]
    par = np.flip(par_cv, axis=0)
    RSS = ln_resid(par, Y_st, X_st)/len(X_st)
    error_bound = check_ln_bounds(par, st_r, RSS)        
    parameters = {'B_par1': par[0], 'A_par1': par[1], 'RSS': RSS}
    y_theor = ln_func(X_st, par)
    no_param = 2
    parameters.update(stat_param(Y_st, y_theor, error_bound, no_param))
    
    return (parameters)

def ln_func_par_opt(Y_st, X_st, st_r):
    """
    The function implemented to calculate an optimal ln function parameters. The logarithmic function is given below. Returns list of tuples with theparameters.
    Uses tuple of two 1-D lists of calibration standards data of the same size as an input data.
    """
    bounds = [(st_r['B'][0], st_r['B'][1]),(st_r['A'][0], st_r['A'][1])]
    result = differential_evolution(ln_resid, bounds, args = (Y_st, X_st),
                                    maxiter=750000, popsize= 45, strategy='best2bin')    
   
    par = [result.x[0], result.x[1]]
    RSS = ln_resid(par, Y_st, X_st)/len(X_st)
    error_bound = check_ln_bounds(par, st_r, RSS)
    parameters = {'B_par1': par[0], 'A_par1': par[1], 'RSS': RSS}
    y_theor = ln_func(X_st, par)
    no_param = 2
    parameters.update(stat_param(Y_st, y_theor, error_bound, no_param))

    return(parameters)

def ln_func_concentration(Y_data, param):
    """
    The function implemented to calculate titer concentration values. 
    Returns list and uses list of absorbance values and parameters obtained from the optimization procedure from ln_func_par_opt.
    """
    return np.exp((np.array(Y_data) - param['B_par1'])/param['A_par1'])

###############################################################################
"""
Functions for 4PL approximation:
1. definition of function
2. fit method: curve_fit
3. fit method: differential_evolution
4. calculating the deviation of the fitted function
5. calculation based on adjusted concentration function
"""

def logit_4PL_func(X_data, param):
    """
    The function implemented in order to return the values of absorbance using titer concentration and 4PL model parameters.
    Function input:
    X_data - list of titer concentrations
    param - list of tuples of the optimal parameters obtained for the 4PL model
    returns calculated absorbance values
    """
    return param[0] + (param[1] - param[0])/(1 + (np.array(X_data)/param[3])**param[2])

def logit_4PL_resid(par, y, x):
    """Deviations of data from logit curve"""
    err = y - logit_4PL_func(x, par)
    return sum(err**2)

def check_4PL_bounds(par, st_r, RSS):
    """Deviations of data from logit curve"""
    if(par[1] == st_r['A'][0] or par[1] == st_r['A'][1] or par[2] == st_r['B'][0] or 
       par[2] == st_r['B'][1] or par[3] == st_r['C'][0] or par[3] == st_r['C'][1] or 
       par[0] == st_r['D'][0] or par[0] == st_r['D'][1] or RSS > 0.3):
        """ at least one of the parameters is equal to the range limit, error!"""
        err = 1
    else:
        """ the parameters in proper range, ok"""
        err = 0

    return err

def logit_4PL_curve_fit(Y_st, X_st, st_r):
    """
    Optimization on the base of curvr_fit function. Returns list of tuples with 
    optimal 4PL-model parameters and R_squ
    """
    def logit_4PL_call(X_data, D, A, B, C):       
        return D + (A - D)/(1 + (np.array(X_data)/C)**B)
    
    par, pcov = curve_fit(logit_4PL_call, X_st, Y_st, 
                          bounds=([st_r['D'][0], st_r['A'][0], st_r['B'][0], st_r['C'][0]], 
                                  [st_r['D'][1], st_r['A'][1], st_r['B'][1], st_r['C'][1]]))
    
    RSS = logit_4PL_resid(par, Y_st, X_st)/len(X_st)    
    error_bound = check_4PL_bounds(par, st_r, RSS)    
    parameters = {'D_par1': par[0], 'A_par1': par[1], 'B_par1': par[2], 'C_par1': par[3], 'RSS': RSS}    
    y_theor = logit_4PL_func(X_st, par)
    no_param = 4
    parameters.update(stat_param(Y_st, y_theor, error_bound, no_param))

    return parameters

def logit_4PL_par_opt(Y_st, X_st, st_r):
    """
    The function implemented to calculate an optimal 4PL function parameters. The 5PL function is given below. Returns a list of tuples with the 4PL model parameters.
    Function input:
    Uses tuple or a list of two 1-D lists of calibration standards data of the same size as an input data.
    Returns list of tuples with optimal 4PL-model parameters and R_squ.
    """    
    bounds=[(st_r['D'][0], st_r['D'][1]), (st_r['A'][0], st_r['A'][1]),
            (st_r['B'][0], st_r['B'][1]), (st_r['C'][0], st_r['C'][1])]
    result = differential_evolution(logit_4PL_resid, bounds, args = (Y_st, X_st),
                                    maxiter=750000, popsize= 45, strategy='best2bin')

    par = [result.x[0], result.x[1], result.x[2], result.x[3]]
    RSS = logit_4PL_resid(par, Y_st, X_st)/len(X_st)  
    error_bound = check_4PL_bounds(par, st_r, RSS)
    parameters = {'D_par1': par[0], 'A_par1': par[1], 'B_par1': par[2], 'C_par1': par[3], 'RSS': RSS}        
    y_theor = logit_4PL_func(X_st, par)   
    no_param = 4
    parameters.update(stat_param(Y_st, y_theor, error_bound, no_param))
       
    return (parameters)

def logit_4PL_concentration(Y_data, param):
    """
    The function was implemented to calculate titer concentration from absorbance and 
    4PL model parameters (reverse 4PL-function).
    Function inputs:
    Y_data - values of absorbance
    pa - list of dictionary with optimal 4PL-model parameters
    Returns list of titer concentration values
    """
    return param['C_par1']*((((param['A_par1'] - param['D_par1'])/(np.array(Y_data) \
                - param['D_par1'])) - 1)**(1/param['B_par1']))

###############################################################################
"""
Functions for 5PL approximation:
1. definition of function
2. fit method: curve_fit
3. fit method: differential_evolution
4. calculating the deviation of the fitted function
5. calculation based on adjusted concentration function
"""

def logit_5PL_func(X_data, param):
    """
    Returns the values of absorbance using titer concentration and 5PL model parameters
    Function input:
    X_data - list of titer concentrations
    param - list of tuples of the optimal parameters obtained for the 5PL model
    Returns calculated absorbance values
    """
    return param[0] + ((param[1] - param[0])/(1 + (np.array(X_data)/param[3])**param[2])**param[4])

def logit_5PL_resid(par, y, x):
    """Deviations of data from log curve"""
    err = y - logit_5PL_func(x, par)
    return sum(err**2)

def check_5PL_bounds(par, st_r, RSS):
    """Deviations of data from logit curve"""
    if(par[1] == st_r['A'][0] or par[1] == st_r['A'][1] or par[2] == st_r['B'][0] or 
       par[2] == st_r['B'][1] or par[3] == st_r['C'][0] or par[3] == st_r['C'][1] or 
       par[0] == st_r['D'][0] or par[0] == st_r['D'][1] or par[4] == st_r['E'][0] or 
       par[4] == st_r['E'][1] or RSS > 0.3):
        """ at least one of the parameters is equal to the range limit, error!"""
        err = 1
    else:
        """ the parameters in proper range, ok"""
        err = 0

    return err

def logit_5PL_curve_fit(Y_st, X_st, st_r):
    """
    Optimization on the base of curvr_fit function. Returns list of tuples with 
    optimal 5PL-model parameters and R_squ
    """
    def logit_5PL_call(X_data, D, A, B, C, E):       
        return  D + ((A - D)/(1 + (np.array(X_data)/C)**B)**E)   

    par, pcov = curve_fit(logit_5PL_call, X_st, Y_st, 
                          bounds=([st_r['D'][0], st_r['A'][0], st_r['B'][0], st_r['C'][0], 
                                   st_r['E'][0]], [st_r['D'][1], st_r['A'][1], st_r['B'][1], 
                                   st_r['C'][1], st_r['E'][1]]))        

    RSS = logit_5PL_resid(par, Y_st, X_st)/len(X_st)
    error_bound = check_5PL_bounds(par, st_r, RSS)  
    parameters = {'D_par1': par[0], 'A_par1': par[1], 'B_par1': par[2], 'C_par1': par[3], 
                  'E_par1': par[4], 'RSS': RSS}    
    y_theor = logit_5PL_func(X_st, par)
    no_param = 5
    parameters.update(stat_param(Y_st, y_theor, error_bound, no_param))
   
    return parameters

def logit_5PL_par_opt(Y_st, X_st, st_r):
    """
    The function implemented to calculate an optimal 5PL function parameters. The 5PL function is given below. Returns list of tuples with the parameters.
    Uses tuple or a list of two 1-D lists of calibration standards data of the same size as an input data.
    Returns the list of tuples with 5PL model parameters
    """   
    bounds=[(st_r['D'][0], st_r['D'][1]), (st_r['A'][0], st_r['A'][1]), (st_r['B'][0], st_r['B'][1]), 
            (st_r['C'][0], st_r['C'][1]), (st_r['E'][0], st_r['E'][1])]
       
    res = differential_evolution(logit_5PL_resid, bounds, args = (Y_st, X_st),
                                 maxiter=750000, popsize= 45, strategy='best2bin')

    par = [res.x[0], res.x[1], res.x[2], res.x[3], res.x[4]]  
    RSS = logit_5PL_resid(par, Y_st, X_st)/len(X_st)
    error_bound = check_5PL_bounds(par, st_r, RSS)       
    parameters = {'D_par1': par[0], 'A_par1': par[1], 'B_par1': par[2], 'C_par1': par[3], 
                  'E_par1': par[4], 'RSS': RSS}    
    y_theor = logit_5PL_func(X_st, par)
    no_param = 5
    parameters.update(stat_param(Y_st, y_theor, error_bound, no_param))
    
    return (parameters)

def logit_5PL_concentration(Y_data, param):
    """
    The function was implemented to calculate titer concentration from absorbance and 5PL model parameters.
    Function inputs:
    Y_data - values of absorbance
    param - list of tuples with optimal 5PL-model parameters
    Returns list of titer concentration values"""
    return param['C_par1']*(((((param['A_par1'] - param['D_par1'])/(np.array(Y_data)  \
                - param['D_par1']))**(1/param['E_par1']))-1)**(1/param['B_par1']))

###############################################################################
