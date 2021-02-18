from __future__ import division

#-------------------------------------------------------------------------------
# Name:        ElectricChillers
# Purpose:     File full of electric chiller simulations for use in urban
#              optimization code.
#
# Author:      Rob Best
# Modifier:    Pouya Rezazadeh [Updated and corrected based on individual intuition and same file from Ch4 and ToyOpt + added a small chiller for bldg-scale chilling
#
# Created:     22/07/2015
# Modified:    26/02/2019
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


###### Auxiliary function start ######
def Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost):
    Capital_Cost *= USD_2015_to_2019
    
    # Calculate the Entering Condenser Water Temperature
    ECFT = Outside_Wet_Bulb+Cooling_Tower_Approach

    # Convert temperatures to Celsius
    Chilled_Water_Supply_Temperature = (Chilled_Water_Supply_Temperature-32)*5.0/9.0
    ECFT = (ECFT-32)*5.0/9.0
    Outside_Air_Temperature = (Outside_Air_Temperature-32)*5.0/9.0

    n = 0

    while n < Number_Iterations:

        if n == 0:
            Available_Capacity = Reference_Capacity
            COP = Reference_COP

        # Calculate the Leaving Condenser Water Temperature
        if Hourly_Cooling < Minimum_Part_Load_Ratio*Available_Capacity:
            Total_Cool = Hourly_Cooling
            Q_avail = Minimum_Part_Load_Ratio*Available_Capacity*(Hourly_Cooling/Available_Capacity/Minimum_Part_Load_Ratio)
        elif Hourly_Cooling > Available_Capacity*Maximum_Part_Load_Ratio:
            Q_avail = Hourly_Cooling/mp.ceil(Hourly_Cooling/Available_Capacity)
            Total_Cool = Q_avail
        else:
            Q_avail = Hourly_Cooling
            Total_Cool = Hourly_Cooling

        if n == 0:
            Rough_Power = Q_avail/COP
            False_Loading = 0
        else:
            Rough_Power = Power

        Condenser_Rejection = (Total_Cool+Rough_Power)*1000 + False_Loading*1000
        Condenser_Water_Leaving_Temperature = ECFT+Condenser_Rejection/Specific_Heat_Water/(Reference_COW_Flow_Rate*Density_Water)
        if Condenser_Water_Leaving_Temperature >= Hot_Water_Requirement:
            Heat_Recovery_Potential =(Condenser_Water_Leaving_Temperature-(Hot_Water_Requirement-Hot_Water_delT))*(Density_Water*Reference_COW_Flow_Rate)*Specific_Heat_Water
        else:
            Heat_Recovery_Potential = 0.0

        # Calculate the first two chiller performance curves
        if Condenser_Type == 'Water Cooled':
            CAPFT = CAPFT_a+CAPFT_b*Chilled_Water_Supply_Temperature+CAPFT_c*Chilled_Water_Supply_Temperature**2+CAPFT_d*Condenser_Water_Leaving_Temperature+CAPFT_e*Condenser_Water_Leaving_Temperature**2+CAPFT_f*Chilled_Water_Supply_Temperature*Condenser_Water_Leaving_Temperature
            EIR = EIR_a+EIR_b*Chilled_Water_Supply_Temperature+EIR_c*Chilled_Water_Supply_Temperature**2+EIR_d*Condenser_Water_Leaving_Temperature+EIR_e*Condenser_Water_Leaving_Temperature**2+EIR_f*Chilled_Water_Supply_Temperature*Condenser_Water_Leaving_Temperature
        elif Condenser_Type == 'Air Cooled':
            CAPFT = CAPFT_a+CAPFT_b*Chilled_Water_Supply_Temperature+CAPFT_c*Chilled_Water_Supply_Temperature**2+CAPFT_d*Outside_Air_Temperature+CAPFT_e*Outside_Air_Temperature**2+CAPFT_f*Chilled_Water_Supply_Temperature*Outside_Air_Temperature
            EIR = EIR_a+EIR_b*Chilled_Water_Supply_Temperature+EIR_c*Chilled_Water_Supply_Temperature**2+EIR_d*Outside_Air_Temperature+EIR_e*Outside_Air_Temperature**2+EIR_f*Chilled_Water_Supply_Temperature*Outside_Air_Temperature

        # Calculate available cooling capacity
        Available_Capacity = Reference_Capacity*abs(CAPFT)
        Test_PLR = Hourly_Cooling/Available_Capacity

        if Test_PLR == 0:
            Power = 0
            Number_Units = 0
            PLR = 0
            EIRPLR = 0
            Rejected_Heat = 0
        elif Test_PLR < Maximum_Part_Load_Ratio:
            Number_Units = 1
            PLR = max(0.0, min(Hourly_Cooling/Available_Capacity, Maximum_Part_Load_Ratio))
            Chiller_Cycling_Ratio = min(PLR/Minimum_Part_Load_Ratio, 1.0)
            PLR = max(PLR, Minimum_Unloading_Ratio)
            False_Loading = Available_Capacity*PLR*Chiller_Cycling_Ratio-Hourly_Cooling
            EIRPLR = EIRPLR_a+EIRPLR_b*Condenser_Water_Leaving_Temperature+EIRPLR_c*Condenser_Water_Leaving_Temperature**2+EIRPLR_d*PLR+EIRPLR_e*PLR**2+EIRPLR_f*Condenser_Water_Leaving_Temperature*PLR+EIRPLR_g*Condenser_Water_Leaving_Temperature**3+EIRPLR_h*PLR**3+EIRPLR_i*Condenser_Water_Leaving_Temperature**2*PLR+EIRPLR_j*Condenser_Water_Leaving_Temperature*PLR**2
            Power = Available_Capacity/Reference_COP*EIR*EIRPLR*Chiller_Cycling_Ratio
            Rejected_Heat = Power*Compressor_Motor_Efficiency+Hourly_Cooling+False_Loading
        else:
            Number_Units = mp.ceil(Hourly_Cooling/(Available_Capacity*Maximum_Part_Load_Ratio))
            Unit_Hourly_Cooling = Hourly_Cooling/Number_Units
            PLR = max(0.0, min(Unit_Hourly_Cooling/Available_Capacity, Maximum_Part_Load_Ratio))
            Chiller_Cycling_Ratio = min(PLR/Minimum_Part_Load_Ratio, 1.0)
            PLR = max(PLR, Minimum_Unloading_Ratio)
            False_Loading = Available_Capacity*PLR*Chiller_Cycling_Ratio-Unit_Hourly_Cooling
            EIRPLR = EIRPLR_a+EIRPLR_b*Condenser_Water_Leaving_Temperature+EIRPLR_c*Condenser_Water_Leaving_Temperature**2+EIRPLR_d*PLR+EIRPLR_e*PLR**2+EIRPLR_f*Condenser_Water_Leaving_Temperature*PLR+EIRPLR_g*Condenser_Water_Leaving_Temperature**3+EIRPLR_h*PLR**3+EIRPLR_i*Condenser_Water_Leaving_Temperature**2*PLR+EIRPLR_j*Condenser_Water_Leaving_Temperature*PLR**2
            Power = Number_Units*Available_Capacity/Reference_COP*EIR*EIRPLR*Chiller_Cycling_Ratio
            Rejected_Heat = Power*Compressor_Motor_Efficiency+Hourly_Cooling+False_Loading*Number_Units

        # Calculate condenser fan energy if chiller is air cooled
        if Condenser_Type == 'Air Cooled':
            Electrical_Demand = Reference_Capacity*Condenser_Fan_Power_Ratio*Chiller_Cycling_Ratio
        else:
            Electrical_Demand = 0

        # Calculate COP
        if PLR == 0 or Power == 0:
            COP = 0
        else:
            COP = Hourly_Cooling/Power

        n += 1

    Cooling_Tower_Fan_Power = Rejected_Heat/1170*11.2
    Power += Electrical_Demand+Cooling_Tower_Fan_Power
    Heat_Input = 0.0

    Total_Cost = Capital_Cost/tons_to_kW*Reference_Capacity*Number_Units

    return [Number_Units, Power, Heat_Input, Hourly_Cooling, COP, Total_Cost, Heat_Recovery_Potential]
