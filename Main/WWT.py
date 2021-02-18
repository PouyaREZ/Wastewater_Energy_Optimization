# -*- coding: utf-8 -*-
"""
Created by PRK
Created on Tue Jan 22 22:27:44 2019
Updated on Mon Feb 17 2020


Wastewater treatment module for returning the required electricity and heat
Assuming 100% GW treatment

## No timelag in treatment included yet, assumed the input hourly gw is treated within the hour

## Recovery ratios are not considered yet!

## Membrane areas are calculated in vain for now

## Capex and Opex are calculated for maximum daily inflow

@Author: PouyaRZ
"""

import numpy as np

Liter_to_Galon = 0.264172
Liter_to_M3 = 1/1000
kWh_to_Btu = 3412                   # Conversion of kWh to Btu
MJ_to_kWh = 1/3.6
MT_to_lbs = 2204.62                 # Conversion of metric tonnes to lbs

Desalin_to_WWT = 1/2 # Should be applied to both capex and opex # From Desalinated versus recycled water — public perceptions and profiles of the accepters @ "D:\PhD\+Main Research Directory\W&WW\+ Power Consumption Desalin vs Reclamat+public's attitude" --> Maked with "Used"
With_Power_Cost_to_No_Power_Cost = 1-0.33 # Should be applied to both the capex and opex (as it's for modifying the total LCA, not just operation) # From ibid.
UV_Electrical_Consumption = 0.01 # kWh/m3 # From CostTemplate from SelWTP
Kelvin = lambda temp : 273.15 + temp
Dyn_Visc = lambda temp : np.exp(-3.7188 + 578.919 / (-137.546 + Kelvin(temp))) # Dynamic viscosity of water Vogel Eq'n [refer to Design Criteria for wastewater treatment Module.docx]

USD_2007_To_2019 = 1.23 # from http://www.in2013dollars.com/us/inflation/2007
USD_2015_To_2019 = 1.08 # from http://www.in2013dollars.com/us/inflation/2015


def Mean_24_hr(arr): # Double-checked: performing all right
    arr_temp = np.cumsum(arr, dtype=float)
    arr_temp[24:] = arr_temp[24:] - arr_temp[:-24]
    return np.average(arr_temp[24 - 1:])

#def Max_24_hr_Avg(arr): # Double-checked: performing all right
#    arr_temp = np.cumsum(arr, dtype=float)
#    arr_temp[24:] = arr_temp[24:] - arr_temp[:-24]
#    return np.max(arr_temp[24 - 1:])/24

def Hourly_24_hr(arr): # 24-hour mean supply # Double-checked: performing all right
    arr_temp = np.cumsum(arr, dtype=float)
    arr_temp[24:] = arr_temp[24:] - arr_temp[:-24]
    return arr_temp/24


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


def FO_RO(Hourly_WW_Supply, Hourly_Temp): ## PROBLEM: USING THE AMBIENT TEMPERATURE AS THAT OF THE GRAYWATER--> MIGHT NEED MODIFICATION

    # Constants
    WWT_Electric_Demand = 1.02 * (0.0102*Kelvin(Hourly_Temp) + 0.28) # kWh/m3 # From Design Criteria for Wastewater Treatment Module.docx located at "D:\PhD\+Main Research Directory\W&WW\!!! My Materials\Designing WWT Module+formulae+software+commercial"
    WWT_Heat_Demand = 0 # kWh/m3
    WWT_Recovery_Rate = 0.5 # From Design Criteria for Wastewater Treatment Module.docx located at "D:\PhD\+Main Research Directory\W&WW\!!! My Materials\Designing WWT Module+formulae+software+commercial"
    Unit_Cost_FO = 1500 # IN 2015 USD # $/unit from LCC of a hybrid FO-LPRO system for seawater desal & recovery @ "D:\PhD\+Main Research Directory\W&WW\++ LCC & LCA"
    Unit_Area_FO = 27 # m2
    Unit_Cost_RO = 675 # IN 2015 USD # $/unit from Ibid.
    Unit_Area_RO = 34 # m2
    Membrane_Cost_To_EPC = 100/19.6 # 19.6% of EPC cost is for the membrane # From Ibid.
    
    # Calculations
    Mean_24_Hourly_Supply = Hourly_24_hr(Hourly_WW_Supply) # in L/hour # ASSUMING 24-HOUR STORAGE
    Mu_m = Dyn_Visc(Hourly_Temp)
    # Mem_Area_FO = np.max(Hourly_WW_Supply * Mu_m / Kelvin(Hourly_Temp))/0.0121 # in m2
    # Mem_Area_RO = np.max(Hourly_WW_Supply * Mu_m / Kelvin(Hourly_Temp))/0.0229 # in m2
    Mem_Area_FO = np.max(Mean_24_Hourly_Supply * Mu_m / Kelvin(Hourly_Temp))/0.0121 # in m2
    Mem_Area_RO = np.max(Mean_24_Hourly_Supply * Mu_m / Kelvin(Hourly_Temp))/0.0229 # in m2
    WWT_Capex = (np.floor(Mem_Area_FO/Unit_Area_FO)*Unit_Cost_FO + np.floor(Mem_Area_RO/Unit_Area_RO)*Unit_Cost_RO)*Membrane_Cost_To_EPC*Desalin_to_WWT * USD_2015_To_2019 # in 2019 $
    
    
    Mean_24_Supply = Mean_24_hr(Hourly_WW_Supply) # in L/day
