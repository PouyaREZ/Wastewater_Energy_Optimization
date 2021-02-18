from __future__ import division

#-------------------------------------------------------------------------------
# Name:        AbsorptionChillers
# Purpose:     File full of absorption chiller simulations for use in urban
#              optimization code
#
# Author:      Rob Best
# Modifier:    Pouya Rezazadeh
#
# Created:     23/07/2015
# Modified:    06/01/2019
#
# Copyright:   (c) Rob Best 2015
#-------------------------------------------------------------------------------

#import numpy as np
import math as mp
#import random as rp
#import sys

'''-----------------------------------------------------------------------------------------------'''
# Universal Constants #
'''-----------------------------------------------------------------------------------------------'''
Btu_to_J = 1055.00                  # Conversion of Btu to J
kWh_to_J = 3600000.00               # Conversion of kWh to J
MWh_to_J = 3600000000.00            # Conversion of MWh to J
tons_to_J_hr = 12660670.23144     #1266067022400.00 WRONG prev value    # Conversion of tons cooling to J/hour
kWh_to_Btu = 3412                   # Conversion of kWh to Btu
tons_to_MMBtu_hr = 0.012            # Conversion of tons to MMBtu/hr
tons_to_Btu_hr = 12000              # Conversion of tons to Btu/hr
tons_to_kW = 3.5168525              # Conversion of tons to kWh
meters_to_ft = 3.28084              # Conversion of meters to feet

Specific_Heat_Water = 4216.00       # Specific heat of water at STP (J/kg-C) ## updated from engineeringtoolbox (Apr 2019)
Density_Water = 999.9               # Density of liquid water (kg/m^3)

Hot_Water_Requirement = 45.5556              # Fahrenheit
Hot_Water_delT = 5.5556                      # Fahrenheit

USD_2015_to_2019 = 1.08             # http://www.in2013dollars.com/us/inflation/2015?amount=1


'''-----------------------------------------------------------------------------------------------'''
# Chiller Parameters #
'''-----------------------------------------------------------------------------------------------'''
#Chilled_Water_Supply_Temperature = 6.67     # deg C
#CWST = 6.67                                 # deg C
#Number_Iterations = 1                       # dimensionless
#Heat_Source_Temperature = 37.78             # deg C
#Water_delT = 5.5556                          # Fahrenheit
#Cooling_Tower_Approach = 5.0                # Fahrenheit
#Tempered_Supply_Temperature = 15.5556       # deg C

############## Auxiliary function start ###################

def Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost):
    Capital_Cost *= USD_2015_to_2019

    # Convert temperatures to Celsius
    CWST = (Chilled_Water_Supply_Temperature-32.0)*5.0/9.0
    HST = (Heat_Source_Temperature-32.0)*5.0/9.0

    # Calculate Condenser Inlet Water Tempearture and convert to Celsius
    ECFT = (Wet_Bulb_Temperature+Cooling_Tower_Approach-32.0)*5.0/9.0 ## Wet_Bulb_Temperature

    # Calculate capacity modifier values and available chiller capacity
    CAPfCond = CAPfCond_1+CAPfCond_2*ECFT+CAPfCond_3*ECFT**2+CAPfCond_4*ECFT**3 ## ECFT
    CAPfEvap = CAPfEvap_1+CAPfEvap_2*CWST+CAPfEvap_3*CWST**2+CAPfEvap_4*CWST**3

    if Heat_Source == 'Hot Water':
        CAPfGen = CAPfGen_1+CAPfGen_2*HST+CAPfGen_3*HST**2+CAPfGen_4*HST**3
        Available_Capacity = Reference_Capacity*CAPfCond*CAPfEvap*CAPfGen ## CAPfCond
    else:
        Available_Capacity = Reference_Capacity*CAPfCond*CAPfEvap ## CAPfCond

    # Calculate Heat Input Requirement modifiers
    SteamfCondTemp = SteamfCondTemp_1+SteamfCondTemp_2*ECFT+SteamfCondTemp_3*ECFT**2+SteamfCondTemp_4*ECFT**3 ## ECFT
    SteamfEvapTemp = SteamfEvapTemp_1+SteamfEvapTemp_2*CWST+SteamfEvapTemp_3*CWST**2+SteamfEvapTemp_4*CWST**3

    # Calculate Test PLR to determine number of units
    Test_PLR = Hourly_Cooling/Available_Capacity ## Available_Capacity ## Hourly_Cooling

    if Test_PLR == 0: ## SHOULD MODIFY ## Test_PLR
        Number_Units = 0
        Heat_Input = 0 ## Should modify
        COP = 0 ## Should modify
        PLR = 0 ## SHOULD MODIFY
        Electrical_Demand = 0  ## SHOULD MODIFY
    elif Test_PLR < Maximum_Part_Load_Ratio: ## Test_PLR
        Number_Units = 1
        PLR = Test_PLR ## Test_PLR
        SteamUsefPLR = SteamUsefPLR_1+SteamUsefPLR_2*PLR+SteamUsefPLR_3*PLR**2+SteamUsefPLR_4*PLR**3 ## PLR
        PumpUsefPLR = PumpUsefPLR_1+PumpUsefPLR_2*PLR+PumpUsefPLR_3*PLR**2 ## PLR
        Chiller_Cycling_Fraction = min(1.0, PLR/Minimum_Part_Load_Ratio) ## PLR
        Heat_Input = Available_Capacity*SteamUsefPLR*SteamfCondTemp*SteamfEvapTemp*Chiller_Cycling_Fraction ## Available_Capacity ## ARRAY ## SteamUsefPLR ## Chiller_Cycling_Fraction
        Electrical_Demand = Nominal_Pumping_Power*PumpUsefPLR*Chiller_Cycling_Fraction ## PumpUsefPLR ## Chiller_Cycling_Fraction
        COP = Hourly_Cooling/Heat_Input ## Hourly_Cooling ## Heat_Input
    else:
        Number_Units = mp.ceil(Hourly_Cooling/(Available_Capacity*Maximum_Part_Load_Ratio)) ## Available_Capacity ## SHOULD MODIFY ##  ## Hourly_Cooling
        Unit_Hourly_Cooling = Hourly_Cooling/Number_Units ##  ## Hourly_Cooling
        PLR = Unit_Hourly_Cooling/Available_Capacity ## Available_Capacity ## PLR
        SteamUsefPLR = SteamUsefPLR_1+SteamUsefPLR_2*PLR+SteamUsefPLR_3*PLR**2+SteamUsefPLR_4*PLR**3 ## PLR  ## SteamUsefPLR
        PumpUsefPLR = PumpUsefPLR_1+PumpUsefPLR_2*PLR+PumpUsefPLR_3*PLR**2 ## PLR ## PumpUsefPLR
        Chiller_Cycling_Fraction = min(1.0, PLR/Minimum_Part_Load_Ratio) ## PLR ## Chiller_Cycling_Fraction
        Unit_Heat_Input = Available_Capacity*SteamUsefPLR*SteamfCondTemp*SteamfEvapTemp*Chiller_Cycling_Fraction ## Available_Capacity ## ARRAY  ## SteamUsefPLR ## Chiller_Cycling_Fraction 
        Electrical_Demand = Number_Units*Nominal_Pumping_Power*PumpUsefPLR*Chiller_Cycling_Fraction ## PumpUsefPLR ## Chiller_Cycling_Fraction
        COP = Unit_Hourly_Cooling/Unit_Heat_Input ## COP
        Heat_Input = Number_Units*Unit_Heat_Input  ## Heat_Input

    Cooling_Tower_Fan_Power = (Hourly_Cooling+Electrical_Demand)/1170*11.2 ## Electrical_Demand  ## Hourly_Cooling
    Electrical_Demand += Cooling_Tower_Fan_Power

    LCFT = ECFT + (Hourly_Cooling+Electrical_Demand)*1000/(Density_Water*Reference_COW_Flow_Rate)/Specific_Heat_Water ## ECFT ## Electrical_Demand  ## Hourly_Cooling
    if LCFT >= Hot_Water_Requirement:
        Heat_Recovery_Potential =(LCFT-(Hot_Water_Requirement-Hot_Water_delT))*(Density_Water*Reference_COW_Flow_Rate)*Specific_Heat_Water
    else:
        Heat_Recovery_Potential = 0.0

    Total_Cost = Capital_Cost/tons_to_kW*Reference_Capacity*Number_Units
    
    return [Number_Units, Electrical_Demand, Heat_Input, Hourly_Cooling, COP, Total_Cost, Heat_Recovery_Potential]

############## Auxiliary function end ###################


