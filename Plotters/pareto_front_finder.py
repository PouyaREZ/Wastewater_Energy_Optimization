# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 15:21:32 2019

Finding the 2-d Pareto fronts and making the interactive filterable plots on them

@Author: PouyaRZ
"""
import numpy as np
import pandas as pd
import pygmo
from Interactive_SCC_LCC_filter import main


file = np.loadtxt('SDO_LHS_TestRuns288_Constraint_SF_Test.txt', dtype='float')


# Obtaining the Pareto Frontier for the 4 (or any number of set) objectives
#file[:, 25] *= -1 # Overall eff (%) # Converting the first obj to minimization
file[:, 26] /= file[:,38] # LCC/GFA ($/m2) # Normalizing the LCC per the m2 GFA
file[:, 27] /= file[:,38] # CO2/GFA (tonne/m2) # Normalizing the CO2 per the m2 GFA

# 2d Pareto fronts
#pareto_front_Eff_LCC = pygmo.non_dominated_front_2d(file[:, 25:27])
#pareto_front_Eff_CO2 = pygmo.non_dominated_front_2d(file[:, 25:28:2])
pareto_front_LCC_CO2 = pygmo.non_dominated_front_2d(file[:, 26:28])
# 3d Pareto front
#pareto_front_3d = pygmo.select_best_N_mo(file[:, 25:28], 30) # Hideaouly heavy!

# Denegating & denormalizing 
#file[:, 25] *= -1 ## Reverting the negative signs applied to file --> !! applied to TestRuns
file[:, 26] *= file[:,38] # De-normalizing the LCC per the m2 GFA
file[:, 27] *= file[:,38] # De-normalizing the CO2 per the m2 GFA

# All the points
main(file, "LCC_SCC_Filter")

# =============================================================================
# # LCC-tot eff front
# Front1 = file[pareto_front_Eff_LCC]
# np.savetxt("Pareto_front_LCC_Eff.csv", Front1, fmt ='%f', delimiter=',')
# main(Front1, "LCC_vs_Tot_Eff_for_LCC_Tot_Eff_Pareto")
# 
# # Tot eff-CO2 front
# Front2 = file[pareto_front_Eff_CO2]
# np.savetxt("Pareto_front_Eff_CO2.csv", Front2, fmt ='%f', delimiter=',')
# main(Front2, "LCC_vs_Tot_Eff_for_Tot_Eff_CO2_Pareto")
# =============================================================================

# LCC-CO2 front
Front3 = file[pareto_front_LCC_CO2]
np.savetxt("Pareto_front_LCC_SCC.csv", Front3, fmt ='%f', delimiter=',')
main(Front3, "LCC_vs_SCC_for_LCC_SCC_Pareto")