###### Auxiliary function end ######
    

def Chiller_Capacities():
    return(897.6, 1758.3, 2412.4, 3133.3, 4536.5, 5549.3, 756.0, 1171.0, 1758.3)


def Electric_Chiller_Small(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YT 207 kW 3.99 COP Electric Chiller with VSD. The methodology for
        calculating the operating point is defined by ASHRAE and explained in the HVAC Simulation Guidebook,
        Second Edition July 2012 originally prepared in 2007 for Pacific Gas and Electric by CTG Energetics
        as part of the the statewide Energy Design Resources program. Data and constants for the chiller from
        the Simulation Research Modelica Buildings Library Chiller Data from Lawrence Berkeley Lab.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Outside Wet Bulb Temperature: Celsius
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 12.0                   # kW
    Reference_COP = 3.00                        # Dimensionless (kW/kW)
    Reference_COW_Flow_Rate = 0.001122          # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.25              # Dimensionless
    Maximum_Part_Load_Ratio = 1.01              # Dimensionless
    Minimum_Unloading_Ratio = 0.25              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
    CAPFT_a = 0.9441897                         # Dimensionless regression constant
    CAPFT_b = 0.03371079                        # Dimensionless regression constant
    CAPFT_c = 0.00009756685                     # Dimensionless regression constant
    CAPFT_d = -0.003220573                      # Dimensionless regression constant
    CAPFT_e = -0.000004917369                   # Dimensionless regression constant
    CAPFT_f = -0.0001775717                     # Dimensionless regression constant
    EIR_a = 0.7273870                           # Dimensionless regression constant
    EIR_b = -0.01189276                         # Dimensionless regression constant
    EIR_c = 0.0005411677                        # Dimensionless regression constant
    EIR_d = 0.001879294                         # Dimensionless regression constant
    EIR_e = 0.0004734664                        # Dimensionless regression constant
    EIR_f = -0.0007114850                       # Dimensionless regression constant
    EIRPLR_a = 0.04146742                       # Dimensionless regression constant
    EIRPLR_b = 0.0                              # Dimensionless regression constant
    EIRPLR_c = 0.0                              # Dimensionless regression constant
    EIRPLR_d = 0.6543795                        # Dimensionless regression constant
    EIRPLR_e = 0.3044125                        # Dimensionless regression constant
    EIRPLR_f = 0.0                              # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = 0.0                              # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 720.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)
    
def Electric_Chiller_1(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YT 897 kW 6.27 COP Electric Chiller with VSD. The methodology for
        calculating the operating point is defined by ASHRAE and explained in the HVAC Simulation Guidebook,
        Second Edition July 2012 originally prepared in 2007 for Pacific Gas and Electric by CTG Energetics
        as part of the the statewide Energy Design Resources program. Data and constants for the chiller from
        the Simulation Research Modelica Buildings Library Chiller Data from Lawrence Berkeley Lab.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Outside Wet Bulb Temperature: Celsius
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 897.6                  # kW
    Reference_COP = 6.27                        # Dimensionless (kW/kW)
    #Reference_LCWT = 43.0                       # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 81.7                       # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.06782           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.05142           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.02              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.10              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = -0.1279200                        # Dimensionless regression constant
    CAPFT_b = 0.1653602                         # Dimensionless regression constant
    CAPFT_c = -0.004202474                      # Dimensionless regression constant
    CAPFT_d = 0.04807512                        # Dimensionless regression constant
    CAPFT_e = -0.0009553549                     # Dimensionless regression constant
    CAPFT_f = -0.002146733                      # Dimensionless regression constant
    EIR_a = 0.3276702                           # Dimensionless regression constant
    EIR_b = -0.07003986                         # Dimensionless regression constant
    EIR_c = 0.005261779                         # Dimensionless regression constant
    EIR_d = 0.07021494                          # Dimensionless regression constant
    EIR_e = -0.0007368698                       # Dimensionless regression constant
    EIR_f = -0.002109336                        # Dimensionless regression constant
    EIRPLR_a = -0.03773762                      # Dimensionless regression constant
    EIRPLR_b = 0.01134114                       # Dimensionless regression constant
    EIRPLR_c = -0.00002659425                   # Dimensionless regression constant
    EIRPLR_d = 0.2639446                        # Dimensionless regression constant
    EIRPLR_e = 0.4805824                        # Dimensionless regression constant
    EIRPLR_f = -0.01117502                      # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = 0.3000515                        # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 720.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)

def Electric_Chiller_2(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YT 1758 kW 5.96 COP Electric Chiller with Vanes. The methodology for
        calculating the operating point is defined by ASHRAE and elaborated in Hydeman, et al. (2002)
        "Development and Testing of a Reformulated Regression-Based Electric Chiller Model." Data and
        constants for the chiller from EnergyPlus v. 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Condenser Water Supply Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 1758.3                 # kW
    Reference_COP = 5.96                        # Dimensionless (kW/kW)
    #Reference_LCWT = 42.008                     # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 90.014                     # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.06309           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.06309           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.10              # Dimensionless
    Maximum_Part_Load_Ratio = 1.01              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.10              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = 0.80756668                        # Dimensionless regression constant
    CAPFT_b = 0.05287917                        # Dimensionless regression constant
    CAPFT_c = -0.0004493793                     # Dimensionless regression constant
    CAPFT_d = 0.007036068                       # Dimensionless regression constant
    CAPFT_e = -0.0003536822                     # Dimensionless regression constant
    CAPFT_f = 0.0003731438                      # Dimensionless regression constant
    EIR_a = 0.2593808                           # Dimensionless regression constant
    EIR_b = -0.001873181                        # Dimensionless regression constant
    EIR_c = -0.0004808688                       # Dimensionless regression constant
    EIR_d = 0.03822020                          # Dimensionless regression constant
    EIR_e = -0.0003813018                       # Dimensionless regression constant
    EIR_f = -0.0002995903                       # Dimensionless regression constant
    EIRPLR_a = 0.1303414                        # Dimensionless regression constant
    EIRPLR_b = 0.01618347                       # Dimensionless regression constant
    EIRPLR_c = -0.00007157278                   # Dimensionless regression constant
    EIRPLR_d = -0.1337481                       # Dimensionless regression constant
    EIRPLR_e = 1.186910                         # Dimensionless regression constant
    EIRPLR_f = -0.01240299                      # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = -0.2328976                       # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 525.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)

def Electric_Chiller_3(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YK 2412 kW 5.58 COP Electric Chiller with Vanes. The methodology for
        calculating the operating point is defined by ASHRAE and elaborated in Hydeman, et al. (2002)
        "Development and Testing of a Reformulated Regression-Based Electric Chiller Model." Data and
        constants for the chiller from EnergyPlus v. 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Condenser Water Supply Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 2412.4                 # kW
    Reference_COP = 5.58                        # Dimensionless (kW/kW)
    #Reference_LCWT = 44.0                       # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 89.78                      # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.09085           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.11356           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.12              # Dimensionless
    Maximum_Part_Load_Ratio = 1.01              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.12              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = 0.6042244                         # Dimensionless regression constant
    CAPFT_b = -0.005282819                      # Dimensionless regression constant
    CAPFT_c = -0.000199374                      # Dimensionless regression constant
    CAPFT_d = 0.02972266                        # Dimensionless regression constant
    CAPFT_e = -0.0008288016                     # Dimensionless regression constant
    CAPFT_f = 0.001587869                       # Dimensionless regression constant
    EIR_a = 0.3175495                           # Dimensionless regression constant
    EIR_b = -0.02563749                         # Dimensionless regression constant
    EIR_c = 0.001177157                         # Dimensionless regression constant
    EIR_d = 0.03422467                          # Dimensionless regression constant
    EIR_e = -0.0002556973                       # Dimensionless regression constant
    EIR_f = -0.0001034934                       # Dimensionless regression constant
    EIRPLR_a = -0.08659288                      # Dimensionless regression constant
    EIRPLR_b = 0.04280342                       # Dimensionless regression constant
    EIRPLR_c = 0.00004027354                    # Dimensionless regression constant
    EIRPLR_d = -0.8726041                       # Dimensionless regression constant
    EIRPLR_e = 3.432389                         # Dimensionless regression constant
    EIRPLR_f = -0.04514744                      # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = -1.440179                        # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 475.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)

def Electric_Chiller_4(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YT 3133 kW 9.16 COP Electric Chiller with Vanes. The methodology for
        calculating the operating point is defined by ASHRAE and elaborated in Hydeman, et al. (2002)
        "Development and Testing of a Reformulated Regression-Based Electric Chiller Model." Data and
        constants for the chiller from EnergyPlus v. 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Condenser Water Supply Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 3133.3                 # kW
    Reference_COP = 9.16                        # Dimensionless (kW/kW)
    #Reference_LCWT = 42.0                       # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 66.866                     # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.08076           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.12618           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.07              # Dimensionless
    Maximum_Part_Load_Ratio = 1.04              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.07              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = 0.6112157                         # Dimensionless regression constant
    CAPFT_b = -0.01430728                       # Dimensionless regression constant
    CAPFT_c = 0.00009823748                     # Dimensionless regression constant
    CAPFT_d = 0.03293543                        # Dimensionless regression constant
    CAPFT_e = -0.001221859                      # Dimensionless regression constant
    CAPFT_f = 0.002659301                       # Dimensionless regression constant
    EIR_a = 0.8749714                           # Dimensionless regression constant
    EIR_b = -0.02881975                         # Dimensionless regression constant
    EIR_c = 0.002003695                         # Dimensionless regression constant
    EIR_d = 0.007313755                         # Dimensionless regression constant
    EIR_e = 0.0005578288                        # Dimensionless regression constant
    EIR_f = -0.001170615                        # Dimensionless regression constant
    EIRPLR_a = 0.3389568                        # Dimensionless regression constant
    EIRPLR_b = -0.01864923                      # Dimensionless regression constant
    EIRPLR_c = 0.0003548361                     # Dimensionless regression constant
    EIRPLR_d = 1.107404                         # Dimensionless regression constant
    EIRPLR_e = -0.5912797                       # Dimensionless regression constant
    EIRPLR_f = -0.0004559304                    # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = 0.3910858                        # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 550.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)

def Electric_Chiller_5(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YK 4537 kW 6.28 COP Electric Chiller with Vanes. The methodology for
        calculating the operating point is defined by ASHRAE and elaborated in Hydeman, et al. (2002)
        "Development and Testing of a Reformulated Regression-Based Electric Chiller Model." Data and
        constants for the chiller from EnergyPlus v. 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Condenser Water Supply Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
            Number Iterations: Dimensionless number of iterations to converge on energy use
    '''
    Reference_Capacity = 4536.5                 # kW
    Reference_COP = 6.28                        # Dimensionless (kW/kW)
    #Reference_LCWT = 44.0                       # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 89.204                     # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.19558           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.24605           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.40              # Dimensionless
    Maximum_Part_Load_Ratio = 1.04              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.40              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = 0.1769339                         # Dimensionless regression constant
    CAPFT_b = 0.0008033367                      # Dimensionless regression constant
    CAPFT_c = -0.01299649                       # Dimensionless regression constant
    CAPFT_d = 0.1160227                         # Dimensionless regression constant
    CAPFT_e = -0.004192731                      # Dimensionless regression constant
    CAPFT_f = 0.009339837                       # Dimensionless regression constant
    EIR_a = 0.8920183                           # Dimensionless regression constant
    EIR_b = -0.01501518                         # Dimensionless regression constant
    EIR_c = 0.001467430                         # Dimensionless regression constant
    EIR_d = -0.01261335                         # Dimensionless regression constant
    EIR_e = 0.0008431355                        # Dimensionless regression constant
    EIR_f = -0.001426299                        # Dimensionless regression constant
    EIRPLR_a = 0.1718938                        # Dimensionless regression constant
    EIRPLR_b = 0.006637990                      # Dimensionless regression constant
    EIRPLR_c = 0.00001666991                    # Dimensionless regression constant
    EIRPLR_d = 0.1634153                        # Dimensionless regression constant
    EIRPLR_e = 0.9517270                        # Dimensionless regression constant
    EIRPLR_f = -0.007705773                     # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = -0.2724672                       # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 510.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)

def Electric_Chiller_6(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YK 5549 kW 6.50 COP Electric Chiller with Vanes. The methodology for
        calculating the operating point is defined by ASHRAE and elaborated in Hydeman, et al. (2002)
        "Development and Testing of a Reformulated Regression-Based Electric Chiller Model." Data and
        constants for the chiller from EnergyPlus v. 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Condenser Water Supply Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 5549.3                 # kW
    Reference_COP = 6.50                        # Dimensionless (kW/kW)
    #Reference_LCWT = 44.0                       # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 89.042                     # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.18296           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.27444           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.14              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.14              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = -0.8620027                        # Dimensionless regression constant
    CAPFT_b = 0.006692796                       # Dimensionless regression constant
    CAPFT_c = -0.004020156                      # Dimensionless regression constant
    CAPFT_d = 0.1550060                         # Dimensionless regression constant
    CAPFT_e = -0.003586968                      # Dimensionless regression constant
    CAPFT_f = 0.003027128                       # Dimensionless regression constant
    EIR_a = 0.3302868                           # Dimensionless regression constant
    EIR_b = -0.08254126                         # Dimensionless regression constant
    EIR_c = 0.006087519                         # Dimensionless regression constant
    EIR_d = 0.04875213                          # Dimensionless regression constant
    EIR_e = -0.0005839053                       # Dimensionless regression constant
    EIR_f = -0.00005006909                      # Dimensionless regression constant
    EIRPLR_a = 0.5179058                        # Dimensionless regression constant
    EIRPLR_b = -0.002419877                     # Dimensionless regression constant
    EIRPLR_c = 0.00004858626                    # Dimensionless regression constant
    EIRPLR_d = -0.8910290                       # Dimensionless regression constant
    EIRPLR_e = 2.272953                         # Dimensionless regression constant
    EIRPLR_f = -0.0003062303                    # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = -0.8631289                       # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 500.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)

def Electric_Chiller_7(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YS 756 kW 7.41 COP Electric Chiller with Valves. The methodology for
        calculating the operating point is defined by ASHRAE and elaborated in Hydeman, et al. (2002)
        "Development and Testing of a Reformulated Regression-Based Electric Chiller Model." Data and
        constants for the chiller from EnergyPlus v. 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Condenser Water Supply Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 756.0                  # kW
    Reference_COP = 7.41                        # Dimensionless (kW/kW)
    #Reference_LCWT = 42.008                     # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 68.09                      # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.06782           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.05142           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.11              # Dimensionless
    Maximum_Part_Load_Ratio = 1.01              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.11              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = 0.9642889                         # Dimensionless regression constant
    CAPFT_b = 0.02866413                        # Dimensionless regression constant
    CAPFT_c = 0.0003109129                      # Dimensionless regression constant
    CAPFT_d = -0.005631322                      # Dimensionless regression constant
    CAPFT_e = -0.00003762572                    # Dimensionless regression constant
    CAPFT_f = -0.00005237190                    # Dimensionless regression constant
    EIR_a = 0.6354619                           # Dimensionless regression constant
    EIR_b = -0.01370325                         # Dimensionless regression constant
    EIR_c = 0.001593968                         # Dimensionless regression constant
    EIR_d = 0.01156358                          # Dimensionless regression constant
    EIR_e = 0.0009449231                        # Dimensionless regression constant
    EIR_f = -0.001967502                        # Dimensionless regression constant
    EIRPLR_a = -1.261074                        # Dimensionless regression constant
    EIRPLR_b = 0.1245378                        # Dimensionless regression constant
    EIRPLR_c = -0.0001028560                    # Dimensionless regression constant
    EIRPLR_d = 0.6936120                        # Dimensionless regression constant
    EIRPLR_e = 0.5828942                        # Dimensionless regression constant
    EIRPLR_f = -0.1203584                       # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = 0.9427000                        # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 800.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)

def Electric_Chiller_8(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YS 1171 kW 9.15 COP Electric Chiller with Valves. The methodology for
        calculating the operating point is defined by ASHRAE and elaborated in Hydeman, et al. (2002)
        "Development and Testing of a Reformulated Regression-Based Electric Chiller Model." Data and
        constants for the chiller from EnergyPlus v. 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Condenser Water Supply Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 1171.0                 # kW
    Reference_COP = 9.15                        # Dimensionless (kW/kW)
    #Reference_LCWT = 43.0                       # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 70.808                     # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.03249           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.05173           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.09              # Dimensionless
    Maximum_Part_Load_Ratio = 1.01              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.09              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = 0.9337294                         # Dimensionless regression constant
    CAPFT_b = 0.01920636                        # Dimensionless regression constant
    CAPFT_c = -0.0006115577                     # Dimensionless regression constant
    CAPFT_d = -0.0007771906                     # Dimensionless regression constant
    CAPFT_e = -0.0002483077                     # Dimensionless regression constant
    CAPFT_f = 0.0007872535                      # Dimensionless regression constant
    EIR_a = 0.3293911                           # Dimensionless regression constant
    EIR_b = -0.02105626                         # Dimensionless regression constant
    EIR_c = 0.001769048                         # Dimensionless regression constant
    EIR_d = 0.03636950                          # Dimensionless regression constant
    EIR_e = 0.0004158157                        # Dimensionless regression constant
    EIR_f = -0.001853560                        # Dimensionless regression constant
    EIRPLR_a = -0.2154861                       # Dimensionless regression constant
    EIRPLR_b = 0.03786873                       # Dimensionless regression constant
    EIRPLR_c = -0.00001127341                   # Dimensionless regression constant
    EIRPLR_d = 0.2109726                        # Dimensionless regression constant
    EIRPLR_e = 1.287825                         # Dimensionless regression constant
    EIRPLR_f = -0.03728032                      # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = -0.2909471                       # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 750.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)

def Electric_Chiller_9(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature):
    ''' Data and operation for a York YS 1758 kW 5.84 COP Electric Chiller with Valves. The methodology for
        calculating the operating point is defined by ASHRAE and elaborated in Hydeman, et al. (2002)
        "Development and Testing of a Reformulated Regression-Based Electric Chiller Model." Data and
        constants for the chiller from EnergyPlus v. 8-0-0.

        Required input units:
            Chilled Water Supply Temperature: Fahrenheit
            Condenser Water Supply Temperature: Fahrenheit
            Outside Air Temperature: Fahrenheit
            Hourly Cooling: kWh
    '''
    Reference_Capacity = 1758.3                 # kW
    Reference_COP = 5.84                        # Dimensionless (kW/kW)
    #Reference_LCWT = 44.0                       # Fahrenheit (Leaving Chilled Water Temperature)
    #Reference_LCFT = 94.37                      # Fahrenheit (Leaving Condenser Fluid Temperature)
#    Reference_CHW_Flow_Rate = 0.07571           # m3/s (Chilled Water)
    Reference_COW_Flow_Rate = 0.09464           # m3/s (Condenser Water)
    Minimum_Part_Load_Ratio = 0.20              # Dimensionless
    Maximum_Part_Load_Ratio = 1.05              # Dimensionless
#    Optimum_Part_Load_Ratio = 1.0               # Dimensionless
    Minimum_Unloading_Ratio = 0.20              # Dimensionless
    Condenser_Type = 'Water Cooled'             # 'Water Cooled' or 'Air Cooled'
    Condenser_Fan_Power_Ratio = 0.0             # Dimensionless (kW/kW)
    Compressor_Motor_Efficiency = 1.0           # Dimensionless
#    LCWT_Lower_Limit = 35.6                     # Fahrenheit (Leaving Chilled Water Temperature)
#    Flow_Mode = 'Constant'                      # 'Constant' or 'Variable'
#    Heat_Recovery_Water_Flow_Rate = 0.0         # m3/s
    CAPFT_a = 0.6348511                         # Dimensionless regression constant
    CAPFT_b = -0.02523830                       # Dimensionless regression constant
    CAPFT_c = -0.001840036                      # Dimensionless regression constant
    CAPFT_d = 0.03830396                        # Dimensionless regression constant
    CAPFT_e = -0.0009961929                     # Dimensionless regression constant
    CAPFT_f = 0.001906565                       # Dimensionless regression constant
    EIR_a = 0.7492787                           # Dimensionless regression constant
    EIR_b = 0.01912506                          # Dimensionless regression constant
    EIR_c = 0.001303486                         # Dimensionless regression constant
    EIR_d = -0.01981703                         # Dimensionless regression constant
    EIR_e = 0.001003666                         # Dimensionless regression constant
    EIR_f = -0.001936814                        # Dimensionless regression constant
    EIRPLR_a = -0.1522140                       # Dimensionless regression constant
    EIRPLR_b = 0.02440667                       # Dimensionless regression constant
    EIRPLR_c = -0.00005691764                   # Dimensionless regression constant
    EIRPLR_d = 0.4875495                        # Dimensionless regression constant
    EIRPLR_e = 0.7490485                        # Dimensionless regression constant
    EIRPLR_f = -0.02093720                      # Dimensionless regression constant
    EIRPLR_g = 0.0                              # Dimensionless regression constant
    EIRPLR_h = -0.1319819                       # Dimensionless regression constant
    EIRPLR_i = 0.0                              # Dimensionless regression constant
    EIRPLR_j = 0.0                              # Dimensionless regression constant
    Cooling_Tower_Approach = 5.0                # Fahrenheit
    Capital_Cost = 525.0                        # USD/ton

    return Computer(Chilled_Water_Supply_Temperature, Outside_Wet_Bulb, Outside_Air_Temperature, Hourly_Cooling, Number_Iterations, Heat_Source_Temperature, Reference_Capacity, Reference_COP, Reference_COW_Flow_Rate, Minimum_Part_Load_Ratio, Maximum_Part_Load_Ratio, Minimum_Unloading_Ratio, Condenser_Type, Condenser_Fan_Power_Ratio, Compressor_Motor_Efficiency, CAPFT_a, CAPFT_b, CAPFT_c, CAPFT_d, CAPFT_e, CAPFT_f, EIR_a, EIR_b, EIR_c, EIR_d, EIR_e, EIR_f, EIRPLR_a, EIRPLR_b, EIRPLR_c, EIRPLR_d, EIRPLR_e, EIRPLR_f, EIRPLR_g, EIRPLR_h, EIRPLR_i, EIRPLR_j, Cooling_Tower_Approach, Capital_Cost)