#    WWT_Capex = (1+0.21) * 10**6 * 9.3423 * (Max_24_Supply * Liter_to_Galon / 10**6)**0.7177 * USD_2007_To_2019 # in 2019 $/year ## THAT OF RO IS USED from P.103 from Cost_Estimate Water Treatment Facility (the "total construction cost") located at ibid. ## The correction factor in the beginning is for SWRO to FO-LPRO from the abstract of "LCC of a hybrid FO system for..." located @ "D:\PhD\+Main Research Directory\W&WW\++ LCC & LCA"
    WWT_Opex = (1-0.56) * 10**6 * 2.9129 * (Mean_24_Supply * Liter_to_Galon / 10**6)**0.6484 * USD_2007_To_2019 # 2019 $/year ## P.103 from Cost_Estimate Water Treatment Facility (the "total construction cost") located at"D:\PhD\+Main Research Directory\W&WW\++ LCC & LCA" ## The correction factor in the beginning is for SWRO to FO-LPRO from the abstract of "LCC of a hybrid FO system for..." located @ "D:\PhD\+Main Research Directory\W&WW\++ LCC & LCA"
#    WRONG FORMULA: Don't calculate the opex based on hourly inputs, they badly overestimate the annual cost # WWT_Opex = np.sum(1/365*(10**6 * 0.686 * (Hourly_WW_Supply * 24 * Liter_to_Galon / 10**6)**0.638)) * USD_2007_To_2019 # in 2019 $/year ## 


    # Heat_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Heat_Demand
    # Electric_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Electric_Demand
    Heat_Demand_Total = Mean_24_Hourly_Supply * Liter_to_M3 * WWT_Heat_Demand
    Electric_Demand_Total = Mean_24_Hourly_Supply * Liter_to_M3 * WWT_Electric_Demand
    
    WWT_Opex_Total = WWT_Opex * Desalin_to_WWT * With_Power_Cost_to_No_Power_Cost # Annual # Don't use hourly graywater and multiplying it by 24 then dividing the result by 365, it badly overshoots the OPEX
    WWT_Capex_Total = WWT_Capex # Annual # The correction factors are acting on the WWT_Capex in this case as the value was extracted from a paper and not from the cost estimation handbook
    
   
    return [Electric_Demand_Total, Heat_Demand_Total, WWT_Opex_Total, WWT_Capex_Total]




