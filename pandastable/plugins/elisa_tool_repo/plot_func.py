#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on January 2019
@author:  Edward Maievskij, Marek Bawiec, Grzegorz Banach
The ELISA tool plugin: module for graphics presentation of results.
"""

__author__ = "Marek Bawiec, Grzegorz Banach, Edward Maievskij"
__copyright__ = "Copyright 2019, Physiolution Polska"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Grzegorz Banach"
__email__ = "g.banach@physiolution.pl"
__status__ = "Production"

import matplotlib.pyplot as plt

def fig_lin_er(X_fun, Y_fun, X_std, Y_std, X_sam, Y_sam,  
               X_sb_err, X_su_err, Y_s_err, Y_std_err, title_s, repres):
    """
    The function was implemented to draw a simple plot in linear scale with a theoretical 4PL curve, calibration standards and measured samples.
    X_fun, Y_fun - theoretical curve data points
    X_std, Y_std - calibration standards data points
    X_sam, Y_sam - sample measurement points
    """
    #name_file = 'calc_results_lin.png'
    name_file = 'calc_results_' + repres + '.png'
    template_path = 'pandastable/plugins/elisa_tool_repo/template/'
    Fpath = template_path + name_file

    plt.plot(X_fun, Y_fun, label='Theory')
    plt.errorbar(X_std, Y_std, yerr=Y_std_err, fmt='o', color='r', ecolor='black', 
                 label='Standards')
    plt.errorbar(X_sam, Y_sam, xerr=[X_sb_err, X_su_err], yerr=Y_s_err, fmt='v', 
                 color='orange', ecolor='lightgray', label='Samples')
    plt.legend(loc='lower right', ncol=1)        
    plt.grid(True) 
    plt.tick_params(axis='both', which='both', direction= 'in')
    plt.xlabel("Concentration")
    plt.ylabel("Absorbance")
    plt.title(title_s)
    plt.savefig(Fpath, format='png', bbox_inches = 'tight', dpi=300)
    plt.close()
    """Returns the filepath to obtained plot."""
    return name_file

def fig_lin_pl(X_fun, Y_fun, X_std, Y_std, X_sam, Y_sam, title_s, repres):
    """
    The function was implemented to draw a simple plot in linear scale with a theoretical 4PL curve, calibration standards and measured samples.
    X_fun, Y_fun - theoretical curve data points
    X_std, Y_std - calibration standards data points
    X_sam, Y_sam - sample measurement points
    """
    name_file = 'calc_results_' + repres + '.png'
    template_path = 'pandastable/plugins/elisa_tool_repo/template/'
    Fpath = template_path + name_file

    #plt.figure(figsize=(7,4), dpi=150)
    plt.plot(X_fun, Y_fun, label='Theory')
    plt.plot(X_std, Y_std, 'o', color='r', label='Standards')
    plt.plot(X_sam, Y_sam, 'v', color='orange', label='Samples')
    plt.legend(loc='lower right', ncol=1)
        
    plt.grid(True) 
    plt.tick_params(axis='both', which='both', direction= 'in')
    plt.xlabel("Concentration")
    plt.ylabel("Absorbance")
    plt.title(title_s)
    plt.savefig(Fpath, format='png', bbox_inches = 'tight', dpi=300)
    plt.close()
    """Returns the filepath to obtained plot."""
    return name_file

def fig_lnx_er(X_fun, Y_fun, X_std, Y_std, X_sam, Y_sam,  
               X_sb_err, X_su_err, Y_s_err, Y_std_err, title_s, repres):
    """
    The function was implemented to draw a simple plot in linear scale with a theoretical 4PL curve, calibration standards and measured samples.
    X_fun, Y_fun - theoretical curve data points
    X_std, Y_std - calibration standards data points
    X_sam, Y_sam - sample measurement points
    """
    name_file = 'calc_results_' + repres + '.png'
    template_path = 'pandastable/plugins/elisa_tool_repo/template/'
    Fpath = template_path + name_file

    plt.semilogx(X_fun, Y_fun, label='Theory')
    plt.errorbar(X_std, Y_std, yerr=Y_std_err, fmt='o', color='r', ecolor='black', 
                 label='Standards')
    plt.errorbar(X_sam, Y_sam, xerr=[X_sb_err, X_su_err], yerr=Y_s_err, fmt='v', 
                 color='orange', ecolor='lightgray', label='Samples')
    plt.legend(loc='upper left', ncol=1)
        
    plt.grid(True) 
    plt.tick_params(axis='both', which='both', direction= 'in')
    plt.xlabel("ln(Concentration)")
    plt.ylabel("Absorbance")
    plt.title(title_s)
    plt.savefig(Fpath, format='png', bbox_inches = 'tight', dpi=300)
    plt.close()
    """Returns the filepath to obtained plot."""
    return name_file

def fig_lnx_pl(X_fun, Y_fun, X_std, Y_std, X_sam, Y_sam, title_s, repres):
    """
    The function was implemented to draw a simple plot in linear scale with a theoretical 4PL curve, calibration standards and measured samples.
    X_fun, Y_fun - theoretical curve data points
    X_std, Y_std - calibration standards data points
    X_sam, Y_sam - sample measurement points
    """
    name_file = 'calc_results_' + repres + '.png'
    template_path = 'pandastable/plugins/elisa_tool_repo/template/'
    Fpath = template_path + name_file

    plt.semilogx(X_fun, Y_fun, label='Theory')
    plt.semilogx(X_std, Y_std, 'o', color='r',label='Standards')
    plt.semilogx(X_sam, Y_sam, 'v', label='Samples')
    plt.legend(loc='upper left', ncol=1)        
    plt.grid(True) 
    plt.tick_params(axis='both', which='both', direction= 'in')
    plt.xlabel("ln(Concentration)")
    plt.ylabel("Absorbance")
    plt.title(title_s)
    plt.savefig(Fpath, format='png', bbox_inches = 'tight', dpi=300)
    plt.close()
    """Returns the filepath to obtained plot."""
    return name_file

def fig_lny_er(X_fun, Y_fun, X_std, Y_std, X_sam, Y_sam,  
               X_sb_err, X_su_err, Y_s_err, Y_std_err, title_s, repres):
    """
    The function was implemented to draw a simple plot in linear scale with a theoretical 4PL curve, calibration standards and measured samples.
    
    X_fun, Y_fun - theoretical curve data points
    X_std, Y_std - calibration standards data points
    X_sam, Y_sam - sample measurement points
    """
    name_file = 'calc_results_' + repres + '.png'
    template_path = 'pandastable/plugins/elisa_tool_repo/template/'
    Fpath = template_path + name_file

    plt.semilogy(X_fun, Y_fun, label='Theory')
    plt.semilogy(X_std, Y_std, 'o', color='r',label='Standards')
    plt.semilogy(X_sam, Y_sam, 'v', label='Samples')
    plt.legend(loc='lower right', ncol=1)
        
    plt.grid(True) 
    plt.tick_params(axis='both', which='both', direction= 'in')
    plt.xlabel("Concentration")
    plt.ylabel("ln(Absorbance)")
    plt.title(title_s)
    plt.savefig(Fpath, format='png', bbox_inches = 'tight', dpi=300)
    plt.close()
    """Returns the filepath to obtained plot."""
    return name_file

def fig_lny_pl(X_fun, Y_fun, X_std, Y_std, X_sam, Y_sam, title_s, repres):
    """
    The function was implemented to draw a simple plot in linear scale with a theoretical 4PL curve, calibration standards and measured samples.
    X_fun, Y_fun - theoretical curve data points
    X_std, Y_std - calibration standards data points
    X_sam, Y_sam - sample measurement points
    """
    name_file = 'calc_results_' + repres + '.png'
    template_path = 'pandastable/plugins/elisa_tool_repo/template/'
    Fpath = template_path + name_file

    plt.semilogy(X_fun, Y_fun, label='Theory')
    plt.semilogy(X_std, Y_std, 'o', color='r',label='Standards')
    plt.semilogy(X_sam, Y_sam, 'v', label='Samples')
    plt.legend(loc='lower right', ncol=1)      
    plt.grid(True) 
    plt.tick_params(axis='both', which='both', direction= 'in')
    plt.xlabel("Concentration")
    plt.ylabel("ln(Absorbance)")
    plt.title(title_s)
    plt.savefig(Fpath, format='png', bbox_inches = 'tight', dpi=300)
    plt.close()
    """Returns the filepath to obtained plot."""
    return name_file 


def fig_lnln_er(X_fun, Y_fun, X_std, Y_std, X_sam, Y_sam,  
               X_sb_err, X_su_err, Y_s_err, Y_std_err, title_s, repres):
    """
    The function was implemented to draw a simple plot in linear scale with a theoretical 4PL curve, calibration standards and measured samples.
    X_fun, Y_fun - theoretical curve data points
    X_std, Y_std - calibration standards data points
    X_sam, Y_sam - sample measurement points
    """
    name_file = 'calc_results_' + repres + '.png'
    template_path = 'pandastable/plugins/elisa_tool_repo/template/'
    Fpath = template_path + name_file

    plt.figure()
    ax = plt.axes()
    ax.set_xscale("log", nonposx='clip')
    ax.set_yscale("log", nonposy='clip')
    plt.plot(X_fun, Y_fun, label='Theory')
    plt.errorbar(X_std, Y_std, yerr=Y_std_err, fmt='o', color='r', ecolor='black', 
                 label='Standards')
    plt.errorbar(X_sam, Y_sam, xerr=[X_sb_err, X_su_err], yerr=Y_s_err, fmt='v', 
                 color='orange', ecolor='lightgray', label='Samples')
    plt.legend(loc='upper left', ncol=1)
    plt.grid(True) 
    plt.tick_params(axis='both', which='both', direction= 'in')
    plt.xlabel("ln(Concentration)")
    plt.ylabel("ln(Absorbance)")
    plt.title(title_s)
    plt.savefig(Fpath, format='png', bbox_inches = 'tight', dpi=300)
    plt.close()
    """Returns the filepath to obtained plot."""
    return name_file

def fig_lnln_pl(X_fun, Y_fun, X_std, Y_std, X_sam, Y_sam, title_s, repres):
    """
    The function was implemented to draw a simple plot in linear scale with a theoretical 4PL curve, calibration standards and measured samples.
    X_fun, Y_fun - theoretical curve data points
    X_std, Y_std - calibration standards data points
    X_sam, Y_sam - sample measurement points
    """
    name_file = 'calc_results_' + repres + '.png'
    template_path = 'pandastable/plugins/elisa_tool_repo/template/'
    Fpath = template_path + name_file

    plt.loglog(X_fun, Y_fun, label='Theory')
    plt.loglog(X_std, Y_std, 'o', color='r',label='Standards')
    plt.loglog(X_sam, Y_sam, 'v', label='Samples')
    plt.legend(loc='upper left', ncol=1)
    plt.grid(True) 
    plt.tick_params(axis='both', which='both', direction= 'in')
    plt.xlabel("ln(Concentration)")
    plt.ylabel("ln(Absorbance)")
    plt.title(title_s)
    plt.savefig(Fpath, format='png', bbox_inches = 'tight', dpi=300)
    plt.close()
    """Returns the filepath to obtained plot."""
    return name_file