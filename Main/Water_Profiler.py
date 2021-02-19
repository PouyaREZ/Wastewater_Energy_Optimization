# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 07:42:51 2018

Module for reading in the water consumption profiles and creating the 8760 hours

Input: Profiles.csv
        1st line: avg monthly use (gal/d)
        2nd line: monthly variations
        Bottom-most lines: 24 hr variations
    
Output: A dictionary of 21 building types and their annual water use profiles
        in lit per each hour

@Author: PouyaRZ
"""

## Constants
gal_to_lit = 3.78541
# W_to_WW = 0.96 # http://www.ct.gov/deep/lib/deep/water_regulating_and_discharges/subsurface/2006designmanual/completesec_3.pdf
W_to_WW = 1 # Conservatively assumed so
#WW_to_GW = 0.4 # Overview of Greywater Reuse: The Potential of Greywater Systems to Aid Sustainable Water Management


from pandas import read_csv
# =============================================================================
# from matplotlib import pyplot as plt
# 
# =============================================================================


# =============================================================================
# Month_hours_cumul = [744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296,
#                      8016, 8760]
# Month_hours_indiv = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
# =============================================================================
Month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def Water_Demand():
    input_file = read_csv('Profiles.csv', index_col = 0, header = 0)
    
    Avg_Use = input_file.iloc[0,:]*gal_to_lit*W_to_WW#*WW_to_GW # Avg daily WW production in lit
    Monthly_Coeffs = input_file.iloc[1:13,:] # Monthly variations
    Hourly_Coeffs = input_file.iloc[13:37,:] # Hourly variations
    
    
    Num_Buildings = len(Monthly_Coeffs.columns[:])
    
    Annl_Use = {}
    
    for i in range(Num_Buildings):
        for j in range(len(Monthly_Coeffs)):
            Num_days = Month_days[j]
            if (i+1) in Annl_Use.keys():
                Annl_Use[i+1].extend(list(Avg_Use[i] * Monthly_Coeffs.iloc[j,i]
                * Hourly_Coeffs.iloc[:,i]) * Num_days)
            else:
                Annl_Use[i+1] = (list(Avg_Use[i] * Monthly_Coeffs.iloc[j,i]
                * Hourly_Coeffs.iloc[:,i]) * Num_days)
    return Annl_Use
            
        
# =============================================================================
# names = list(input_file.columns[:])
# 
# plt.figure(figsize=(14, 34))
# plt.style.use('ggplot')
# for i in range(21):
#     plt.subplot(7,3,i+1)
#     plt.plot(range(8760),Annl_Use[i+1])
#     plt.title(names[i], size = 5)
#     plt.xlabel('Time (hr)', fontsize = 5)
#     plt.ylabel('Water Use (lit)', fontsize = 5)
#     plt.xticks(fontsize = 5)
#     plt.yticks(fontsize = 5)
# plt.savefig('Annual Water Consumptions.svg', dpi = 100, bbox_inches = 'tight')
# 
# plt.figure(figsize=(14, 34))
# plt.style.use('ggplot')
# for i in range(21):
#     plt.subplot(7,3,i+1)
#     plt.plot(range(24),Annl_Use[i+1][0:24])
#     plt.title(names[i], size = 5)
#     plt.xlabel('Time (hr)', fontsize = 5)
#     plt.ylabel('Water Use (lit)', fontsize = 5)
#     plt.xticks(fontsize = 5)
#     plt.yticks(fontsize = 5)
# plt.savefig('Annual Water Consumptions_24hrs.svg', dpi = 100, bbox_inches = 'tight', font = 10)
# =============================================================================