def FO_MD(Hourly_WW_Supply, Hourly_Temp): ## Note: Volumetric weight of water considered a con't: 1kg/L; Atmospheric pressure considered constant: 101325 Pa
    
    # Constants
    WWT_Electric_Demand = 0.55 # kWh/m3 # From Design Criteria for Wastewater Treatment Module.docx located at "D:\PhD\+Main Research Directory\W&WW\!!! My Materials\Designing WWT Module+formulae+software+commercial"
    WWT_Recovery_Rate = 0.5 # From Design Criteria for Wastewater Treatment Module.docx located at "D:\PhD\+Main Research Directory\W&WW\!!! My Materials\Designing WWT Module+formulae+software+commercial"
    Unit_Cost_FO = 1500 # IN 2015 USD # $/unit from LCC of a hybrid FO-LPRO system for seawater desal & recovery @ "D:\PhD\+Main Research Directory\W&WW\++ LCC & LCA"
    Unit_Area_FO = 27 # m2
    Unit_Cost_MD = 60 # IN 2015 USD # $/unit from Tavakkoli et al. 2017
    Unit_Area_MD = 1 # m2
    Membrane_Cost_To_EPC_FO_MD = 1.81 # from Al-Obaidani et al. 2008 (look at the Design Criteria for Wastewater Treatment Module document)
    Membrane_Cost_To_Operation_FO_MD = 1.28 # from Al-Obaidani
    Membrane_Cost_To_Replacement_Cost = 0.15 # from Al-Obaidani et al. 2008
    
    
    Mole_Fraction_H2O_in_Feed = 0.99954
    
    ### Calculations
    Mu_m = Dyn_Visc(Hourly_Temp)
    
    # Delta P (FO draw - MD permeate) & Delta T (FO draw - FO feed)
    Draw_Temp = Kelvin(np.ones(len(Hourly_Temp))*60)
    Permeate_Temp = Kelvin(Hourly_Temp) + 10
    Feed_Temp = Kelvin(Hourly_Temp)
    Delta_T = Draw_Temp - Feed_Temp
    P_Draw = Mole_Fraction_H2O_in_Feed*np.exp(23.1964-3816.44/(-46.13+Draw_Temp)) # in Pa
    P_Permeate = np.exp(23.1964-3816.44/(-46.13+Permeate_Temp)) # in Pa
    Delta_P = P_Draw - P_Permeate # in Pa
    
    # PD
    Mean_Temp = (Draw_Temp+Permeate_Temp)/2
    PD = 1.895*10**-5*(Mean_Temp)**2.072
    
    # Bw
    Atmos_Pressure = 101325 # Pa
    R = 8.314 # J/mol/K # Universal gas cons't
    delta = 0.000115 # m # Thickness of membrane
    epsilon = 0.85 # porosity
    tau = (2-epsilon)**2/epsilon
    pore_radius = 0.000000225 # m
    Mw = 18/1000 # kg/mol (molar weight of H2O)
    
    Bw = 1/R/Mean_Temp/delta*(3*tau/2/epsilon/pore_radius*(np.pi*Mw/8/R/Mean_Temp)**0.5+Atmos_Pressure*tau/epsilon/PD)**-1 # mol/m2/s/Pa
    
    # Jw
    Jw_Correction_Factor = 0.6395
    Jw = Bw*Delta_P*Mw*3600*Jw_Correction_Factor # in kg/m2/h
    
    # Membrane Areas
    Mean_24_Hourly_Supply = Hourly_24_hr(Hourly_WW_Supply) # in L/hour # ASSUMING 24-HOUR STORAGE
    # Mem_Area_FO = np.max(Hourly_WW_Supply * Mu_m / Kelvin(Hourly_Temp))/0.0139 # in m2
    # Mem_Area_MD = np.max(Hourly_WW_Supply/Jw)/1.196 # 1 Liter of water assumed equal to 1 kg # in m2
    Mem_Area_FO = np.max(Mean_24_Hourly_Supply * Mu_m / Kelvin(Hourly_Temp))/0.0139 # in m2
    Mem_Area_MD = np.max(Mean_24_Hourly_Supply/Jw)/1.196 # 1 Liter of water assumed equal to 1 kg # in m2

    WWT_Capex = np.floor(Mem_Area_FO/Unit_Area_FO)*Unit_Cost_FO*USD_2015_To_2019 + (np.floor(Mem_Area_MD/Unit_Area_MD)*Unit_Cost_MD)*Membrane_Cost_To_EPC_FO_MD*Desalin_to_WWT * USD_2015_To_2019 # in 2019 $
    WWT_Opex = Membrane_Cost_To_Replacement_Cost*(np.floor(Mem_Area_FO/Unit_Area_FO)*Unit_Cost_FO*USD_2015_To_2019 + (np.floor(Mem_Area_MD/Unit_Area_MD)*Unit_Cost_MD)*Membrane_Cost_To_Operation_FO_MD*Desalin_to_WWT * USD_2015_To_2019) # 2019 $/year ## from Al-Obaidani et al. 2008 (look at the Design Criteria for Wastewater Treatment... document)

    
    # Heat and electricity demand
    c_water = 4.184 # kJ/kg/K # Specific heat capacity of water
    # Heat_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Recovery_Rate * c_water * Delta_T / 0.7 * MJ_to_kWh # 0.7 = total energy efficiency of FO-MD
    # Electric_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Electric_Demand * np.ones(len(Hourly_Temp))
    Heat_Demand_Total = Mean_24_Hourly_Supply * Liter_to_M3 * WWT_Recovery_Rate * c_water * Delta_T / 0.7 * MJ_to_kWh # 0.7 = total energy efficiency of FO-MD
    Electric_Demand_Total = Mean_24_Hourly_Supply * Liter_to_M3 * WWT_Electric_Demand * np.ones(len(Hourly_Temp))
    
    WWT_Opex_Total = WWT_Opex # Annual
    WWT_Capex_Total = WWT_Capex # total # The correction factors are acting on the WWT_Capex in this case as the value was extracted from a paper and not from the cost estimation handbook
        
    return [Electric_Demand_Total, Heat_Demand_Total, WWT_Opex_Total, WWT_Capex_Total]




