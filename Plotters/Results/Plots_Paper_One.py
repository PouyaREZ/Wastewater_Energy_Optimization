# -*- coding: utf-8 -*-
"""
Created on Fri Feb 4 2020


@Author: PouyaRZ

____________________________________________________
Plots to produce:
1. LCC of equipment for each scenario for all the individuals
2, SCC of equipment for each scenario for all the individuals

3. SCC vs LCC scatter plot.

4. SCC vs chiller type
5. SCC vs CHP type,
6. LCC vs chiller type
7. SCC vs CHP type

8. Traces of building types across all the runs
____________________________________________________

"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def DF_Filter(filename):
    
    file = np.loadtxt(filename, dtype='float')
    
    inputDF = pd.DataFrame(file)
    
    error_tol = 1.15
    
#    print('GFA stats:')
#    print(inputDF.iloc[:,38].describe())
    print('+++++ processing %s +++++\n'%(filename))
    
    print('Count duplicates:')
    condition1 = inputDF.duplicated()==True
    print(inputDF[condition1][38].count())
    
    
    print('Count under the min GFA:') # Count non-trivial neighborhoods
    condition2 = inputDF[38] <= 1/error_tol#<=647497/10
    print(inputDF[condition2][38].count())
    
    
    print('Count over the max GFA:')
    condition3 = inputDF[38]>=647497*5*error_tol
    print(inputDF[condition3][38].count())
    
    
    print('Count over the max Site GFA:')
    condition4 = inputDF[38]/inputDF[36]>=647497*error_tol
    print(inputDF[condition4][38].count())
    
    
    print('Count valid answers:')
    print(len(inputDF) - inputDF[condition1 | condition2 | condition3 | condition4][38].count())
    
#    print('------------------')
    # Filtering the inadmissible results
    Filtered = ~(condition1 | condition2 | condition3 | condition4)
    inputDF = inputDF[Filtered]
    inputDF.reset_index(inplace=True, drop=True)
    
#    print('Annual energy demand stats (MWh):')
    inputDF[26] /= inputDF[38] # Normalizing LCC ($/m2)
    inputDF[27] /= inputDF[38] # Normalizing SCC ($/m2)
    inputDF[39] /= inputDF[38] # Normalizing CO2 (Tonnes/m2)
    inputDF[40] /= (10**3*inputDF[38]) # Normalizing total energy demand (MWh/m2)
    inputDF[41] /= inputDF[38] # Normalizing total wwater treatment demand (L/m2)
    for i in range(29,36): # Converting percent areas to integer %
        inputDF[i] = inputDF[i] * 100
#    print(inputDF[40].describe())
    
    return inputDF
    


### MAIN FUNCTION
print('loading data')
filenames = ['../RQ1_W_CWWTP_ModConsts_Feb17/SDO_LHS_TestRuns288_Constraint_SF_Test.txt',
                 '../RQ1_WO_CWWTP_ModConsts_Feb17/SDO_LHS_TestRuns288_Constraint_SF_Test.txt']
DFNames = ['CCHP|CWWTP','CCHP+WWT']
DFs = {}
for i in range(2):
    DFs[DFNames[i]] = DF_Filter(filenames[i])




plt.style.use('ggplot')
colors_rb = {DFNames[0]:'r', DFNames[1]:'b'}








# =============================================================================
## CHP/Chiller/Solar Types used in the individual neighborhood
CHP_Types = {}
CHP_Types[1] = 'Gas_1'
CHP_Types[2] = 'Gas_2'
CHP_Types[3] = 'Gas_3'
CHP_Types[4] = 'Gas_4'
CHP_Types[5] = 'Gas_5'
CHP_Types[6] = 'Micro_1'
CHP_Types[7] = 'Micro_2'
CHP_Types[8] = 'Micro_3'
CHP_Types[9] = 'Recipro_1'
CHP_Types[10] = 'Recipro_2'
CHP_Types[11] = 'Recipro_3'
CHP_Types[12] = 'Recipro_4'
CHP_Types[13] = 'Recipro_5'
CHP_Types[14] = 'Steam_1'
CHP_Types[15] = 'Steam_2'
CHP_Types[16] = 'Steam_3'
CHP_Types[17] = 'Fuel_Cell_1'
CHP_Types[18] = 'Fuel_Cell_2'
CHP_Types[19] = 'Fuel_Cell_3'
CHP_Types[20] = 'Fuel_Cell_4'
CHP_Types[21] = 'Fuel_Cell_5'
CHP_Types[22] = 'Fuel_Cell_6'
CHP_Types[23] = 'Bio_1'
CHP_Types[24] = 'Bio_2'
CHP_Types[25] = 'Bio_3'
CHP_Types[26] = 'Bio_4'
CHP_Types[27] = 'Bio_5'
CHP_Types[28] = 'Bio_6'
CHP_Types[29] = 'Bio_7'
CHP_Types[30] = 'Bio_8'
CHP_Types[31] = 'Bio_9'
CHP_Types[32] = 'Bio_10'


Chiller_Types = {}
Chiller_Types[1] = 'Electric_1'
Chiller_Types[2] = 'Electric_2'
Chiller_Types[3] = 'Electric_3'
Chiller_Types[4] = 'Electric_4'
Chiller_Types[5] = 'Electric_5'
Chiller_Types[6] = 'Electric_6'
Chiller_Types[7] = 'Electric_7'
Chiller_Types[8] = 'Electric_8'
Chiller_Types[9] = 'Electric_9'
Chiller_Types[10] = 'Absorp_1'
Chiller_Types[11] = 'Absorp_2'
Chiller_Types[12] = 'Absorp_3'
Chiller_Types[13] = 'Absorp_4'
Chiller_Types[14] = 'Absorp_5'
Chiller_Types[15] = 'Absorp_6'
Chiller_Types[16] = 'Absorp_7'
Chiller_Types[17] = 'Absorp_8'


WWT_Types = {}
WWT_Types[1] = "FO_MD"
WWT_Types[2] = "FO_RO"
WWT_Types[3] = "CWWTP"



## CHP, Chiller and WWT name assignments
# CHP = {}
# Chiller = {}
# WWT = {}
for DFName in DFNames:
    # CHP[DFName] = np.array([CHP_Types[int(i)] for i in DFs[DFName][21]]) # Making strings of CHP names instead of integers
    DFs[DFName][21] = np.array([CHP_Types[int(i)] for i in DFs[DFName][21]]) # Making strings of CHP names instead of integers
    # Chiller[DFName] = np.array([Chiller_Types[int(i)] for i in DFs[DFName][22]]) # Making strings of Chiller names instead of integers
    DFs[DFName][22] = np.array([Chiller_Types[int(i)] for i in DFs[DFName][22]]) # Making strings of Chiller names instead of integers
    # WWT[DFName] = np.array([WWT_Types[int(i)] for i in DFs[DFName][24]]) # Making strings of WWT module names instead of integers
    DFs[DFName][24] = np.array([WWT_Types[int(i)] for i in DFs[DFName][24]]) # Making strings of WWT module names instead of integers


# =============================================================================





######################## PLOTS ##########################

#############################################
print('plotting overall LCC and SCC graphs')
# LCC
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=26, ascending=True).reset_index(drop=True)
    plt.scatter(x=sortedDF.index,y=(sortedDF[26]/10**3),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel('Rank')
plt.ylabel(r'LCC (k\$/$m^2$)')
# plt.title('LCC')
plt.legend()
plt.savefig('LCC_Ascending.png', dpi=400, bbox_inches='tight')



# SCC
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=27, ascending=True).reset_index(drop=True)
    plt.scatter(x=sortedDF.index,y=(sortedDF[27]/10**3),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel('Rank')
plt.ylabel(r'SCC (k\$/$m^2$)')
# plt.title('SCC')
plt.legend()
plt.savefig('SCC_Ascending.png', dpi=400, bbox_inches='tight')

plt.close('all')



#############################################
print('plotting LCC and SCC box plots')

print('\n#############################################')
print('Stats of LCC ($/m2) for Disintegrated Case:\n',(DFs[DFNames[0]][26]).describe())
print('Stats of LCC ($/m2) for Integrated Case:\n',(DFs[DFNames[1]][26]).describe())
print('Stats of SCC ($/m2) for Disintegrated Case:\n',(DFs[DFNames[0]][27]).describe())
print('Stats of SCC ($/m2) for Integrated Case:\n',(DFs[DFNames[1]][27]).describe())
print('#############################################\n')

# =============================================================================
# # LCC
# plt.figure(figsize=(10,5))
# # for DFName in DFNames:
# plt.boxplot(x=[(DFs[DFNames[0]][26]/10**3), (DFs[DFNames[1]][26]/10**3)])
# #    (DFs[DFName][0][26]/10**6).plot(label=DFName)
# # plt.xlabel('Rank')
# plt.ylabel(r'LCC (k\$/$m^2$)')
# plt.xticks([1,2],[DFNames[0],DFNames[1]])
# # plt.title('LCC')
# plt.savefig('LCC_Boxplot.png', dpi=400, bbox_inches='tight')
# 
# 
# 
# # SCC
# plt.figure(figsize=(10,5))
# # for DFName in DFNames:
# plt.boxplot(x=[(DFs[DFNames[0]][27]/10**3), (DFs[DFNames[1]][27]/10**3)])
# #    (DFs[DFName][0][26]/10**6).plot(label=DFName)
# # plt.xlabel('Rank')
# plt.ylabel(r'SCC (k\$/$m^2$)')
# plt.xticks([1,2],[DFNames[0],DFNames[1]])
# # plt.title('LCC')
# plt.savefig('SCC_Boxplot.png', dpi=400, bbox_inches='tight')
# 
# plt.close('all')
# =============================================================================


'''
#############################################
print('plotting LCC/SCC vs total neighborhood energy and ww graphs')

print('\n#############################################')
print('Stats of Total Energy Demand (MWh/m2) for Disintegrated Case:\n',(DFs[DFNames[0]][40]).describe())
print('Stats of Total Energy Demand (MWh/m2) for Integrated Case:\n',(DFs[DFNames[1]][40]).describe())
print('Stats of Total Wastewater Treatment Demand (m3/m2) for Disintegrated Case:\n',(DFs[DFNames[0]][41]/10**3).describe())
print('Stats of Total Wastewater Treatment Demand (m3/m2) for Integrated Case:\n',(DFs[DFNames[1]][41]/10**3).describe())
print('#############################################\n')

# LCC vs Neighborhood's Total Energy Use
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=40, ascending=True).reset_index(drop=True)
    plt.scatter(x=(sortedDF[40]),y=(sortedDF[26]/10**3),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel(r'Total Energy Demand (MWh/$m^2$)')
plt.ylabel(r'LCC (k\$/$m^2$)')
# plt.title('LCC')
plt.legend()
plt.savefig('LCC_vs_Energy_Demand.png', dpi=400, bbox_inches='tight')


# LCC vs Neighborhood's Total WWater Demand
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=41, ascending=True).reset_index(drop=True)
    plt.scatter(x=(sortedDF[41]/10**3),y=(sortedDF[26]/10**3),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel(r'Total Wastewater Treatment Demand ($m^3$/$m^2$)')
plt.ylabel(r'LCC (k\$/$m^2$)')
# plt.title('LCC')
plt.legend()
plt.savefig('LCC_vs_WWater_Demand.png', dpi=400, bbox_inches='tight')



# SCC vs Neighborhood's Total Energy Use
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=40, ascending=True).reset_index(drop=True)
    plt.scatter(x=(sortedDF[40]),y=(sortedDF[27]/10**3),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel(r'Total Energy Demand (MWh/$m^2$)')
plt.ylabel(r'SCC (k\$/$m^2$)')
# plt.title('LCC')
plt.legend()
plt.savefig('SCC_vs_Energy_Demand.png', dpi=400, bbox_inches='tight')


# SCC vs Neighborhood's Total WWater Demand
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=41, ascending=True).reset_index(drop=True)
    plt.scatter(x=(sortedDF[41]/10**3),y=(sortedDF[27]/10**3),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel(r'Total Wastewater Treatment Demand ($m^3$/$m^2$)')
plt.ylabel(r'SCC (k\$/$m^2$)')
# plt.title('LCC')
plt.legend()
plt.savefig('SCC_vs_WWater_Demand.png', dpi=400, bbox_inches='tight')

plt.close('all')

#############################################

print('plotting building mix vs neighborhood energy and ww graphs')

# Building Mix vs Neighborhood's Total WWater Demand (integrated)
DFName = 'CCHP+WWT'
bldg_types = ['Res','Off','Com','Ind','Hos','Med','Edu']
colors = ['m','b','c','g','y','orange','r']
columns = list(range(29,36))
plt.figure(figsize=(10,5))
sortedDF = DFs[DFName].sort_values(by=41, ascending=True).reset_index(drop=True)
for i in range(len(bldg_types)):
    plt.scatter(x=(sortedDF[41]/10**3),y=DFs[DFName].iloc[:,columns[i]],
                s=0.5, label=bldg_types[i], c=colors[i], alpha=0.5)
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel(r'Total Wastewater Treatment Demand ($m^3$/$m^2$)')
plt.ylabel('Percent of Total GFA (%)')
plt.ylim(0, 100)
plt.xlim(0,11)
# plt.title('LCC')
plt.legend()
plt.savefig('Bldg_Mix_vs_WWater_Demand_Integ.png', dpi=400, bbox_inches='tight')



# Building Mix vs Neighborhood's Total WWater Demand (Disintegrated)
DFName = 'CCHP|CWWTP'
bldg_types = ['Res','Off','Com','Ind','Hos','Med','Edu']
colors = ['m','b','c','g','y','orange','r']
columns = list(range(29,36))
plt.figure(figsize=(10,5))
sortedDF = DFs[DFName].sort_values(by=41, ascending=True).reset_index(drop=True)
for i in range(len(bldg_types)):
    plt.scatter(x=(sortedDF[41]/10**3),y=DFs[DFName].iloc[:,columns[i]],
                s=0.5, label=bldg_types[i], c=colors[i], alpha=0.5)
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel(r'Total Wastewater Treatment Demand ($m^3$/$m^2$)')
plt.ylabel('Percent of Total GFA (%)')
# plt.title('LCC')
plt.ylim(0, 100)
plt.xlim(0,11)
plt.legend()
plt.savefig('Bldg_Mix_vs_WWater_Demand_Disinteg.png', dpi=400, bbox_inches='tight')




# Building Mix vs Neighborhood's Total Energy Demand (integrated)
DFName = 'CCHP+WWT'
bldg_types = ['Res','Off','Com','Ind','Hos','Med','Edu']
colors = ['m','b','c','g','y','orange','r']
columns = list(range(29,36))
plt.figure(figsize=(10,5))
sortedDF = DFs[DFName].sort_values(by=40, ascending=True).reset_index(drop=True)
for i in range(len(bldg_types)):
    plt.scatter(x=(sortedDF[40]),y=DFs[DFName].iloc[:,columns[i]],
                s=0.5, label=bldg_types[i], c=colors[i], alpha=0.5)
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel(r'Total Energy Demand (MWh/$m^2$)')
plt.ylabel('Percent of Total GFA (%)')
# plt.title('LCC')
plt.ylim(0, 100)
plt.xlim(0,1)
plt.legend()
plt.savefig('Bldg_Mix_vs_Energy_Demand_Integ.png', dpi=400, bbox_inches='tight')



# Building Mix vs Neighborhood's Total Energy Demand (Disintegrated)
DFName = 'CCHP|CWWTP'
bldg_types = ['Res','Off','Com','Ind','Hos','Med','Edu']
colors = ['m','b','c','g','y','orange','r']
columns = list(range(29,36))
plt.figure(figsize=(10,5))
sortedDF = DFs[DFName].sort_values(by=40, ascending=True).reset_index(drop=True)
for i in range(len(bldg_types)):
    plt.scatter(x=(sortedDF[40]),y=DFs[DFName].iloc[:,columns[i]],
                s=0.5, label=bldg_types[i], c=colors[i], alpha=0.5)
#    (DFs[DFName][0][26]/10**6).plot(label=DFName)
plt.xlabel(r'Total Energy Demand (MWh/$m^2$)')
plt.ylabel('Percent of Total GFA (%)')
# plt.title('LCC')
plt.ylim(0, 100)
plt.xlim(0,1)
plt.legend()
plt.savefig('Bldg_Mix_vs_Energy_Demand_Disinteg.png', dpi=400, bbox_inches='tight')

plt.close('all')

#############################################
print('plotting Supply type vs total neighborhood energy and ww graphs')

# Total Energy Demand vs CHP
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=40, ascending=True).reset_index(drop=True)
    plt.scatter(x=DFs[DFName][21],y=(sortedDF[40]),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
plt.xlabel(r'CHP Type')
plt.ylabel(r'Total Energy Demand (MWh/$m^2$)')
plt.legend()
plt.savefig('Total_Energy_vs_CHP.png', dpi=400, bbox_inches='tight')


# Total WWater Demand vs CHP
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=41, ascending=True).reset_index(drop=True)
    plt.scatter(x=DFs[DFName][21],y=(sortedDF[41]/10**3),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
plt.xlabel(r'CHP Type')
plt.ylabel(r'Total Wastewater Treatment Demand ($m^3$/$m^2$)')
plt.legend()
plt.savefig('Total_WWater_vs_CHP.png', dpi=400, bbox_inches='tight')


# Total Energy Demand vs Chiller
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=40, ascending=True).reset_index(drop=True)
    plt.scatter(x=DFs[DFName][22],y=(sortedDF[40]),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
plt.xlabel(r'Chiller Type')
plt.ylabel(r'Total Energy Demand (MWh/$m^2$)')
plt.legend()
plt.savefig('Total_Energy_vs_Chiller.png', dpi=400, bbox_inches='tight')


# Total WWater Demand vs Chiller
plt.figure(figsize=(10,5))
for DFName in DFNames:
    sortedDF = DFs[DFName].sort_values(by=41, ascending=True).reset_index(drop=True)
    plt.scatter(x=DFs[DFName][22],y=(sortedDF[41]/10**3),label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
plt.xlabel(r'Chiller Type')
plt.ylabel(r'Total Wastewater Treatment Demand ($m^3$/$m^2$)')
plt.legend()
plt.savefig('Total_WWater_vs_Chiller.png', dpi=400, bbox_inches='tight')


# Total Energy Demand vs WWT (integrated)
plt.figure(figsize=(10,5))
DFName = 'CCHP+WWT'
sortedDF = DFs[DFName].sort_values(by=40, ascending=True).reset_index(drop=True)
plt.scatter(x=DFs[DFName][24],y=(sortedDF[40]),s=2, c=colors_rb[DFName])
plt.xlabel(r'WWT Type')
plt.ylabel(r'Total Energy Demand (MWh/$m^2$)')
plt.legend()
plt.savefig('Total_Energy_vs_WWT_Integ.png', dpi=400, bbox_inches='tight')


# Total WWater Demand vs WWT (integrated)
plt.figure(figsize=(10,5))
DFName = 'CCHP+WWT'
sortedDF = DFs[DFName].sort_values(by=41, ascending=True).reset_index(drop=True)
plt.scatter(x=DFs[DFName][24],y=(sortedDF[41]/10**3), s=2, c=colors_rb[DFName])
plt.xlabel(r'WWT Type')
plt.ylabel(r'Total Wastewater Treatment Demand ($m^3$/$m^2$)')
plt.savefig('Total_Wwater_vs_WWT_Integ.png', dpi=400, bbox_inches='tight')
'''
plt.close('all')

#############################################
print('plotting pareto fronts')

# LCC vs CO2
plt.figure(figsize=(10,5))
for DFName in DFNames:
    plt.scatter(x=DFs[DFName][26]/10**3,y=DFs[DFName][39],label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
plt.xlabel(r'LCC (k\$/$m^2$)')
plt.ylabel(r'Lifecycle $CO_{2e}$ (T/$m^2$)')
plt.legend()
plt.savefig('CO2_vs_LCC.png', dpi=400, bbox_inches='tight')




#############################################

# LCC vs SCC
plt.figure(figsize=(10,5))
for DFName in DFNames:
    plt.scatter(x=DFs[DFName][26]/10**3,y=DFs[DFName][27]/10**3,label=DFName, s=2, alpha=0.5, c=colors_rb[DFName])
plt.xlabel(r'LCC (k\$/$m^2$)')
plt.ylabel(r'SCC (k\$/$m^2$)')
plt.legend()
plt.savefig('SCC_vs_LCC.png', dpi=400, bbox_inches='tight')


# LCC vs SCC w Generation-based transparency
plt.figure(figsize=(10,5))
for DFName in DFNames:
    alphas = np.linspace(0.1, 1, len(DFs[DFName]))
    rgba_colors = np.zeros((len(DFs[DFName]),4))
    if DFName == DFNames[0]:
        rgba_colors[:,0] = 1.0 # red
    else:
        rgba_colors[:,2] = 1.0 # blue
    rgba_colors[:,3] = alphas
    plt.scatter(x=DFs[DFName][26]/10**3,y=DFs[DFName][27]/10**3,label=DFName, s=1, c=rgba_colors)
plt.xlabel(r'LCC (k\$/$m^2$)')
plt.ylabel(r'SCC (k\$/$m^2$)')
plt.legend()
plt.savefig('SCC_vs_LCC_Gen_Colorcoded.png', dpi=400, bbox_inches='tight')


# LCC vs SCC w Generation-based transparency and elite-filtered
plt.figure(figsize=(10,5))
for DFName in DFNames:
    DF = DFs[DFName][DFs[DFName][26]/10**3 <= 500]
    DF = DF[DFs[DFName][27]/10**3 <= 0.1]
    alphas = np.linspace(0.1, 1, len(DF))
    rgba_colors = np.zeros((len(DF),4))
    if DFName == DFNames[0]:
        rgba_colors[:,0] = 1.0 # red
    else:
        rgba_colors[:,2] = 1.0 # blue
    rgba_colors[:,3] = alphas
    plt.scatter(x=DF[26]/10**3,y=DF[27]/10**3,label=DFName, s=1, c=rgba_colors)
plt.xlabel(r'LCC (k\$/$m^2$)')
plt.ylabel(r'SCC (k\$/$m^2$)')
plt.legend()
plt.savefig('SCC_vs_LCC_Gen_Colorcoded_Filtered.png', dpi=400, bbox_inches='tight')


# =============================================================================
# # LCC vs SCC (integrated)
# plt.figure(figsize=(10,5))
# DFName = 'CCHP+WWT'
# plt.scatter(x=DFs[DFName][26]/10**3,y=DFs[DFName][27]/10**3, s=2)
# plt.xlabel(r'LCC (k\$/$m^2$)')
# plt.ylabel(r'SCC (k\$/$m^2$)')
# plt.savefig('SCC_vs_LCC_Integ.png', dpi=400, bbox_inches='tight')
# 
# 
# # LCC vs SCC (disintegrated)
# plt.figure(figsize=(10,5))
# DFName = 'CCHP|CWWTP'
# plt.scatter(x=DFs[DFName][26]/10**3,y=DFs[DFName][27]/10**3, s=2)
# #    (DFs[DFName][0][26]/10**6).plot(label=DFName)
# plt.xlabel(r'LCC (k\$/$m^2$)')
# plt.ylabel(r'SCC (k\$/$m^2$)')
# # plt.title('LCC')
# plt.savefig('SCC_vs_LCC_Disinteg.png', dpi=400, bbox_inches='tight')
# 
# =============================================================================

#############################################
print('plotting Supply type vs opt objectives')


print('\n#############################################')
Disinteg_Grpd_by_CHP_meanLCC = DFs[DFNames[0]].groupby(21)[26].mean()
Disnteg_Grpd_by_CHP_medLCC = DFs[DFNames[0]].groupby(21)[26].median()
Disnteg_Grpd_by_CHP_meanSCC = DFs[DFNames[0]].groupby(21)[27].mean()
Disnteg_Grpd_by_CHP_medSCC = DFs[DFNames[0]].groupby(21)[27].median()
Integ_Grpd_by_CHP_meanLCC = DFs[DFNames[1]].groupby(21)[26].mean()
Integ_Grpd_by_CHP_medLCC = DFs[DFNames[1]].groupby(21)[26].median()
Integ_Grpd_by_CHP_meanSCC = DFs[DFNames[1]].groupby(21)[27].mean()
Integ_Grpd_by_CHP_medSCC = DFs[DFNames[1]].groupby(21)[27].median()
items = [Disinteg_Grpd_by_CHP_meanLCC, Disnteg_Grpd_by_CHP_medLCC, Disnteg_Grpd_by_CHP_meanSCC,
 Disnteg_Grpd_by_CHP_medSCC, Integ_Grpd_by_CHP_meanLCC, Integ_Grpd_by_CHP_medLCC,
 Integ_Grpd_by_CHP_meanSCC, Integ_Grpd_by_CHP_medSCC]
items_names = ['Disinteg_Grpd_by_CHP_meanLCC', 'Disnteg_Grpd_by_CHP_medLCC', 'Disnteg_Grpd_by_CHP_meanSCC',
 'Disnteg_Grpd_by_CHP_medSCC', 'Integ_Grpd_by_CHP_meanLCC', 'Integ_Grpd_by_CHP_medLCC',
 'Integ_Grpd_by_CHP_meanSCC', 'Integ_Grpd_by_CHP_medSCC']
for i in range(len(items)):
    print(items_names[i], items[i])
print('#############################################\n')



# shapes = {DFNames[0]: '+', DFNames[1]: 'x'}


# LCC vs CHP
for DFName in DFNames:
    plt.figure(figsize=(10,5))
    DF = DFs[DFName].sort_values(by=21)
    plt.scatter(x=DF[21], y=DF[26]/10**3,label=DFName, s=2, alpha=0.5)#, c=colors_rb[DFName])#, marker=shapes[DFName])
    plt.xlabel(r'CHP Type')
    plt.xticks(rotation=75)
    plt.ylabel(r'LCC (k\$/$m^2$)')
    plt.ylim(-5, 500)
    # plt.legend()
    if DFName == 'CCHP|CWWTP':
        plt.savefig('LCC_vs_CHP_disinteg.png', dpi=400, bbox_inches='tight')
    else:
        plt.savefig('LCC_vs_CHP_integ.png', dpi=400, bbox_inches='tight')


# SCC vs CHP
for DFName in DFNames:
    plt.figure(figsize=(10,5))
    DF = DFs[DFName].sort_values(by=21)
    plt.scatter(x=DF[21], y=DF[27]/10**3,label=DFName, s=2, alpha=0.5)#, c=colors_rb[DFName])
    plt.xlabel(r'CHP Type')
    plt.xticks(rotation=75)
    plt.ylabel(r'SCC (k\$/$m^2$)')
    plt.ylim(-0.01, 0.1)
    # plt.legend()
    if DFName == 'CCHP|CWWTP':
        plt.savefig('SCC_vs_CHP_disinteg.png', dpi=400, bbox_inches='tight')
    else:
        plt.savefig('SCC_vs_CHP_integ.png', dpi=400, bbox_inches='tight')


# SCC vs CHP with LCC-oriented transparency
for DFName in DFNames:
    plt.figure(figsize=(10,5))
    DF = DFs[DFName].sort_values(by=21)
    DF = DF[(DF[26]<=100) & (DF[27]<=100)]
    print('number of indivs plotted: ', len(DF))
    alphas = 1.2 - DF[26]/DF[26].max() # Normalized LCCs (lowest LCC: 1; highest LCC: 0)
    # alphas = np.linspace(0.1, 1, len(DFs[DFName]))
    rgba_colors = np.zeros((len(DF),4))
    rgba_colors[:,3] = alphas
    plt.scatter(x=DF[21],y=DF[27]/10**3,label=DFName, s=1, c=rgba_colors)
    plt.xlabel(r'CHP Type')
    plt.xticks(rotation=75)
    plt.ylabel(r'SCC (k\$/$m^2$)')
    plt.ylim(-0.01, 0.1)
    # plt.legend()
    if DFName == 'CCHP|CWWTP':
        plt.savefig('SCC_vs_CHP_disinteg_colorCoded.png', dpi=400, bbox_inches='tight')
    else:
        plt.savefig('SCC_vs_CHP_integ_colorCoded.png', dpi=400, bbox_inches='tight')
        
    

# =============================================================================
# # LCC vs CHP (integrated)
# plt.figure(figsize=(10,5))
# DFName = 'CCHP+WWT'
# plt.scatter(x=DFs[DFName][21], y=DFs[DFName][26]/10**3, s=2)
# plt.xlabel(r'CHP Type')
# plt.ylabel(r'LCC (k\$/$m^2$)')
# plt.savefig('LCC_vs_CHP_Integ.png', dpi=400, bbox_inches='tight')
# 
# 
# # LCC vs CHP (disintegrated)
# plt.figure(figsize=(10,5))
# DFName = 'CCHP|CWWTP'
# plt.scatter(x=DFs[DFName][21], y=DFs[DFName][26]/10**3, s=2)
# plt.xlabel(r'CHP Type')
# plt.ylabel(r'LCC (k\$/$m^2$)')
# plt.savefig('LCC_vs_CHP_Disinteg.png', dpi=400, bbox_inches='tight')
# =============================================================================



# LCC vs Chiller
for DFName in DFNames:
    plt.figure(figsize=(10,5))
    DF = DFs[DFName].sort_values(by=22)
    plt.scatter(x=DF[22], y=DF[26]/10**3,label=DFName, s=2, alpha=0.5)#, c=colors_rb[DFName])
    plt.xlabel(r'Chiller Type')
    plt.xticks(rotation=75)
    plt.ylabel(r'LCC (k\$/$m^2$)')
    plt.ylim(-5, 500)
    # plt.legend()
    if DFName == 'CCHP|CWWTP':
        plt.savefig('LCC_vs_Chiller_disinteg.png', dpi=400, bbox_inches='tight')
    else:
        plt.savefig('LCC_vs_Chiller_integ.png', dpi=400, bbox_inches='tight')


# SCC vs Chiller
for DFName in DFNames:
    plt.figure(figsize=(10,5))
    DF = DFs[DFName].sort_values(by=22)
    plt.scatter(x=DF[22], y=DF[27]/10**3,label=DFName, s=2, alpha=0.5)#, c=colors_rb[DFName])
    plt.xlabel(r'Chiller Type')
    plt.xticks(rotation=75)
    plt.ylabel(r'SCC (k\$/$m^2$)')
    plt.ylim(-0.01, 0.1)
    # plt.legend()
    if DFName == 'CCHP|CWWTP':
        plt.savefig('SCC_vs_Chiller_disinteg.png', dpi=400, bbox_inches='tight')
    else:
        plt.savefig('SCC_vs_Chiller_integ.png', dpi=400, bbox_inches='tight')
        
        
# SCC vs Chiller with LCC-oriented transparency
for DFName in DFNames:
    plt.figure(figsize=(10,5))
    DF = DFs[DFName].sort_values(by=22)
    DF = DF[(DF[26]<=100) & (DF[27]<=0.5)]
    print('number of indivs plotted: ', len(DF))
    alphas = 1 - DF[26]/DF[26].max() # Normalized LCCs (lowest LCC: 1; highest LCC: 0)
    # alphas = np.linspace(0.1, 1, len(DFs[DFName]))
    rgba_colors = np.zeros((len(DF),4))
    rgba_colors[:,3] = alphas
    plt.scatter(x=DF[22],y=DF[27]/10**3,label=DFName, s=1, c=rgba_colors)
    plt.xlabel(r'Chiller Type')
    plt.xticks(rotation=75)
    plt.ylabel(r'SCC (k\$/$m^2$)')
    plt.ylim(-0.01, 0.1)
    # plt.legend()
    if DFName == 'CCHP|CWWTP':
        plt.savefig('SCC_vs_Chiller_disinteg_colorCoded.png', dpi=400, bbox_inches='tight')
    else:
        plt.savefig('SCC_vs_Chiller_integ_colorCoded.png', dpi=400, bbox_inches='tight')



# =============================================================================
# # LCC vs Chiller (integrated)
# plt.figure(figsize=(10,5))
# DFName = 'CCHP+WWT'
# plt.scatter(x=DFs[DFName][22], y=DFs[DFName][26]/10**3, s=2)
# plt.xlabel(r'Chiller Type')
# plt.ylabel(r'LCC (k\$/$m^2$)')
# plt.savefig('LCC_vs_Chiller_Integ.png', dpi=400, bbox_inches='tight')
# 
# 
# # LCC vs Chiller (disintegrated)
# plt.figure(figsize=(10,5))
# DFName = 'CCHP|CWWTP'
# plt.scatter(x=DFs[DFName][22], y=DFs[DFName][26]/10**3, s=2)
# plt.xlabel(r'Chiller Type')
# plt.ylabel(r'LCC (k\$/$m^2$)')
# plt.savefig('LCC_vs_Chiller_Disinteg.png', dpi=400, bbox_inches='tight')
# =============================================================================



# LCC vs WWT (integrated)
plt.figure(figsize=(10,5))
DFName = 'CCHP+WWT'
DF = DFs[DFName].sort_values(by=24)
plt.scatter(x=DF[24], y=DF[26]/10**3, s=2)#, c=colors_rb[DFName])
plt.xlabel(r'WWT Type')
plt.xticks(rotation=75)
plt.ylabel(r'LCC (k\$/$m^2$)')
plt.ylim(-5, 500)
plt.savefig('LCC_vs_WWT_Integ.png', dpi=400, bbox_inches='tight')



# SCC vs WWT (integrated)
plt.figure(figsize=(10,5))
DFName = 'CCHP+WWT'
DF = DFs[DFName].sort_values(by=24)
plt.scatter(x=DF[24], y=DF[27]/10**3, s=2)#, c=colors_rb[DFName])
plt.xlabel(r'WWT Type')
plt.xticks(rotation=75)
plt.ylabel(r'SCC (k\$/$m^2$)')
plt.ylim(-0.01, 0.1)
plt.savefig('SCC_vs_WWT_Integ.png', dpi=400, bbox_inches='tight')



# SCC vs WWT with LCC-oriented transparency  (integrated)
plt.figure(figsize=(10,5))
DFName = 'CCHP+WWT'
DF = DFs[DFName].sort_values(by=24)
DF = DF[(DF[26]<=100) & (DF[27]<=0.5)]
print('number of indivs plotted: ', len(DF))
alphas = 1 - DF[26]/DF[26].max() # Normalized LCCs (lowest LCC: 1; highest LCC: 0)
# alphas = np.linspace(0.1, 1, len(DFs[DFName]))
rgba_colors = np.zeros((len(DF),4))
rgba_colors[:,3] = alphas
plt.scatter(x=DF[24],y=DF[27]/10**3,s=1, c=rgba_colors)
plt.xlabel(r'WWT Type')
plt.xticks(rotation=75)
plt.ylabel(r'SCC (k\$/$m^2$)')
plt.ylim(-0.01, 0.1)
plt.savefig('SCC_vs_WWT_Integ_colorCoded.png', dpi=400, bbox_inches='tight')

plt.close('all')

#############################################
'''
print('plotting building mix traces')

# Building Mix trace plots
DFName = 'CCHP+WWT'
plt.figure(figsize=(10,5))
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
Num_Individuals = len(DFs[DFName])
cm = plt.get_cmap('rainbow')
ax.set_prop_cycle(color=[cm(1.*i/Num_Individuals) for i in range(Num_Individuals)])#ax.set_color_cycle([cm(1.*i/Num_Individuals) for i in range(Num_Individuals)])
for i in range(Num_Individuals):
    ax.plot(['Res','Off','Com','Ind','Hos','Med','Edu'],
            DFs[DFName].iloc[i,29:36],linewidth=0.2, alpha=0.5)
ax.set_xlabel('Building-Use')
ax.set_ylabel('Percent of Total GFA (%)')
plt.ylim(0, 100)
fig.savefig('Uses_Integ.png', dpi=400, bbox_inches='tight')




DFName = 'CCHP|CWWTP'
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
Num_Individuals = len(DFs[DFName])
cm = plt.get_cmap('rainbow')
ax.set_prop_cycle(color=[cm(1.*i/Num_Individuals) for i in range(Num_Individuals)])#ax.set_color_cycle([cm(1.*i/Num_Individuals) for i in range(Num_Individuals)])
y_array = np.array(DFs[DFName].iloc[:,29:36])
for i in range(Num_Individuals):
    ax.plot(['Res','Off','Com','Ind','Hos','Med','Edu'],
            DFs[DFName].iloc[i,29:36],linewidth=0.2, alpha=0.5)
ax.set_xlabel('Building-Use')
ax.set_ylabel('Percent of Total GFA (%)')
plt.ylim(0, 100)
fig.savefig('Uses_Disinteg.png', dpi=400, bbox_inches='tight')
plt.close('all')
'''