def Absorption_Chiller_1(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Based on Indirect Absorption Chiller model from EnergyPlus, Version 8-0-0. Modifier curves from
        EnergyPlus Indirect Absorption Chiller model Example, Version 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Wet Bulb Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 100.0                  # kW
    Nominal_Pumping_Power = 1.50                # kW
    Minimum_Part_Load_Ratio = 0.15              # Dimensionless
    Maximum_Part_Load_Ratio = 1.0               # Dimensionless
#    Optimum_Part_Load_Ratio = 0.65              # Dimensionless
#    Reference_ECFT = 95.0                       # Fahrenheit (Entering Condenser Fluid Temperature)
#    ECFT_Lower_Limit = 50.0                     # Fahrenheit (Entering Condenser Fluid Temperature)
#    LCWT_Lower_Limit = 41.0                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Reference_CHW_Flow_Rate = 0.011             # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.011             # m3/s (Condenser Water)
    Heat_Source = 'Steam'                       # Source of hot water ('Steam' or 'Hot_Water')
#    EGWT_Lower_Limit = 86.0                     # Fahrenheit (Entering Generator Water Temperature)
#    Generator_Subcooling = 35.6                 # Fahrenheit
#    Steam_Loop_Subcooling = 53.6                # Fahrenheit
    CAPfCond_1 = 0.245507                       # Dimensionless
    CAPfCond_2 = 0.023614                       # Dimensionless
    CAPfCond_3 = 0.0000278                      # Dimensionless
    CAPfCond_4 = 0.000013                       # Dimensionless
    CAPfEvap_1 = 0.690571                       # Dimensionless
    CAPfEvap_2 = 0.065571                       # Dimensionless
    CAPfEvap_3 = -0.00289                       # Dimensionless
    CAPfEvap_4 = 0.0                            # Dimensionless
    CAPfGen_1 = 1.0                             # Dimensionless
    CAPfGen_2 = 0.0                             # Dimensionless
    CAPfGen_3 = 0.0                             # Dimensionless
    CAPfGen_4 = 0.0                             # Dimensionless
    SteamUsefPLR_1 = 0.18892                    # Dimensionless
    SteamUsefPLR_2 = 0.968044                   # Dimensionless
    SteamUsefPLR_3 = 1.119202                   # Dimensionless
    SteamUsefPLR_4 = -0.5034                    # Dimensionless
    PumpUsefPLR_1 = 1.0                         # Dimensionless
    PumpUsefPLR_2 = 0.0                         # Dimensionless
    PumpUsefPLR_3 = 0.0                         # Dimensionless
    SteamfCondTemp_1 = 0.712019                 # Dimensionless
    SteamfCondTemp_2 = -0.00478                 # Dimensionless
    SteamfCondTemp_3 = 0.000864                 # Dimensionless
    SteamfCondTemp_4 = -0.000013                # Dimensionless
    SteamfEvapTemp_1 = 0.995571                 # Dimensionless
    SteamfEvapTemp_2 = 0.046821                 # Dimensionless
    SteamfEvapTemp_3 = -0.01099                 # Dimensionless
    SteamfEvapTemp_4 = 0.000608                 # Dimensionless
#    Reference_GS_Flow_Rate = 0.270              # kg/s (Generator Steam)
#    Chiller_Flow = 'Constant'                   # Specifies flow type ('Constant' or 'Variable')
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 1000.0                       # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost)

def Absorption_Chiller_2(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Based on Indirect Absorption Chiller model from EnergyPlus, Version 8-0-0. Modifier curves from a York
        YIA-ST-1A1 COP 0.793 Single-Effect Absorption Chiller. The data are from Johnson Controls, Inc.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Wet Bulb Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 420.0                  # kW
    Nominal_Pumping_Power = 5.9                 # kW
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
#    Reference_ECFT = 85.0                       # Fahrenheit (Entering Condenser Fluid Temperature)
#    ECFT_Lower_Limit = 50.0                     # Fahrenheit (Entering Condenser Fluid Temperature)
#    LCWT_Lower_Limit = 40.0                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Reference_CHW_Flow_Rate = 0.01817           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.02725           # m3/s (Condenser Water)
    Heat_Source = 'Steam'                       # Source of hot water ('Steam' or 'Hot_Water')
#    EGWT_Lower_Limit = 86.0                     # Fahrenheit (Entering Generator Water Temperature)
#    Generator_Subcooling = 35.6                 # Fahrenheit
#    Steam_Loop_Subcooling = 53.6                # Fahrenheit
    CAPfCond_1 = 0.4907                         # Dimensionless
    CAPfCond_2 = -0.0253                        # Dimensionless
    CAPfCond_3 = 0.0043                         # Dimensionless
    CAPfCond_4 = -0.0001                        # Dimensionless
    CAPfEvap_1 = 0.96                           # Dimensionless
    CAPfEvap_2 = -0.075                         # Dimensionless
    CAPfEvap_3 = 0.0202                         # Dimensionless
    CAPfEvap_4 = -0.0012                        # Dimensionless
    CAPfGen_1 = 1.0                             # Dimensionless
    CAPfGen_2 = 0.0                             # Dimensionless
    CAPfGen_3 = 0.0                             # Dimensionless
    CAPfGen_4 = 0.0                             # Dimensionless
    SteamUsefPLR_1 = 0.1173                     # Dimensionless
    SteamUsefPLR_2 = 0.4986                     # Dimensionless
    SteamUsefPLR_3 = 0.683                      # Dimensionless
    SteamUsefPLR_4 = -0.2991                    # Dimensionless
    PumpUsefPLR_1 = 1.0                         # Dimensionless
    PumpUsefPLR_2 = 0.0                         # Dimensionless
    PumpUsefPLR_3 = 0.0                         # Dimensionless
    SteamfCondTemp_1 = 0.7064                   # Dimensionless
    SteamfCondTemp_2 = 0.0049                   # Dimensionless
    SteamfCondTemp_3 = 0.0002                   # Dimensionless
    SteamfCondTemp_4 = 0.00000000000000002      # Dimensionless
    SteamfEvapTemp_1 = 0.8223                   # Dimensionless
    SteamfEvapTemp_2 = 0.1303                   # Dimensionless
    SteamfEvapTemp_3 = -0.0237                  # Dimensionless
    SteamfEvapTemp_4 = 0.0012                   # Dimensionless
#    Reference_GS_Flow_Rate = 0.270              # kg/s (Generator Steam)
#    Chiller_Flow = 'Constant'                   # Specifies flow type ('Constant' or 'Variable')
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 900.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost)

def Absorption_Chiller_3(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Based on Indirect Absorption Chiller model from EnergyPlus, Version 8-0-0. Modifier curves from a York
        YIA-ST-3B3 COP 0.793 Single-Effect Absorption Chiller. The data are from Johnson Controls, Inc.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Wet Bulb Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 1094.0                 # kW
    Nominal_Pumping_Power = 7.3                 # kW
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
#    Reference_ECFT = 85.0                       # Fahrenheit (Entering Condenser Fluid Temperature)
#    ECFT_Lower_Limit = 50.0                     # Fahrenheit (Entering Condenser Fluid Temperature)
#    LCWT_Lower_Limit = 40.0                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Reference_CHW_Flow_Rate = 0.04709           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.7066            # m3/s (Condenser Water)
    Heat_Source = 'Steam'                       # Source of hot water ('Steam' or 'Hot_Water')
#    EGWT_Lower_Limit = 86.0                     # Fahrenheit (Entering Generator Water Temperature)
#    Generator_Subcooling = 35.6                 # Fahrenheit
#    Steam_Loop_Subcooling = 53.6                # Fahrenheit
    CAPfCond_1 = 0.4907                         # Dimensionless
    CAPfCond_2 = -0.0253                        # Dimensionless
    CAPfCond_3 = 0.0043                         # Dimensionless
    CAPfCond_4 = -0.0001                        # Dimensionless
    CAPfEvap_1 = 0.96                           # Dimensionless
    CAPfEvap_2 = -0.075                         # Dimensionless
    CAPfEvap_3 = 0.0202                         # Dimensionless
    CAPfEvap_4 = -0.0012                        # Dimensionless
    CAPfGen_1 = 1.0                             # Dimensionless
    CAPfGen_2 = 0.0                             # Dimensionless
    CAPfGen_3 = 0.0                             # Dimensionless
    CAPfGen_4 = 0.0                             # Dimensionless
    SteamUsefPLR_1 = 0.1173                     # Dimensionless
    SteamUsefPLR_2 = 0.4986                     # Dimensionless
    SteamUsefPLR_3 = 0.683                      # Dimensionless
    SteamUsefPLR_4 = -0.2991                    # Dimensionless
    PumpUsefPLR_1 = 1.0                         # Dimensionless
    PumpUsefPLR_2 = 0.0                         # Dimensionless
    PumpUsefPLR_3 = 0.0                         # Dimensionless
    SteamfCondTemp_1 = 0.7064                   # Dimensionless
    SteamfCondTemp_2 = 0.0049                   # Dimensionless
    SteamfCondTemp_3 = 0.0002                   # Dimensionless
    SteamfCondTemp_4 = 0.00000000000000002      # Dimensionless
    SteamfEvapTemp_1 = 0.8223                   # Dimensionless
    SteamfEvapTemp_2 = 0.1303                   # Dimensionless
    SteamfEvapTemp_3 = -0.0237                  # Dimensionless
    SteamfEvapTemp_4 = 0.0012                   # Dimensionless
#    Reference_GS_Flow_Rate = 0.695              # kg/s (Generator Steam)
#    Chiller_Flow = 'Constant'                   # Specifies flow type ('Constant' or 'Variable')
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 775.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost)

def Absorption_Chiller_4(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Based on Indirect Absorption Chiller model from EnergyPlus, Version 8-0-0. Modifier curves from a York
        YIA-ST-5C3 COP 0.793 Single-Effect Absorption Chiller. The data are from Johnson Controls, Inc.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Wet Bulb Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 1568.0                 # kW
    Nominal_Pumping_Power = 7.3                 # kW
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
#    Reference_ECFT = 85.0                       # Fahrenheit (Entering Condenser Fluid Temperature)
#    ECFT_Lower_Limit = 50.0                     # Fahrenheit (Entering Condenser Fluid Temperature)
#    LCWT_Lower_Limit = 40.0                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Reference_CHW_Flow_Rate = 0.06753           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.10094           # m3/s (Condenser Water)
    Heat_Source = 'Steam'                       # Source of hot water ('Steam' or 'Hot_Water')
#    EGWT_Lower_Limit = 86.0                     # Fahrenheit (Entering Generator Water Temperature)
#    Generator_Subcooling = 35.6                 # Fahrenheit
#    Steam_Loop_Subcooling = 53.6                # Fahrenheit
    CAPfCond_1 = 0.4907                         # Dimensionless
    CAPfCond_2 = -0.0253                        # Dimensionless
    CAPfCond_3 = 0.0043                         # Dimensionless
    CAPfCond_4 = -0.0001                        # Dimensionless
    CAPfEvap_1 = 0.96                           # Dimensionless
    CAPfEvap_2 = -0.075                         # Dimensionless
    CAPfEvap_3 = 0.0202                         # Dimensionless
    CAPfEvap_4 = -0.0012                        # Dimensionless
    CAPfGen_1 = 1.0                             # Dimensionless
    CAPfGen_2 = 0.0                             # Dimensionless
    CAPfGen_3 = 0.0                             # Dimensionless
    CAPfGen_4 = 0.0                             # Dimensionless
    SteamUsefPLR_1 = 0.1173                     # Dimensionless
    SteamUsefPLR_2 = 0.4986                     # Dimensionless
    SteamUsefPLR_3 = 0.683                      # Dimensionless
    SteamUsefPLR_4 = -0.2991                    # Dimensionless
    PumpUsefPLR_1 = 1.0                         # Dimensionless
    PumpUsefPLR_2 = 0.0                         # Dimensionless
    PumpUsefPLR_3 = 0.0                         # Dimensionless
    SteamfCondTemp_1 = 0.7064                   # Dimensionless
    SteamfCondTemp_2 = 0.0049                   # Dimensionless
    SteamfCondTemp_3 = 0.0002                   # Dimensionless
    SteamfCondTemp_4 = 0.00000000000000002      # Dimensionless
    SteamfEvapTemp_1 = 0.8223                   # Dimensionless
    SteamfEvapTemp_2 = 0.1303                   # Dimensionless
    SteamfEvapTemp_3 = -0.0237                  # Dimensionless
    SteamfEvapTemp_4 = 0.0012                   # Dimensionless
#    Reference_GS_Flow_Rate = 1.001              # kg/s (Generator Steam)
#    Chiller_Flow = 'Constant'                   # Specifies flow type ('Constant' or 'Variable')
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 720.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost)

def Absorption_Chiller_5(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Based on Indirect Absorption Chiller model from EnergyPlus, Version 8-0-0. Modifier curves from a York
        YIA-ST-1A1 COP 0.793 Single-Effect Absorption Chiller. The data are from Johnson Controls, Inc.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Wet Bulb Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 2170.0                 # kW
    Nominal_Pumping_Power = 9.7                 # kW
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
#    Reference_ECFT = 85.0                       # Fahrenheit (Entering Condenser Fluid Temperature)
#    ECFT_Lower_Limit = 50.0                     # Fahrenheit (Entering Condenser Fluid Temperature)
#    LCWT_Lower_Limit = 40.0                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Reference_CHW_Flow_Rate = 0.09342           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.14006           # m3/s (Condenser Water)
    Heat_Source = 'Steam'                       # Source of hot water ('Steam' or 'Hot_Water')
#    EGWT_Lower_Limit = 86.0                     # Fahrenheit (Entering Generator Water Temperature)
#    Generator_Subcooling = 35.6                 # Fahrenheit
#    Steam_Loop_Subcooling = 53.6                # Fahrenheit
    CAPfCond_1 = 0.4907                         # Dimensionless
    CAPfCond_2 = -0.0253                        # Dimensionless
    CAPfCond_3 = 0.0043                         # Dimensionless
    CAPfCond_4 = -0.0001                        # Dimensionless
    CAPfEvap_1 = 0.96                           # Dimensionless
    CAPfEvap_2 = -0.075                         # Dimensionless
    CAPfEvap_3 = 0.0202                         # Dimensionless
    CAPfEvap_4 = -0.0012                        # Dimensionless
    CAPfGen_1 = 1.0                             # Dimensionless
    CAPfGen_2 = 0.0                             # Dimensionless
    CAPfGen_3 = 0.0                             # Dimensionless
    CAPfGen_4 = 0.0                             # Dimensionless
    SteamUsefPLR_1 = 0.1173                     # Dimensionless
    SteamUsefPLR_2 = 0.4986                     # Dimensionless
    SteamUsefPLR_3 = 0.683                      # Dimensionless
    SteamUsefPLR_4 = -0.2991                    # Dimensionless
    PumpUsefPLR_1 = 1.0                         # Dimensionless
    PumpUsefPLR_2 = 0.0                         # Dimensionless
    PumpUsefPLR_3 = 0.0                         # Dimensionless
    SteamfCondTemp_1 = 0.7064                   # Dimensionless
    SteamfCondTemp_2 = 0.0049                   # Dimensionless
    SteamfCondTemp_3 = 0.0002                   # Dimensionless
    SteamfCondTemp_4 = 0.00000000000000002      # Dimensionless
    SteamfEvapTemp_1 = 0.8223                   # Dimensionless
    SteamfEvapTemp_2 = 0.1303                   # Dimensionless
    SteamfEvapTemp_3 = -0.0237                  # Dimensionless
    SteamfEvapTemp_4 = 0.0012                   # Dimensionless
#    Reference_GS_Flow_Rate = 1.390              # kg/s (Generator Steam)
#    Chiller_Flow = 'Constant'                   # Specifies flow type ('Constant' or 'Variable')
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 650.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost)

def Absorption_Chiller_6(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Based on Indirect Absorption Chiller model from EnergyPlus, Version 8-0-0. Modifier curves from a York
        YIA-ST-9E2 COP 0.793 Single-Effect Absorption Chiller. The data are from Johnson Controls, Inc.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Wet Bulb Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 3193.0                 # kW
    Nominal_Pumping_Power = 11.2                # kW
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
#    Reference_ECFT = 85.0                       # Fahrenheit (Entering Condenser Fluid Temperature)
#    ECFT_Lower_Limit = 50.0                     # Fahrenheit (Entering Condenser Fluid Temperature)
#    LCWT_Lower_Limit = 40.0                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Reference_CHW_Flow_Rate = 0.13748           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.20630           # m3/s (Condenser Water)
    Heat_Source = 'Steam'                       # Source of hot water ('Steam' or 'Hot_Water')
#    EGWT_Lower_Limit = 86.0                     # Fahrenheit (Entering Generator Water Temperature)
#    Generator_Subcooling = 35.6                 # Fahrenheit
#    Steam_Loop_Subcooling = 53.6                # Fahrenheit
    CAPfCond_1 = 0.4907                         # Dimensionless
    CAPfCond_2 = -0.0253                        # Dimensionless
    CAPfCond_3 = 0.0043                         # Dimensionless
    CAPfCond_4 = -0.0001                        # Dimensionless
    CAPfEvap_1 = 0.96                           # Dimensionless
    CAPfEvap_2 = -0.075                         # Dimensionless
    CAPfEvap_3 = 0.0202                         # Dimensionless
    CAPfEvap_4 = -0.0012                        # Dimensionless
    CAPfGen_1 = 1.0                             # Dimensionless
    CAPfGen_2 = 0.0                             # Dimensionless
    CAPfGen_3 = 0.0                             # Dimensionless
    CAPfGen_4 = 0.0                             # Dimensionless
    SteamUsefPLR_1 = 0.1173                     # Dimensionless
    SteamUsefPLR_2 = 0.4986                     # Dimensionless
    SteamUsefPLR_3 = 0.683                      # Dimensionless
    SteamUsefPLR_4 = -0.2991                    # Dimensionless
    PumpUsefPLR_1 = 1.0                         # Dimensionless
    PumpUsefPLR_2 = 0.0                         # Dimensionless
    PumpUsefPLR_3 = 0.0                         # Dimensionless
    SteamfCondTemp_1 = 0.7064                   # Dimensionless
    SteamfCondTemp_2 = 0.0049                   # Dimensionless
    SteamfCondTemp_3 = 0.0002                   # Dimensionless
    SteamfCondTemp_4 = 0.00000000000000002      # Dimensionless
    SteamfEvapTemp_1 = 0.8223                   # Dimensionless
    SteamfEvapTemp_2 = 0.1303                   # Dimensionless
    SteamfEvapTemp_3 = -0.0237                  # Dimensionless
    SteamfEvapTemp_4 = 0.0012                   # Dimensionless
#    Reference_GS_Flow_Rate = 2.031              # kg/s (Generator Steam)
#    Chiller_Flow = 'Constant'                   # Specifies flow type ('Constant' or 'Variable')
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 610.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost)

def Absorption_Chiller_7(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Based on Indirect Absorption Chiller model from EnergyPlus, Version 8-0-0. Modifier curves from a York
        YIA-ST-12F1 COP 0.793 Single-Effect Absorption Chiller. The data are from Johnson Controls, Inc.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Wet Bulb Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 4037.0                 # kW
    Nominal_Pumping_Power = 13.5                # kW
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
#    Reference_ECFT = 85.0                       # Fahrenheit (Entering Condenser Fluid Temperature)
#    ECFT_Lower_Limit = 50.0                     # Fahrenheit (Entering Condenser Fluid Temperature)
#    LCWT_Lower_Limit = 40.0                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Reference_CHW_Flow_Rate = 0.17382           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.26119           # m3/s (Condenser Water)
    Heat_Source = 'Steam'                       # Source of hot water ('Steam' or 'Hot_Water')
#    EGWT_Lower_Limit = 86.0                     # Fahrenheit (Entering Generator Water Temperature)
#    Generator_Subcooling = 35.6                 # Fahrenheit
#    Steam_Loop_Subcooling = 53.6                # Fahrenheit
    CAPfCond_1 = 0.4907                         # Dimensionless
    CAPfCond_2 = -0.0253                        # Dimensionless
    CAPfCond_3 = 0.0043                         # Dimensionless
    CAPfCond_4 = -0.0001                        # Dimensionless
    CAPfEvap_1 = 0.96                           # Dimensionless
    CAPfEvap_2 = -0.075                         # Dimensionless
    CAPfEvap_3 = 0.0202                         # Dimensionless
    CAPfEvap_4 = -0.0012                        # Dimensionless
    CAPfGen_1 = 1.0                             # Dimensionless
    CAPfGen_2 = 0.0                             # Dimensionless
    CAPfGen_3 = 0.0                             # Dimensionless
    CAPfGen_4 = 0.0                             # Dimensionless
    SteamUsefPLR_1 = 0.1173                     # Dimensionless
    SteamUsefPLR_2 = 0.4986                     # Dimensionless
    SteamUsefPLR_3 = 0.683                      # Dimensionless
    SteamUsefPLR_4 = -0.2991                    # Dimensionless
    PumpUsefPLR_1 = 1.0                         # Dimensionless
    PumpUsefPLR_2 = 0.0                         # Dimensionless
    PumpUsefPLR_3 = 0.0                         # Dimensionless
    SteamfCondTemp_1 = 0.7064                   # Dimensionless
    SteamfCondTemp_2 = 0.0049                   # Dimensionless
    SteamfCondTemp_3 = 0.0002                   # Dimensionless
    SteamfCondTemp_4 = 0.00000000000000002      # Dimensionless
    SteamfEvapTemp_1 = 0.8223                   # Dimensionless
    SteamfEvapTemp_2 = 0.1303                   # Dimensionless
    SteamfEvapTemp_3 = -0.0237                  # Dimensionless
    SteamfEvapTemp_4 = 0.0012                   # Dimensionless
#    Reference_GS_Flow_Rate = 2.561              # kg/s (Generator Steam)
#    Chiller_Flow = 'Constant'                   # Specifies flow type ('Constant' or 'Variable')
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 575.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost)

def Absorption_Chiller_8(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Based on Indirect Absorption Chiller model from EnergyPlus, Version 8-0-0. Modifier curves from a York
        YIA-ST-14f3 COP 0.793 Single-Effect Absorption Chiller. The data are from Johnson Controls, Inc.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Wet Bulb Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 14842.0                # kW
    Nominal_Pumping_Power = 13.5                # kW
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
#    Reference_ECFT = 85.0                       # Fahrenheit (Entering Condenser Fluid Temperature)
#    ECFT_Lower_Limit = 50.0                     # Fahrenheit (Entering Condenser Fluid Temperature)
#    LCWT_Lower_Limit = 40.0                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Reference_CHW_Flow_Rate = 0.20849           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.31292           # m3/s (Condenser Water)
    Heat_Source = 'Steam'                       # Source of hot water ('Steam' or 'Hot_Water')
#    EGWT_Lower_Limit = 86.0                     # Fahrenheit (Entering Generator Water Temperature)
#    Generator_Subcooling = 35.6                 # Fahrenheit
#    Steam_Loop_Subcooling = 53.6                # Fahrenheit
    CAPfCond_1 = 0.4907                         # Dimensionless
    CAPfCond_2 = -0.0253                        # Dimensionless
    CAPfCond_3 = 0.0043                         # Dimensionless
    CAPfCond_4 = -0.0001                        # Dimensionless
    CAPfEvap_1 = 0.96                           # Dimensionless
    CAPfEvap_2 = -0.075                         # Dimensionless
    CAPfEvap_3 = 0.0202                         # Dimensionless
    CAPfEvap_4 = -0.0012                        # Dimensionless
    CAPfGen_1 = 1.0                             # Dimensionless
    CAPfGen_2 = 0.0                             # Dimensionless
    CAPfGen_3 = 0.0                             # Dimensionless
    CAPfGen_4 = 0.0                             # Dimensionless
    SteamUsefPLR_1 = 0.1173                     # Dimensionless
    SteamUsefPLR_2 = 0.4986                     # Dimensionless
    SteamUsefPLR_3 = 0.683                      # Dimensionless
    SteamUsefPLR_4 = -0.2991                    # Dimensionless
    PumpUsefPLR_1 = 1.0                         # Dimensionless
    PumpUsefPLR_2 = 0.0                         # Dimensionless
    PumpUsefPLR_3 = 0.0                         # Dimensionless
    SteamfCondTemp_1 = 0.7064                   # Dimensionless
    SteamfCondTemp_2 = 0.0049                   # Dimensionless
    SteamfCondTemp_3 = 0.0002                   # Dimensionless
    SteamfCondTemp_4 = 0.00000000000000002      # Dimensionless
    SteamfEvapTemp_1 = 0.8223                   # Dimensionless
    SteamfEvapTemp_2 = 0.1303                   # Dimensionless
    SteamfEvapTemp_3 = -0.0237                  # Dimensionless
    SteamfEvapTemp_4 = 0.0012                   # Dimensionless
#    Reference_GS_Flow_Rate = 3.092              # kg/s (Generator Steam)
#    Chiller_Flow = 'Constant'                   # Specifies flow type ('Constant' or 'Variable')
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 450.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Wet_Bulb_Temperature, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Nominal_Pumping_Power , Minimum_Part_Load_Ratio , Maximum_Part_Load_Ratio, Reference_COW_Flow_Rate, Heat_Source, CAPfCond_1 , CAPfCond_2 , CAPfCond_3 , CAPfCond_4 , CAPfEvap_1 , CAPfEvap_2 , CAPfEvap_3 , CAPfEvap_4, CAPfGen_1 , CAPfGen_2, CAPfGen_3 , CAPfGen_4 , SteamUsefPLR_1 , SteamUsefPLR_2 , SteamUsefPLR_3 , SteamUsefPLR_4 , PumpUsefPLR_1 , PumpUsefPLR_2, PumpUsefPLR_3, SteamfCondTemp_1 , SteamfCondTemp_2, SteamfCondTemp_3 , SteamfCondTemp_4 , SteamfEvapTemp_1 , SteamfEvapTemp_2, SteamfEvapTemp_3, SteamfEvapTemp_4, Cooling_Tower_Approach, Capital_Cost)    