# =============================================================================
# ## All costs are in US dollars and all indexes were brought current to June 2007!!
# def UF_NF(Hourly_WW_Supply, Hourly_Temp):
#     '''
#     energy & heat req't from CostTemplate sheet in DST_ERC_V25.xlsm [SelWTP]
#     '''
#     
#     # Constants
#     WWT_Electric_Demand =  0.50 +  0.15 + UV_Electrical_Consumption  # Loose NF (i.e. 0.50) + MF/UF (Ceramic) (i.e. 0.15) # kWh/m3
#     WWT_Heat_Demand = 0 # kWh/m3
#     WWT_Recovery_Rate = 0.931 # From CostTemplate from SelWTP
#     
#     # Calculations
#     Max_24_Supply = Mean_24_hr(Hourly_WW_Supply) # in L
#     WWT_Capex = 3 * (10**6 * 11.268 * (Max_24_Supply * Liter_to_Galon / 10**6)**0.7271 * USD_2007_To_2019) # in 2019 $/year # That of UF is used # Factor of 3 used to convert UF to NF cost and assumed the hybrid process to have the same cost as NF plant # Ibid. as FO_RO's OPEX
#     WWT_Opex = 10**6 * 0.686 * (Max_24_Supply * Liter_to_Galon / 10**6)**0.638 * USD_2007_To_2019 # in 2019 $/year  # That of UF is used # Ibid. as FO_RO's OPEX
# 
# 
#     Heat_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Heat_Demand
#     Electric_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Electric_Demand
#     
#     WWT_Opex_Total = WWT_Opex * Desalin_to_WWT * With_Power_Cost_to_No_Power_Cost # Annual # Don't use hourly graywater and multiplying it by 24 then dividing the result by 365, it badly overshoots the OPEX
#     WWT_Capex_Total = WWT_Capex * Desalin_to_WWT * With_Power_Cost_to_No_Power_Cost # Annual
#     
#     return [Electric_Demand_Total, Heat_Demand_Total, WWT_Opex_Total, WWT_Capex_Total]
# =============================================================================
    
    
def WWTP(Hourly_WW_Supply, Hourly_Temp, Grid_Emissions): 


## IT'S FOR A WATER TREATMENT PLANT!! ## MUST CONVERT WATER TREATMENT PLANT TO WW TREATMENT PLANT COSTS AND ENERGY CONSUMPTION ## Also the values must be updated!

    # Constants
    
    ### NEED TO CHANGE THE POWER CONSUMPTION VALUES, THEY'RE TOO HIGH!
    
    Cap_Real_CWWTP = 57 # MGD
    ## Electric demand from https://www.energystar.gov/sites/default/files/tools/DataTrends_Wastewater_20150129.pdf
    WWT_Electric_Demand = 1.1 # kWh/m3 # From Design Criteria for Wastewater Treatment Module document
    WWT_Heat_Demand = 0 # kWh/m3
    
    
    # Calculations
    Mean_24_Hourly_Supply = Hourly_24_hr(Hourly_WW_Supply) # in L/hour # ASSUMING 24-HOUR STORAGE
    Mean_24_Supply = Mean_24_hr(Hourly_WW_Supply) * Liter_to_Galon / 10**6 # in million gallons per day
    WWT_Capex = 10**6 * 7.1052 * (Cap_Real_CWWTP)**0.8302 * USD_2007_To_2019 # in 2019 $/year # Micromembrnae Filtration from Cost_Estimate Water Treatment Facility (the "total construction cost") located at"D:\PhD\+Main Research Directory\W&WW\++ LCC & LCA" -> P99
    WWT_Opex = 10**6 * 0.4441 * (Cap_Real_CWWTP)**0.4323 * USD_2007_To_2019 # in 2019 $/year # Micromembrnae Filtration from Cost_Estimate Water Treatment Facility located at"D:\PhD\+Main Research Directory\W&WW\++ LCC & LCA" -> P113
    
    # Heat_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Heat_Demand
    # Electric_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Electric_Demand
    Heat_Demand_Total = Mean_24_Hourly_Supply * Liter_to_M3 * WWT_Heat_Demand
    Electric_Demand_Total = Mean_24_Hourly_Supply * Liter_to_M3 * WWT_Electric_Demand
    
    WWT_Opex_Total = Mean_24_Supply/Cap_Real_CWWTP * WWT_Opex # Annual # Mean_24_Supply/Cap_Real_CWWTP = attribution factor
    WWT_Capex_Total = Mean_24_Supply/Cap_Real_CWWTP * WWT_Capex # Annual
    
    # WWT_Direct_GHG = np.sum(Hourly_WW_Supply) * Liter_to_M3 * 10**-3 # Ton CO2 [10^-3 ton = 1 kg per m3 input ww] from (Flores-Alsina et al., 2011)
    WWT_Direct_GHG = np.sum(Mean_24_Hourly_Supply) * Liter_to_M3 * 10**-3 # Ton CO2 [10^-3 ton = 1 kg per m3 input ww] from (Flores-Alsina et al., 2011)
    WWT_Indirect_GHG = np.sum(Electric_Demand_Total * Grid_Emissions) / MT_to_lbs # Ton CO2
    
    return [0, 0, WWT_Opex_Total, WWT_Capex_Total, WWT_Direct_GHG + WWT_Indirect_GHG]


