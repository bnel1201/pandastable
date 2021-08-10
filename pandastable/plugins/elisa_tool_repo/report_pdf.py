#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on January 2019
@author:  Edward Maievskij, Marek Bawiec, Grzegorz Banach
The ELISA tool plugin: module for pdf export functions.
"""

__author__ = "Marek Bawiec, Grzegorz Banach, Edward Maievskij"
__copyright__ = "Copyright 2019, Physiolution Polska"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Grzegorz Banach"
__email__ = "g.banach@physiolution.pl"
__status__ = "Production"

# from weasyprint import HTML
import datetime
import pandas as pd
import textwrap
from os import remove

def rej_samples_html_table(Y_s_bad):
    """
    The function was implemented to generate html-formatted table with the rejected sample names.
    """
    dftable = pd.DataFrame()
    dftable["Bad Sample"] = Y_s_bad['sample_name']
    dftable["Comment"] = Y_s_bad['blq_name']
    dftable.sort_index(inplace=True)
    dftable.index += 1
    
    html_table = dftable.to_html()
    return html_table 

def rep_html_table(D_sam):
    """
    The function was implemented to create a HTML-table named "Calculation results" from the list of list containing the data about sample names,
    titer concentration, bottom edge ot titer concentration standard deviation, top edge of titer concentration standard deviation, sample absorbance
    value and simmetrical value of absorbance standard deviation.
    """
    D_sam.reset_index(inplace=True)
    dftable = pd.DataFrame()
    dftable["Good Samples"] = D_sam['sam_name']
    dftable["Conc."] = D_sam['conc']
    dftable["SD down Conc."] = D_sam['conc_std_up']
    dftable["SD up Conc."] = D_sam['conc_std_dow']
    dftable["Absorbance"] = D_sam['absorbance']
    dftable["SD Abs."] = D_sam['abs_std_var']
    dftable.sort_values(by=["Good Samples"], inplace=True)
    dftable.index += 1
    
    dftable = dftable.style.format({'Absorbance': "{:,.5f}", "Conc.":"{:,.3f}", 
                              "SD down Conc.":"{:,.5f}", "SD up Conc.":"{:,.5f}", 
                              "SD Abs.":"{:,.5f}"}).hide_index().render()
   
    """returns html-formatted "calculation results" table"""
    return dftable

def csv_report_create(D_sam, Y_s_bad, rep_name, i_data, i_data_map, d_st, 
                      p_folder, param, order, cal_time, repres_run, st_ran):
    """
    The function was implemented to create and save csv report for 5PL model.
    """
    ts = datetime.datetime.now()
    ts_name = ts.strftime("%d_%b_%Y_%H_%M")
    dftable = pd.DataFrame()
    dftable["good_sample_names"] = D_sam['sam_name']
    dftable["concentration_X_axis"] = D_sam['conc']
    dftable["c_st_dev_bo"] = D_sam['conc_std_up']
    dftable["c_st_dev_up"] = D_sam['conc_std_dow']
    dftable["Absorbance_Y_axis"] = D_sam['sam_name']
    dftable["Abs_st_dev"] = D_sam['abs_std_var']
    dftable.sort_values(by=["good_sample_names"], inplace=True)
    dftable.set_index(['good_sample_names'], inplace=True)
    
    s_csv_res = dftable.to_csv(path_or_buf=None)

    dftable1 = pd.DataFrame()
    dftable1["bad_sample_names"] = Y_s_bad['sample_name']
    dftable["comment"] = Y_s_bad['blq_name']
    dftable.sort_index(inplace=True)
        
    s_csv_rej = dftable1.to_csv(path_or_buf=None)
    s_csv_i_data = i_data.to_csv(path_or_buf=None)
    s_csv_i_data_map = i_data_map.to_csv(path_or_buf=None)
    s_csv_d_st = d_st.to_csv(path_or_buf=None)
    
    doc_structure='Initial measurement results'+ '\r\n'+ s_csv_i_data + '\r\n'+ 'Multiwell plate map' +'\r\n'+s_csv_i_data_map + \
        '\r\n'+ 'Calibration standards'+'\r\n'+ s_csv_d_st + '\r\n'+ 'Calculation results'+'\r\n'+s_csv_res + '\r\n'+ 'BLQ samples'+ \
        '\r\n'+s_csv_rej + '\r\n'+'Coefficient of Determination R^2: '+ str(round(param['R_squ'],8))+ '\r\n'\
                         + 'Akaike Information Criterion AIC: '+ str(round(param['AIC_crit'],8))+ '\r\n'\
                         + 'Bayesian Information Criterion BIC: '+ str(round(param['BIC_crit'],8))+ '\r\n'\
                         + 'Coefficient of Correlation r: '+ str(round(param['R_corre'],8))+ '\r\n'\
                         + 'The Residual Sum of Squares RSS: ' + str(round(param['RSS'],8))+'\r\n'\
                         + '\r\n Data input in '+ repres_run 

    if ((order=="LIN curve_fit") or (order=="LIN diff_evol")):
        s=doc_structure + ' representation: Absorbance = B*Conc + A' + '\r\n'\
                        + 'A: ' + str(round(param['A_par1'],8))+'\r\n'\
                        + 'B: '+ str(round(param['B_par1'],8)) + '\r\n'\
                        + '\r\n' + 'The range of parameter changes used:' + '\r\n'\
                        + 'A: [' + str(st_ran['A'][0]) +' ;'+ str(st_ran['A'][1]) + '] \r\n'\
                        + 'B: [' + str(st_ran['B'][0]) +' ;'+ str(st_ran['B'][1]) + '] \r\n'\
                        + 'Time of calculation: ' + str(round(cal_time,6))
    
    if ((order=="LN curve_fit") or (order=="LN diff_evol")):
        s=doc_structure + ' representation: Absorbance=A*ln(Conc)+B' + '\r\n'\
                        + 'A: ' + str(round(param['A_par1'],8))+'\r\n'\
                        + 'B: '+ str(round(param['B_par1'],8)) + '\r\n'\
                        + '\r\n' + 'The range of parameter changes used:' + '\r\n'\
                        + 'A: [' + str(st_ran['A'][0]) +' ;'+ str(st_ran['A'][1]) + '] \r\n'\
                        + 'B: [' + str(st_ran['B'][0]) +' ;'+ str(st_ran['B'][1]) + '] \r\n'\
                        + 'Time of calculation: ' + str(round(cal_time,6))

    if ((order=="4PL diff_evol") or (order=="4PL curve_fit")):
        s=doc_structure + ' representation: Absorbance=D+((A-D)/(1+(Conc/C)^B)'+'\r\n'\
                        + 'D: ' + str(round(param['D_par1'],8))+'\r\n' + 'A: '+str(round(param['A_par1'],8)) \
                        + '\r\n' + 'B: ' \
                        +  str(round(param['B_par1'],8))+'\r\n'+'C: '+str(round(param['C_par1'],8)) + '\r\n'\
                        + '\r\n' + 'The range of parameter changes used:' + '\r\n'\
                        + 'D: [' + str(st_ran['D'][0]) +' ;'+ str(st_ran['D'][1]) + '] \r\n'\
                        + 'A: [' + str(st_ran['A'][0]) +' ;'+ str(st_ran['A'][1]) + '] \r\n'\
                        + 'B: [' + str(st_ran['B'][0]) +' ;'+ str(st_ran['B'][1]) + '] \r\n'\
                        + 'C: [' + str(st_ran['C'][0]) +' ;'+ str(st_ran['C'][1]) + '] \r\n'\
                        + 'Time of calculation: ' + str(round(cal_time,6))

    if ((order=="5PL curve_fit") or (order=="5PL diff_evol")):
        s=doc_structure + ' representation: Absorbance=D+((A-D)/(1+(Conc/C)^B)^E)'+'\r\n'\
                        + 'D: ' + str(round(param['D_par1'],8)) + '\r\n' + 'A: '+ str(round(param['A_par1'],8)) + '\r\n'\
                        + 'B: ' + str(round(param['B_par1'],8)) + '\r\n' + 'C: '+ str(round(param['C_par1'],8)) \
                        + '\r\n' + 'E: ' + str(round(param['E_par1'],8)) + '\r\n'\
                        + '\r\n' + 'The range of parameter changes used:' + '\r\n'\
                        + 'D: [' + str(st_ran['D'][0]) +' ;'+ str(st_ran['D'][1]) + '] \r\n'\
                        + 'A: [' + str(st_ran['A'][0]) +' ;'+ str(st_ran['A'][1]) + '] \r\n'\
                        + 'B: [' + str(st_ran['B'][0]) +' ;'+ str(st_ran['B'][1]) + '] \r\n'\
                        + 'C: [' + str(st_ran['C'][0]) +' ;'+ str(st_ran['C'][1]) + '] \r\n'\
                        + 'E: [' + str(st_ran['E'][0]) +' ;'+ str(st_ran['E'][1]) + '] \r\n'\
                        + 'Time of calculation: ' + str(round(cal_time,6))
    
    file= open(p_folder + '/' + rep_name + '_' + order + '_' + ts_name + "_data.csv","w")
    file.write(s)
    file.close() 
    return

def csv_error_create(rep_name, p_folder, param, order, error_text, repres_run, st_ran):
    """
    The function was implemented to create and save csv report for all models.
    """
    doc_structure = error_text + '\r\n Results for '+ repres_run + ' representation: ' \
                        + '\r\n'+'Coefficient of Determination R^2,'+ str(round(param['R_squ'],8)) + '\r\n'\
                        + 'Akaike Information Criterion AIC,'+ str(round(param['AIC_crit'],8)) + '\r\n'\
                        + 'Bayesian Information Criterion BIC,'+ str(round(param['BIC_crit'],8)) + '\r\n'\
                        + 'Coefficient of Correlation r,'+ str(round(param['R_corre'],8)) + '\r\n'\
                        + 'The Residual Sum of Squares RSS,' + str(round(param['RSS'],8)) +'\r\n'\
                                    
    if ((order=="LIN curve_fit") or (order=="LIN diff_evol")):
        s=doc_structure + '\r\n' + 'Absorbance = B*Conc + A' + '\r\n'\
                        + 'A,' + str(round(param['A_par1'],8)) +'\r\n'\
                        + 'B,'+ str(round(param['B_par1'],8)) +'\r\n'\
                        + '\r\n' + 'The range of parameter changes used:' + '\r\n'\
                        + 'A: [' + str(st_ran['A'][0]) +' ;'+ str(st_ran['A'][1]) + '] \r\n'\
                        + 'B: [' + str(st_ran['B'][0]) +' ;'+ str(st_ran['B'][1]) + '] \r\n'\
   
    if ((order=="LN curve_fit") or (order=="LN diff_evol")):
        s=doc_structure + '\r\n' + 'Absorbance=A*ln(Conc)+B' + '\r\n'\
                        + 'A: ' + str(round(param['A_par1'],8)) +'\r\n'\
                        + 'B: '+ str(round(param['B_par1'],8))+'\r\n'\
                        + '\r\n' + 'The range of parameter changes used:' + '\r\n'\
                        + 'A: [' + str(st_ran['A'][0]) +' ;'+ str(st_ran['A'][1]) + '] \r\n'\
                        + 'B: [' + str(st_ran['B'][0]) +' ;'+ str(st_ran['B'][1]) + '] \r\n'\

    if ((order=="4PL diff_evol") or (order=="4PL curve_fit")):
        s=doc_structure + '\r\n' + 'Absorbance=D+((A-D)/(1+(Conc/C)^B)' + '\r\n'\
                        + 'D: ' + str(round(param['D_par1'],8)) + '\r\n' + 'A: '+str(round(param['A_par1'],8)) \
                        + '\r\n' + 'B: ' + str(round(param['B_par1'],8))+'\r\n'+'C: '+str(round(param['C_par1'],8))+'\r\n'\
                        + '\r\n' + 'The range of parameter changes used:' + '\r\n'\
                        + 'D: [' + str(st_ran['D'][0]) +' ;'+ str(st_ran['D'][1]) + '] \r\n'\
                        + 'A: [' + str(st_ran['A'][0]) +' ;'+ str(st_ran['A'][1]) + '] \r\n'\
                        + 'B: [' + str(st_ran['B'][0]) +' ;'+ str(st_ran['B'][1]) + '] \r\n'\
                        + 'C: [' + str(st_ran['C'][0]) +' ;'+ str(st_ran['C'][1]) + '] \r\n'\

    if ((order=="5PL curve_fit") or (order=="5PL diff_evol")):
        s=doc_structure + '\r\n' + 'Absorbance=D+((A-D)/(1+(Conc/C)^B)^E)' + '\r\n'\
                        + 'D: ' + str(round(param['D_par1'],8)) + '\r\n' + 'A: '+ str(round(param['A_par1'],8)) + '\r\n'\
                        + 'B: ' + str(round(param['B_par1'],8)) + '\r\n' + 'C: '+ str(round(param['C_par1'],8)) + '\r\n'\
                        + 'E: ' + str(round(param['E_par1'],8)) +'\r\n'\
                        + '\r\n' + 'The range of parameter changes used:' + '\r\n'\
                        + 'D: [' + str(st_ran['D'][0]) +' ;'+ str(st_ran['D'][1]) + '] \r\n'\
                        + 'A: [' + str(st_ran['A'][0]) +' ;'+ str(st_ran['A'][1]) + '] \r\n'\
                        + 'B: [' + str(st_ran['B'][0]) +' ;'+ str(st_ran['B'][1]) + '] \r\n'\
                        + 'C: [' + str(st_ran['C'][0]) +' ;'+ str(st_ran['C'][1]) + '] \r\n'\
                        + 'E: [' + str(st_ran['E'][0]) +' ;'+ str(st_ran['E'][1]) + '] \r\n'\

    ts=datetime.datetime.now()
    ts_name=ts.strftime("%d_%b_%Y_%H_%M")
    file= open(p_folder + '/' + rep_name + '_' + order + '_' + ts_name + "_error.csv","w")
    file.write(s)
    file.close() 
    
    return

    
def pdf_report_create(rep_name, i_data, i_data_map, d_st, p_folder, D_samples, Y_s_bad, param, 
                      legend, plot_lin, plot_lnx, plot_lny, plot_lnln, spec, notice, order, 
                      cal_time, repres_run):
    """
    The function was implemented in order to create logarithmic model pdf-report with the help of the functions from weasyprint module.
    """
    #variables definitions
    ts = datetime.datetime.now()
    ts1 = ts.strftime("%d.%m.%Y %H:%M")
    ts_name = ts.strftime("%d_%m_%Y_%H_%M")
    expdate = legend['DATE_of_exp']
    projname = legend['PROJECT_NAME']
    sopname = legend["SOP_name"]
    resname = legend["RESEARCH_name"]
    test_no = legend["TEST_No"]
    sopver = legend["SOP_version"]
    username = legend['PERFORMED_BY']
    tempver = legend['TEMPLATE_version']
    effectivetemplate = legend['EFFECTIVE']
    if len(resname)>65:
        s61=textwrap.wrap(text=resname, width=65)
        resname= ' \A '.join(s61)
    
    if len(notice)>99:
        s71=textwrap.wrap(text=notice, width=99)
        notice= ' \A '.join(s71)

    i_data = i_data.fillna('BLQ')
    i_data = i_data.to_html(index_names=False, col_space=10)
    i_data_map = i_data_map.to_html(index_names=False, col_space=20)
    d_st.reset_index(inplace=True)
    d_st = d_st.rename(columns={"conc": "Conc.", "absorbance": "Absorbance", "samples_nb":"Number",
                                "abs_std":"Measured", "abs_std_var":"Variation", "std_name":"Std. name"})
    d_st = d_st.drop(['Measured','Errors'], 1) 
    d_st = d_st.style.format({'Absorbance': "{:,.4f}", "Conc.":"{:,.2f}", 
                              "Variation":"{:,.5f}"}).hide_index().render()
  
    g_sample_table = rep_html_table(D_samples)
    rej_sam = rej_samples_html_table(Y_s_bad)
    spec.index += 1
    spec_html_table = spec.to_html()
    
    if ((order=="LIN curve_fit") or (order=="LIN diff_evol")):     
        core_name="_" + order + "_out_report_"
        report_name="Linear"
        formula="Absorbance = B*Conc + A"
        sb=("""
            <div class="elem">
                <h2>Model: {R_name} fitting in {input_data} system</h2>
                <p style="font-size:12px"> 
                    {form}<br>
                </p>
                
                <h3>Model parameters</h3>
                <p style="font-size:12px">
                    A= {A:.6f}, B= {B:.6f} <br>
                </p>
            </div>
            """).format(R_name=report_name, input_data=repres_run, form=formula, 
                        A=param['A_par1'], B=param['B_par1'])
   
    if ((order=="LN curve_fit") or (order=="LN diff_evol")):     
        core_name="_" + order + "_out_report_"
        report_name="Logarithmic"
        formula="Absorbance = A*ln(Conc) + B"
        sb=("""
            <div class="elem">
                <h2>Model: {R_name} fitting in {input_data} system</h2>
                <p style="font-size:12px"> 
                    {form}<br>
                </p>
                
                <h3>Model parameters</h3>
                <p style="font-size:12px">
                    A= {A:.6f}, B= {B:.6f} <br>
                </p>
            </div>
            """).format(R_name=report_name, input_data=repres_run, form=formula, 
                        A=param['A_par1'], B=param['B_par1'])

    if ((order=="4PL diff_evol") or (order=="4PL curve_fit")): 
        core_name="_logit_" + order + "_out_report_"
        report_name="Logit " + order
        formula="Absorbance = D + ((A - D)/(1 + (Conc/C)^B)"
        sb=("""
            <div class="elem">
                <h2>Model: {R_name} fitting in {input_data} system</h2>
                <p style="font-size:12px"> 
                    {form}<br>
                </p>
                
                <h3>Model parameters</h3>
                <p style="font-size:12px">
                      A= {A:.6f}, B= {B:.6f}, C= {C:.6f}, D= {D:.6f}</p>
                </p>
          </div>
            """).format(R_name=report_name, input_data=repres_run, form=formula, 
                        D=param['D_par1'], A=param['A_par1'], B=param['B_par1'], C=param['C_par1'])

    if ((order=="5PL curve_fit") or (order=="5PL diff_evol")):
        core_name="_logit_" + order + "_out_report_"
        report_name="Logit " + order
        formula="Absorbance = D + ((A - D)/(1 + (Conc/C)^B)^E)"
        sb=("""
          <div class="elem">
                <h2>Model: {R_name} fitting in {input_data} system</h2>
                <p style="font-size:12px"> 
                    {form}<br>
                </p>              
                <h3>Model parameters</h3>
                <p style="font-size:12px">
                    A= {A:.6f}, B= {B:.6f}, C= {C:.6f}, D= {D:.6f}, E= {E:.6f}</p>
                </p>
          </div>
            """).format(R_name=report_name, input_data=repres_run, form=formula, D=param['D_par1'], 
                        A=param['A_par1'], B=param['B_par1'],  C=param['C_par1'], E=param['E_par1'])
    
    template_dir = 'pandastable/plugins/elisa_tool_repo/template/'
    html_temp = open(template_dir + 'template_html.html', "r").read()
    
    s_html = html_temp.format(spec_html=spec_html_table, exdate=expdate, proj_name=projname,  
                           uname=username, tno= test_no, timestamp1=ts1, timestamp=ts1, 
                           data_in=i_data, data_map=i_data_map, cal_st=d_st, plot0 = plot_lin, 
                           plot1 = plot_lnx, plot2 = plot_lny, plot3 = plot_lnln, pathfolder=p_folder,
                           table1=g_sample_table, table2=rej_sam, sb_approx=sb, cal_time=str(round(cal_time,3)),
                           rss=str(round(param['RSS'],6)), rsq=str(round(param['R_squ'],6)),AIC=str(round(param['AIC_crit'],6)), 
                           BIC=str(round(param['BIC_crit'],6)), rcc=str(round(param['R_corre'],6)))
    
    s_css = css_string_new(sop_name=sopname, res_name=resname, sop_ver=sopver, noti=notice, temp_version=tempver, eff=effectivetemplate)

    s_fine= s_css + s_html 
    
    #temporary html-file generation
    Html_file= open(template_dir + 'AAA_tempfile1.html',"w")
    Html_file.write(s_fine)
    Html_file.close()
    #conversion to pdf with further removing of temporary files, becouse of /path for including png files
    HTML(template_dir + "AAA_tempfile1.html").write_pdf(p_folder + '/' + rep_name + core_name + ts_name + '.pdf')
    #HTML(string=s_fine).write_pdf(p_folder + '/' + rep_name + core_name + ts_name + 'HTML_direct.pdf')
    remove(template_dir + "AAA_tempfile1.html")
    
    return "pdf report generated"

def css_string_new(sop_name, res_name, sop_ver, noti, temp_version, eff):
    
    css_temp = open('pandastable/plugins/elisa_tool_repo/template/template_css.css', "r").read()
    
    tc_content = sop_name + ' \A ' + res_name    # tc_content = "{sop_name} \A {res_name}"
    control_1 = css_temp.replace('tc_content', tc_content)
    tr_content = "Ver: " + sop_ver + " \A \A Page \" counter(page) \" of \" counter(pages) \" " #"Ver: {sop_ver} \A \A Page  counter(page) of counter(pages)"
    control_2 = control_1.replace('tr_content', tr_content)
    bc_content = noti # "{noti}"
    control_3 = control_2.replace('bc_content', bc_content)  
    bl_content = "Template: \A Version: " + temp_version + " \A Effective: " + eff 
    # "Template: \A     Version:{temp_version} \A     Effective:{eff}"
    control_4 = control_3.replace('bl_content', bl_content)
    #logo_url = 'pandastable/plugins/elisa_tool_repo/template/Logo.png'
    # or full /path from OS 
    logo_url = './Logo.png'
    control_5 = control_4.replace('logo_url', logo_url)
    css_inset = control_5
    return css_inset