## IF YOU DECIDE TO USE THE NEXT TECHS, THEIR CALCULATIONS MUST BE UPDATED ACCORDING TO THE ONES ABOVE
    

## All costs are in US dollars and all indexes were brought current to June 2007!!
# =============================================================================
# def MED(Hourly_WW_Supply):
#     '''
#     energy & heat req't from CostTemplate sheet in DST_ERC_V25.xlsm [SelWTP]
#     '''
#     
#     # Constants
#     WWT_Electric_Demand = 1.5 # kWh/m3
#     WWT_Heat_Demand = 52.08333333 # kWh/m3
#     WWT_Recovery_Rate = 0.9312
#     
#     # Calculations
#     Max_24_Supply = Max_24_hr(Hourly_WW_Supply) # in L
#     WWT_Capex = 10**6 * 31.05 * (Max_24_Supply * Liter_to_Galon / 10**6)**0.6097 # in $/year ## THAT OF RO IS USED! P.103 from Cost_Estimate Water Treatment Facility
#     WWT_Opex = 10**6 * 1.2576 * (Max_24_Supply * Liter_to_Galon / 10**6)**1.0549 # $/year ## THAT OF RO IS USED! P.103 from Cost_Estimate Water Treatment Facility
# 
#     Heat_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Heat_Demand
#     Electric_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Electric_Demand
#     WWT_Opex_Total = WWT_Opex * 0.3 ## Assumed 70% of the O&M is from energy ## Is this way of calculating the OPEX right? Or should I hourly change the OPEX based on the hourly input gw?
#     WWT_Capex_Total = WWT_Capex
#     
#     return [Electric_Demand_Total, Heat_Demand_Total, WWT_Opex_Total, WWT_Capex_Total]
# =============================================================================


## All costs are in US dollars and all indexes were brought current to June 2007!!
# =============================================================================
# def MSF(Hourly_WW_Supply):
#     '''
#     energy & heat req't from CostTemplate sheet in DST_ERC_V25.xlsm [SelWTP]
#     '''
#     
#     # Constants
#     WWT_Electric_Demand = 3.5 # kWh/m3
#     WWT_Heat_Demand = 65.55555556 # kWh/m3
#     WWT_Recovery_Rate = 0.9312
#     
#     # Calculations
#     Max_24_Supply = Max_24_hr(Hourly_WW_Supply) # in L
#     WWT_Capex = 10**6 * 43.577 * (Max_24_Supply * Liter_to_Galon / 10**6)**0.6739 # in $ ## THAT OF RO IS USED! P.103 from Cost_Estimate Water Treatment Facility
#     WWT_Opex = 10**6 * 1.8653 * (Max_24_Supply * Liter_to_Galon / 10**6)**0.9808 # $/year ## THAT OF RO IS USED! P.103 from Cost_Estimate Water Treatment Facility
# 
#     Heat_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Heat_Demand
#     Electric_Demand_Total = Hourly_WW_Supply * Liter_to_M3 * WWT_Electric_Demand
#     WWT_Opex_Total = WWT_Opex * 0.3 ## Assumed 70% of the O&M is from energy ## Is this way of calculating the OPEX right? Or should I hourly change the OPEX based on the hourly input gw?
#     WWT_Capex_Total = WWT_Capex
#     
#     return [Electric_Demand_Total, Heat_Demand_Total, WWT_Opex_Total, WWT_Capex_Total]
# =============================================================================
