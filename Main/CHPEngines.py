from __future__ import division

#-------------------------------------------------------------------------------
# Name:        CCHPEngines
# Purpose:     File full of CCHP engine simulations for use in urban
#              optimization code.
#
# Author:      Rob Best
# Modifier:    Pouya Rezazadeh
#
# Created:     23/07/2015
# Modified:    06/01/2019
# Copyright:   (c) Rob Best 2015
#-------------------------------------------------------------------------------


### NOTE: Must uncomment the lines for other gas line pressures if you change it to s'th other than 55 Pa


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


ft3_to_Btu_Nat_Gas = 1037			# https://www.eia.gov/tools/faqs/faq.php?id=45&t=8
kg_to_Btu_H2 = 115119				# https://www.nrel.gov/docs/gen/fy08/43061.pdf
ton_to_Btu_Biomass = 5.74*10**6		# https://www.fpl.fs.fed.us/documnts/techline/fuel-value-calculator.pdf
LHV_Natural_Gas = 47100000.00       # Lower heating value of natural gas (J/kg) ## updated from engineeringtoolbox (Apr 2019)
Specific_Heat_Water = 4216.00       # Specific heat of water at STP (J/kg-C) ## updated from engineeringtoolbox (Apr 2019)
Density_Water = 999.9               # Density of liquid water (kg/m^3)

Natural_Gas_Emissions = 117.0       # CO2 emissions for natural gas combustion (lbs/MMBtu) # Checked June 2019 with https://www.epa.gov/sites/production/files/2018-03/documents/emission-factors_mar_2018_0.pdf

USD_2007_to_2019 = 1.23             # From http://www.in2013dollars.com/2007-dollars-in-2019

'''-----------------------------------------------------------------------------------------------'''
# CHP Parameters #
'''-----------------------------------------------------------------------------------------------'''
Gas_Line_Pressure = 55.0            # psi
Natural_Gas_Cost = 7.05/ft3_to_Btu_Nat_Gas 	# $/Btu 2017 avg industrial gas price from https://www.eia.gov/dnav/ng/ng_pri_sum_dcu_SCA_a.htm # Old value: 0.000006
Hydrogen_Cost = 15/kg_to_Btu_H2  			# $/Btu   # retail price from https://cafcp.org/sites/default/files/CAFCR.pdf # Old price 0.000044
Biomass_Cost = 30/ton_to_Btu_Biomass		# $/Btu		# https://www.eia.gov/biofuels/biomass/?year=2018&month=12#table_data # Old price 0.000002 


''' Note: Cooling tower in chillers comes from http://www.taylor-engineering.com/downloads/articles/ASHRAE%20Symposium%20AC-02-9-4%20Cooling%20Tower%20Model-Hydeman.pdf'''


###### AUXILIARY FUNCTION START #######
def Computer(engine, Conts, Electrical_Capacity, Basic_Installed_Cost, Installed_Cost_SCR, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, Compressor_Parasitic_Power):
    if Hourly_Electricity <= 0: ## handling hours with trivial consumption
        return [0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    Basic_Installed_Cost *= USD_2007_to_2019
    Installed_Cost_SCR *= USD_2007_to_2019
    Total_O_and_M_Cost *= USD_2007_to_2019
    
    if 'bio' in engine:
        # Calculate base line electrical efficiency
        Electrical_Capacity_MMBtu = Electrical_Capacity*kWh_to_Btu/1000000
        Electrical_Efficiency = Electrical_Capacity_MMBtu/Fuel_Input*100
        
    # Store hourly electricity
    Hourly_Electrical_Consumption = Hourly_Electricity ## It's not deep copied! It changes the input!

    # Derate available electrical capacity for altitude
    Updated_Electrical_Capacity = (-1.0/300*Altitude+100.0)/100*Electrical_Capacity
    Altitude_Derate = Updated_Electrical_Capacity/Electrical_Capacity
    Electrical_Capacity = Updated_Electrical_Capacity

    if 'gas' in engine: ## For gas turbines
        # Derate available electrical capacity for ambient temperature
        Electrical_Capacity = (-1.0/6*Ambient_Temperature+110)/100*Electrical_Capacity

        # Calculate the power requirement for gas compression based on line pressure, an input to the function
        if engine == 'gas1':
            if Gas_Line_Pressure == 55:
                Gas_Compression_Power = 8.0             # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+416000/Electrical_Capacity
        elif engine == 'gas2':
            if Gas_Line_Pressure == 55:
                Gas_Compression_Power = 82.0            # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+937000/Electrical_Capacity
            #elif Gas_Line_Pressure == 150:
                #Gas_Compression_Power = 35.0            # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+400000/Electrical_Capacity
        elif engine == 'gas3':
            if Gas_Line_Pressure == 55:
                Gas_Compression_Power = 198.0           # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+1182000/Electrical_Capacity
            #elif Gas_Line_Pressure == 150:
                #Gas_Compression_Power = 58.0            # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+346000/Electrical_Capacity
            #elif Gas_Line_Pressure == 250:
                #Gas_Compression_Power = 22.0            # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+131000/Electrical_Capacity
        elif engine == 'gas4':
            if Gas_Line_Pressure == 55:
                Gas_Compression_Power = 536.0           # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+1223500/Electrical_Capacity
            #elif Gas_Line_Pressure == 150:
                #Gas_Compression_Power = 300.0           # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+684794/Electrical_Capacity
            #elif Gas_Line_Pressure == 250:
                #Gas_Compression_Power = 150.0           # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+342397/Electrical_Capacity
        elif engine == 'gas5':
            if Gas_Line_Pressure == 55:
                Gas_Compression_Power = 859.0           # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+1797900/Electrical_Capacity
            #elif Gas_Line_Pressure == 150:
                #Gas_Compression_Power = 673.0           # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+1408599/Electrical_Capacity
            #elif Gas_Line_Pressure == 250:
                #Gas_Compression_Power = 380.0           # kW
                #Basic_Installed_Cost = Basic_Installed_Cost+795345/Electrical_Capacity
        else:
            Gas_Compression_Power = 0
        Hourly_Electricity = Hourly_Electricity+Gas_Compression_Power
    elif 'micro' in engine: ## For micro turbines
        # Derate available electrical capacity for ambient temperature
        if engine == 'micro1':
            Electrical_Capacity = (-2.0/7*Ambient_Temperature+100)/100*Electrical_Capacity
        elif ((engine == 'micro2') or (engine == 'micro3')):
            Electrical_Capacity = (-1.0/2*Ambient_Temperature+130)/100*Electrical_Capacity
        # Calculate derated electrical capacity for parasitic losses ## MODIFIED: INCLUDED FOR Micro 1 & 2, it was only included for 3!
        Hourly_Electricity = Hourly_Electricity+Compressor_Parasitic_Power
    elif (('recip' in engine) or ('cell' in engine) or ('bio' in engine)):
        # Derate available electrical capacity for ambient temperature
        Electrical_Capacity = (-1.0/6*Ambient_Temperature+110)/100*Electrical_Capacity
    elif 'steam' in engine:
        # Derate available electrical capacity for ambient temperature
        Electrical_Capacity = (-1.0/6*Ambient_Temperature+110)/100*Electrical_Capacity
        
        # Reduction in maximum capacity due to pump input
        Electrical_Capacity = Electrical_Capacity-Electrical_Capacity*0.006
    
    
    # Calculate electrical efficiency from part load
    Num_Engines = mp.ceil(Hourly_Electricity/Electrical_Capacity)
# =============================================================================
#     if Num_Engines <= Max_Engines:
#         Part_Load = Hourly_Electricity/(Num_Engines*Electrical_Capacity)*100    # Percent
#         if Part_Load < min_PLR:
#             Part_Load = min_PLR
#             Updated_Electrical_Efficiency = Conts[0]*Part_Load**3+Conts[1]*Part_Load**2+Conts[2]*Part_Load+Conts[3]
#         else:
#             Updated_Electrical_Efficiency = Conts[0]*Part_Load**3+Conts[1]*Part_Load**2+Conts[2]*Part_Load+Conts[3]
#     else:
#         Part_Load = 100
#         Num_Engines = Max_Engines
#         Updated_Electrical_Efficiency = Conts[0]*Part_Load**3+Conts[1]*Part_Load**2+Conts[2]*Part_Load+Conts[3]
# =============================================================================
    
    Part_Load = Hourly_Electricity/(Num_Engines*Electrical_Capacity)*100    # Percent
    if Part_Load < min_PLR:
        Part_Load = min_PLR
        Updated_Electrical_Efficiency = Conts[0]*Part_Load**3+Conts[1]*Part_Load**2+Conts[2]*Part_Load+Conts[3]
    else:
        Updated_Electrical_Efficiency = Conts[0]*Part_Load**3+Conts[1]*Part_Load**2+Conts[2]*Part_Load+Conts[3]


    if 'gas' in engine:
        Maximum_Electrical_Production = Part_Load*Num_Engines*Electrical_Capacity/100-Gas_Compression_Power ## Is it correct to subtract the gas_compression while it has already been used in finding the part load?
    else:
        Maximum_Electrical_Production = Part_Load*Num_Engines*Electrical_Capacity/100
            
    # Derate electrical efficiency from altitude
    Updated_Electrical_Efficiency = Updated_Electrical_Efficiency*Altitude_Derate

    # Derate efficiency from ambient air temperature
    if 'micro' in engine:
        if engine == 'micro1':
            cont = 31
        elif ((engine == 'micro2') or (engine == 'micro3')):
            cont = 20
        Updated_Electrical_Efficiency = (-1.0/cont*Ambient_Temperature+Conts[4])/Electrical_Efficiency*Updated_Electrical_Efficiency
    else:
        Updated_Electrical_Efficiency = (-9.0/250*Ambient_Temperature+Conts[4])/Electrical_Efficiency*Updated_Electrical_Efficiency
        

    # Calculate upramp or downramp for the hour (which is attributed to this hour solely)
    if Num_Engines > Num_Engines_Last_T:
        Delta_Engines = Num_Engines-Num_Engines_Last_T
        Ramp_Minutes = Part_Load*Electrical_Capacity/100/Ramp_Rate
        Ramp_Energy = 0.5*Ramp_Minutes*Part_Load*Electrical_Capacity/100*Delta_Engines/60
        if Part_Load > Part_Load_Last_T:
            Delta_Part_Load = Part_Load-Part_Load_Last_T
            Ramp_Minutes = Delta_Part_Load*Electrical_Capacity/100/Ramp_Rate
            Ramp_Energy += 0.5*Ramp_Minutes*Delta_Part_Load*Electrical_Capacity/100*Num_Engines_Last_T/60
        else:
            Delta_Part_Load = Part_Load_Last_T-Part_Load
            Ramp_Minutes = Delta_Part_Load*Electrical_Capacity/100/Ramp_Rate
            Ramp_Energy += 0.5*Ramp_Minutes*Delta_Part_Load*Electrical_Capacity/100*Num_Engines_Last_T/60
    else:
        Delta_Engines = Num_Engines_Last_T-Num_Engines
        Ramp_Minutes = Part_Load_Last_T*Electrical_Capacity/100/Ramp_Rate
        Ramp_Energy = 0.5*Ramp_Minutes*Part_Load_Last_T*Electrical_Capacity/100*Delta_Engines/60
        if Part_Load > Part_Load_Last_T:
            Delta_Part_Load = Part_Load-Part_Load_Last_T
            Ramp_Minutes = Delta_Part_Load*Electrical_Capacity/100/Ramp_Rate
            Ramp_Energy += 0.5*Ramp_Minutes*Delta_Part_Load*Electrical_Capacity/100*Num_Engines/60
        else:
            Delta_Part_Load = Part_Load_Last_T-Part_Load
            Ramp_Minutes = Delta_Part_Load*Electrical_Capacity/100/Ramp_Rate
            Ramp_Energy += 0.5*Ramp_Minutes*Delta_Part_Load*Electrical_Capacity/100*Num_Engines/60

    # Calculate maximum electrical and heat output
    Heat_Rate = kWh_to_Btu/(Updated_Electrical_Efficiency/100)
    Fuel_Input = Heat_Rate*(Part_Load/100*Num_Engines*Electrical_Capacity+Ramp_Energy)   # Btu
    HRR = (Total_CHP_Efficiency-Electrical_Efficiency)/(100-Electrical_Efficiency)
    Maximum_Heat_Production = (Fuel_Input/kWh_to_Btu-Maximum_Electrical_Production)*HRR    # kWh

    # Calculate costs and emissions of interest
    Capital_Cost = Num_Engines*Electrical_Capacity*Installed_Cost_SCR
    
    if 'cell' in engine:
        Variable_Cost = Hourly_Electrical_Consumption*Total_O_and_M_Cost+Fuel_Input*Hydrogen_Cost
    elif 'bio' in engine:
        Variable_Cost = Hourly_Electrical_Consumption*(Total_O_and_M_Cost) ## Total_O_and_M_Cost = (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M)
    else:
        Variable_Cost = Hourly_Electrical_Consumption*Total_O_and_M_Cost+Fuel_Input*Natural_Gas_Cost
        
    if 'steam' in engine:
        Carbon_Emissions = CO2*(Fuel_Input/1000000)
    else: 
        Carbon_Emissions = CO2*(Hourly_Electrical_Consumption/1000) # In lbs
        
    return [Fuel_Input, Hourly_Electrical_Consumption, Maximum_Heat_Production, Maximum_Electrical_Production, Capital_Cost, Variable_Cost, Carbon_Emissions, Num_Engines, Part_Load] 
#### AUXILIARY FUNCTION END ######



def EPA_CHP_Gas_Turbine_1(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Gas Turbine System 1. Simulates a Solar Turbines Saturn 20 - 1 MW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 1150.0                # kW
    Basic_Installed_Cost = 3324.0               # 2007 USD/kW
    Installed_Cost_SCR = 5221.0                 # 2007 USD/kW
#    Heat_Rate = 16047.0                         # Btu/kWh HHV
    Electrical_Efficiency = 21.27               # Percent, HHV
    Fuel_Input = 18.5                           # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 82.6           # psig
#    Exhaust_Flow = 51.4                         # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 951.0              # Fahrenheit
#    HRSG_Exhaust_Temperature = 309.0            # Fahrenheit
#    Steam_Output_MMBtu = 8.31                   # MMBtu/hr
#    Steam_Output_lbs = 8.26                     # 1,000 lbs/hr
#    Steam_Output_kW = 2435.0                    # kW equivalent
    Total_CHP_Efficiency = 66.3                 # Percent, HHV
#    Power_Heat_Ratio = 0.47                     # Dimensionless
#    Net_Heat_Rate = 7013.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 49.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0111                 # $/kWh
#    NOx = 2.43                                  # lbs/MWh
#    CO = 0.71                                   # lbs/MWh
    CO2 = 1877.0                                # lbs/MWh
#    Total_Carbon = 512.0                        # lbs/MWh
    Conts = [0.00002, -0.005, 0.4865, 4.4641, 23.43]   # Regression constants
    min_PLR = 10.0
    engine = 'gas1'                            # Identifier for the auxiliary function
    
    return Computer(engine, Conts, Electrical_Capacity, Basic_Installed_Cost, Installed_Cost_SCR, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Gas_Turbine_2(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Gas Turbine System 2. Simulates a Solar Turbines Taurus 60 - 5 MW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 5457.0                # kW
    Basic_Installed_Cost = 1314.0               # 2007 USD/kW
    Installed_Cost_SCR = 2210.0                 # 2007 USD/kW
#    Heat_Rate = 12312.0                         # Btu/kWh HHV
    Electrical_Efficiency = 27.72               # Percent, HHV
    Fuel_Input = 67.2                           # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 216.0          # psig
#    Exhaust_Flow = 170.8                        # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 961.0              # Fahrenheit
#    HRSG_Exhaust_Temperature = 307.0            # Fahrenheit
#    Steam_Output_MMBtu = 28.26                  # MMBtu/hr
#    Steam_Output_lbs = 28.09                    # 1,000 lbs/hr
#    Steam_Output_kW = 8279.0                    # kW equivalent
    Total_CHP_Efficiency = 69.8                 # Percent, HHV
#    Power_Heat_Ratio = 0.66                     # Dimensionless
#    Net_Heat_Rate = 5839.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 58.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0074                 # $/kWh
#    NOx = 0.66                                  # lbs/MWh
#    CO = 0.68                                   # lbs/MWh
    CO2 = 1440.0                                # lbs/MWh
#    Total_Carbon = 393.0                        # lbs/MWh
    Conts = [0.00002, -0.0065, 0.634, 5.8179, 29.88]   # Regression constants
    min_PLR = 10.0
    engine = 'gas2'                            # Identifier for the auxiliary function
    
    return Computer(engine, Conts, Electrical_Capacity, Basic_Installed_Cost, Installed_Cost_SCR, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Gas_Turbine_3(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Gas Turbine System 3. Simulates a Solar Turbines Mars 100 - 10 MW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 10239.0               # kW
    Basic_Installed_Cost = 1298.0               # 2007 USD/kW
    Installed_Cost_SCR = 1965.0                 # 2007 USD/kW
#    Heat_Rate = 12001.0                         # Btu/kWh HHV
    Electrical_Efficiency = 28.44               # Percent, HHV
    Fuel_Input = 122.9                          # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 317.6          # psig
#    Exhaust_Flow = 328.2                        # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 916.0              # Fahrenheit
#    HRSG_Exhaust_Temperature = 322.0            # Fahrenheit
#    Steam_Output_MMBtu = 49.10                  # MMBtu/hr
#    Steam_Output_lbs = 48.80                    # 1,000 lbs/hr
#    Steam_Output_kW = 14385.0                   # kW equivalent
    Total_CHP_Efficiency = 68.4                 # Percent, HHV
#    Power_Heat_Ratio = 0.71                     # Dimensionless
#    Net_Heat_Rate = 6007.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 57.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0070                 # $/kWh
#    NOx = 0.65                                  # lbs/MWh
#    CO = 0.66                                   # lbs/MWh
    CO2 = 1404.0                                # lbs/MWh
#    Total_Carbon = 383.0                        # lbs/MWh
    Conts = [0.00002, -0.0067, 0.6505, 5.969, 30.6]   # Regression constants
    min_PLR = 10.0
    engine = 'gas3'                            # Identifier for the auxiliary function

    return Computer(engine, Conts, Electrical_Capacity, Basic_Installed_Cost, Installed_Cost_SCR, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Gas_Turbine_4(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Gas Turbine System 4. Simulates a GE LM2500+ - 25 MW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 25000.0               # kW
    Basic_Installed_Cost = 1097.0               # 2007 USD/kW
    Installed_Cost_SCR = 1516.0                 # 2007 USD/kW
#    Heat_Rate = 9945.0                          # Btu/kWh HHV
    Electrical_Efficiency = 34.30               # Percent, HHV
    Fuel_Input = 248.6                          # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 340.0          # psig
#    Exhaust_Flow = 571.0                        # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 950.0              # Fahrenheit
#    HRSG_Exhaust_Temperature = 280.0            # Fahrenheit
#    Steam_Output_MMBtu = 90.34                  # MMBtu/hr
#    Steam_Output_lbs = 89.80                    # 1,000 lbs/hr
#    Steam_Output_kW = 26469.0                   # kW equivalent
    Total_CHP_Efficiency = 70.7                 # Percent, HHV
#    Power_Heat_Ratio = 0.94                     # Dimensionless
#    Net_Heat_Rate = 5427.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 63.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0049                 # $/kWh
#    NOx = 0.90                                  # lbs/MWh
#    CO = 0.55                                   # lbs/MWh
    CO2 = 1163.0                                # lbs/MWh
#    Total_Carbon = 317.0                        # lbs/MWh
    Conts = [0.00003, -0.0081, 0.7845, 7.1989, 36.4]   # Regression constants
    min_PLR = 10.0
    engine = 'gas4'                            # Identifier for the auxiliary function

    return Computer(engine, Conts, Electrical_Capacity, Basic_Installed_Cost, Installed_Cost_SCR, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Gas_Turbine_5(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Gas Turbine System 5. Simulates a GE LM26000PD - 40 MW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 40000.0               # kW
    Basic_Installed_Cost = 972.0                # 2007 USD/kW
    Installed_Cost_SCR = 1290.0                 # 2007 USD/kW
#    Heat_Rate = 9220.0                          # Btu/kWh HHV
    Electrical_Efficiency = 37.00               # Percent, HHV
    Fuel_Input = 368.8                          # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 435.0          # psig
#    Exhaust_Flow = 954.0                        # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 854.0              # Fahrenheit
#    HRSG_Exhaust_Temperature = 280.0            # Fahrenheit
#    Steam_Output_MMBtu = 129.27                 # MMBtu/hr
#    Steam_Output_lbs = 128.5                    # 1,000 lbs/hr
#    Steam_Output_kW = 37876.0                   # kW equivalent
    Total_CHP_Efficiency = 72.1                 # Percent, HHV
#    Power_Heat_Ratio = 1.06                     # Dimensionless
#    Net_Heat_Rate = 5180.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 66.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0042                 # $/kWh
#    NOx = 0.50                                  # lbs/MWh
#    CO = 0.51                                   # lbs/MWh
    CO2 = 1079.0                                # lbs/MWh
#    Total_Carbon = 294.0                        # lbs/MWh
    Conts = [0.00003, -0.0087, 0.8463, 7.7655, 39.1]   # Regression constants
    min_PLR = 10.0
    engine = 'gas5'                            # Identifier for the auxiliary function

    return Computer(engine, Conts, Electrical_Capacity, Basic_Installed_Cost, Installed_Cost_SCR, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Microturbine_1(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Microturbine System 1. Simulates a Capstone Model 330 - 30 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 30.0                  # kW
    Compressor_Parasitic_Power = 2.0            # kW
#    Package_Cost = 1290.0                       # 2007 USD/kW
    Total_Installed_Cost = 2970.0               # 2007 USD/kW
#    Heat_Rate = 15075.0                         # Btu/kWh HHV
    Electrical_Efficiency = 22.6                # Percent, HHV
    Fuel_Input = 0.422                          # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 75.0           # psig
#    Exhaust_Flow = 0.69                         # lbs/sec
#    GT_Exhaust_Temperature = 530.0              # Fahrenheit
#    Heat_Output_MMBtu = 0.17                    # MMBtu/hr
#    Heat_Output_kW = 50.9                       # kW equivalent
    Total_CHP_Efficiency = 63.8                 # Percent, HHV
#    Power_Heat_Ratio = 0.55                     # Dimensionless
#    Net_Heat_Rate = 7313.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 46.7      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.020                  # $/kW
#    NOx = 0.54                                  # lbs/MWh
#    CO = 1.46                                   # lbs/MWh
    CO2 = 1736.0                                # lbs/MWh
#    THC = 0.19                                  # lbs/MWh
    Conts = [0.00003, -0.0068, 0.553, 5.593, 24.76]   # Regression constants
    min_PLR = 10.0
    engine = 'micro1'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, Compressor_Parasitic_Power)

def EPA_CHP_Microturbine_2(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Microturbine System 2. Simulates a Capstone Model C65 - 65 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 65.0                  # kW
    Compressor_Parasitic_Power = 2.0            # kW
#    Package_Cost = 1280.0                       # 2007 USD/kW
    Total_Installed_Cost = 2490.0               # 2007 USD/kW
#    Heat_Rate = 13891.0                         # Btu/kWh HHV
    Electrical_Efficiency = 24.6                # Percent, HHV
    Fuel_Input = 0.875                          # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 75.0           # psig
#    Exhaust_Flow = 1.12                         # lbs/sec
#    GT_Exhaust_Temperature = 592.0              # Fahrenheit
#    Heat_Output_MMBtu = 0.41                    # MMBtu/hr
#    Heat_Output_kW = 119.5                      # kW equivalent
    Total_CHP_Efficiency = 71.2                 # Percent, HHV
#    Power_Heat_Ratio = 0.53                     # Dimensionless
#    Net_Heat_Rate = 5796.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 58.9      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0175                 # $/kW
#    NOx = 0.22                                  # lbs/MWh
#    CO = 0.30                                   # lbs/MWh
    CO2 = 1597.0                                # lbs/MWh
#    THC = 0.09                                  # lbs/MWh
    Conts = [0.00003, -0.0074, 0.6019, 6.0879, 26.76]   # Regression constants
    min_PLR = 10.0
    engine = 'micro2'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, Compressor_Parasitic_Power)

def EPA_CHP_Microturbine_3(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Microturbine System 3. Simulates a Ingersoll Rand Power MT250 - 250 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 250.0                 # kW
    Compressor_Parasitic_Power = 8.0            # kW
#    Package_Cost = 1410.0                       # 2007 USD/kW
    Total_Installed_Cost = 2440.0               # 2007 USD/kW
#    Heat_Rate = 13080.0                         # Btu/kWh HHV
    Electrical_Efficiency = 26.09               # Percent, HHV
    Fuel_Input = 3.165                          # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 75.0           # psig
#    Exhaust_Flow = 4.70                         # lbs/sec
#    GT_Exhaust_Temperature = 468.0              # Fahrenheit
#    Heat_Output_MMBtu = 1.20                    # MMBtu/hr
#    Heat_Output_kW = 351.6                      # kW equivalent
    Total_CHP_Efficiency = 64.0                 # Percent, HHV
#    Power_Heat_Ratio = 0.69                     # Dimensionless
#    Net_Heat_Rate = 6882.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 49.6      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.016                  # $/kW
#    NOx = 0.29                                  # lbs/MWh
#    CO = 0.14                                   # lbs/MWh
    CO2 = 1377.0                                # lbs/MWh
#    THC = 0.10                                  # lbs/MWh
    Conts = [0.00003, -0.0079, 0.6384, 6.4567, 28.25]   # Regression constants
    min_PLR = 10.0
    engine = 'micro3'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, Compressor_Parasitic_Power)

def EPA_CHP_Reciprocating_Engine_1(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Reciprocating Engine System 1. Simulates an IPower EN185 - 85 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 100.0                 # kW
    Total_Installed_Cost = 2210.0               # 2007 USD/kW
#    Heat_Rate = 12000.0                         # Btu/kWh HHV
    Electrical_Efficiency = 28.4                # Percent, HHV
#    Engine_Speed = 1800                         # rpm
    Fuel_Input = 1.20                           # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 3.0            # psig
#    Exhaust_Flow = 1.4                          # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 1060.0             # Fahrenheit
#    Heat_Recovered_From_Exhaust = 0.28          # MMBtu/hr
#    Heat_Recovered_From_Cooling_Jacket = 0.33   # MMBtu/hr
#    Heat_Recovered_From_Lube_System = 0.00      # MMBtu/hr
#    Total_Heat_Recovered_MMBtu = 0.61           # MMBtu/hr
#    Total_Heat_Recovered_kW = 179.0             # kW equivalent
    Total_CHP_Efficiency = 79.0                 # Percent, HHV
#    Power_Heat_Ratio = 0.56                     # Dimensionless
#    Net_Heat_Rate = 4383.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 78.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0022                 # $/kWh
#    NOx = 0.10                                  # lbs/MWh
#    CO = 0.32                                   # lbs/MWh
#    VOC = 0.10                                  # lbs/MWh
    CO2 = 1404.0                                # lbs/MWh
    Conts = [-0.0000001, -0.0008, 0.1605, 20.016, 30.56]   # Regression constants
    min_PLR = 30.0
    engine = 'recip1'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Reciprocating_Engine_2(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Reciprocating Engine System 2. Simulates a GE Jenbacher JMS 312 GS-N.L. - 625 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 300.0                 # kW
    Total_Installed_Cost = 1940.0               # 2007 USD/kW
#    Heat_Rate = 9866.0                          # Btu/kWh HHV
    Electrical_Efficiency = 34.6                # Percent, HHV
#    Engine_Speed = 1800                         # rpm
    Fuel_Input = 4.93                           # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 3.0            # psig
#    Exhaust_Flow = 6.3                          # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 939.0              # Fahrenheit
#    Heat_Recovered_From_Exhaust = 1.03          # MMBtu/hr
#    Heat_Recovered_From_Cooling_Jacket = 1.13   # MMBtu/hr
#    Heat_Recovered_From_Lube_System = 0.00      # MMBtu/hr
#    Total_Heat_Recovered_MMBtu = 2.16           # MMBtu/hr
#    Total_Heat_Recovered_kW = 632.0             # kW equivalent
    Total_CHP_Efficiency = 78.0                 # Percent, HHV
#    Power_Heat_Ratio = 0.79                     # Dimensionless
#    Net_Heat_Rate = 4470.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 76.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0016                 # $/kWh
#    NOx = 0.50                                  # lbs/MWh
#    CO = 1.87                                   # lbs/MWh
#    VOC = 0.47                                  # lbs/MWh
    CO2 = 1284.0                                # lbs/MWh
    Conts = [-0.0000002, -0.0009, 0.1955, 24.386, 36.76]   # Regression constants
    min_PLR = 30.0
    engine = 'recip2'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Reciprocating_Engine_3(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Reciprocating Engine System 3. Simulates a GE Jenbacher JMS 320 GS-N.L. - 1050 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 800.0                 # kW
    Total_Installed_Cost = 1640.0               # 2007 USD/kW
#    Heat_Rate = 9760.0                          # Btu/kWh HHV
    Electrical_Efficiency = 35.0                # Percent, HHV
#    Engine_Speed = 1800                         # rpm
    Fuel_Input = 9.76                           # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 3.0            # psig
#    Exhaust_Flow = 12.1                         # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 909.0              # Fahrenheit
#    Heat_Recovered_From_Exhaust = 1.85          # MMBtu/hr
#    Heat_Recovered_From_Cooling_Jacket = 2.45   # MMBtu/hr
#    Heat_Recovered_From_Lube_System = 0.00      # MMBtu/hr
#    Total_Heat_Recovered_MMBtu = 4.30           # MMBtu/hr
#    Total_Heat_Recovered_kW = 1260.0            # kW equivalent
    Total_CHP_Efficiency = 79.0                 # Percent, HHV
#    Power_Heat_Ratio = 0.79                     # Dimensionless
#    Net_Heat_Rate = 4385.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 78.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0013                 # $/kWh
#    NOx = 1.49                                  # lbs/MWh
#    CO = 0.87                                   # lbs/MWh
#    VOC = 0.38                                  # lbs/MWh
    CO2 = 1142.0                                # lbs/MWh
    Conts = [-0.0000002, -0.0009, 0.1975, 24.668, 37.16]   # Regression constants
    min_PLR = 30.0
    engine = 'recip3'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Reciprocating_Engine_4(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Reciprocating Engine System 4. Simulates a Caterpillar G3616 LE - 3 MW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 3000.0                # kW
    Total_Installed_Cost = 1130.0               # 2007 USD/kW
#    Heat_Rate = 9492.0                          # Btu/kWh HHV
    Electrical_Efficiency = 36.0                # Percent, HHV
#    Engine_Speed = 900                          # rpm
    Fuel_Input = 28.48                          # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 43.0           # psig
#    Exhaust_Flow = 48.4                         # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 688.0              # Fahrenheit
#    Heat_Recovered_From_Exhaust = 4.94          # MMBtu/hr
#    Heat_Recovered_From_Cooling_Jacket = 4.37   # MMBtu/hr
#    Heat_Recovered_From_Lube_System = 1.22      # MMBtu/hr
#    Total_Heat_Recovered_MMBtu = 10.53          # MMBtu/hr
#    Total_Heat_Recovered_kW = 3084.0            # kW equivalent
    Total_CHP_Efficiency = 73.0                 # Percent, HHV
#    Power_Heat_Ratio = 0.97                     # Dimensionless
#    Net_Heat_Rate = 5107.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 67.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0010                 # $/kWh
#    NOx = 1.52                                  # lbs/MWh
#    CO = 0.78                                   # lbs/MWh
#    VOC = 0.34                                  # lbs/MWh
    CO2 = 1110.0                                # lbs/MWh
    Conts = [-0.0000002, -0.001, 0.2034, 25.373, 38.16]   # Regression constants
    min_PLR = 30.0
    engine = 'recip4'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Reciprocating_Engine_5(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Reciprocating Engine System 5. Simulates a Wartsila 5238 LN - 5 MW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 5000.0                # kW
    Total_Installed_Cost = 1130.0               # 2007 USD/kW
#    Heat_Rate = 8758.0                          # Btu/kWh HHV
    Electrical_Efficiency = 39.0                # Percent, HHV
#    Engine_Speed = 720                          # rpm
    Fuel_Input = 43.79                          # MMBtu/hr
#    Required_Fuel_Gas_Pressure = 65.0           # psig
#    Exhaust_Flow = 67.1                         # 1,000 lbs/hr
#    GT_Exhaust_Temperature = 698.0              # Fahrenheit
#    Heat_Recovered_From_Exhaust = 7.01          # MMBtu/hr
#    Heat_Recovered_From_Cooling_Jacket = 6.28   # MMBtu/hr
#    Heat_Recovered_From_Lube_System = 1.94      # MMBtu/hr
#    Total_Heat_Recovered_MMBtu = 15.23          # MMBtu/hr
#    Total_Heat_Recovered_kW = 4463.0            # kW equivalent
    Total_CHP_Efficiency = 74.0                 # Percent, HHV
#    Power_Heat_Ratio = 1.12                     # Dimensionless
#    Net_Heat_Rate = 4950.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 69.0      # Percent
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0009                 # $/kWh
#    NOx = 1.24                                  # lbs/MWh
#    CO = 0.75                                   # lbs/MWh
#    VOC = 0.22                                  # lbs/MWh
    CO2 = 1024.0                                # lbs/MWh
    Conts = [-0.0000002, -0.001, 0.2204, 27.487, 41.16]   # Regression constants
    min_PLR = 30.0
    engine = 'recip5'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

# =============================================================================
# def Jenbacher(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
#     ''' Jenbacher Engine per the Oakland Baseline Case Study. Simulates a GE Jenbacher 920 FleXtra 9.5 MW CHP
#         prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
#         Environmental Analysis, an ICF International Company.
# 
#         Required input units:
#             Altitude: Feet
#             Ambient Temperature: Fahrenheit
#             Gas Line Pressure: psig
#             Hourly Electricity: kWh
#     '''
#     # Parameters
#     Electrical_Capacity = 9500.0                # kW
#     Total_Installed_Cost = 1130.0               # 2007 USD/kW
#     Heat_Rate = 6837.0                          # Btu/kWh HHV
#     Electrical_Efficiency = 49.9                # Percent, HHV
#     Engine_Speed = 900                          # rpm
#     Fuel_Input = 64.95                          # MMBtu/hr
#     Required_Fuel_Gas_Pressure = 65.0           # psig
#     Exhaust_Flow = 67.1                         # 1,000 lbs/hr
#     GT_Exhaust_Temperature = 698.0              # Fahrenheit
#     Heat_Recovered_From_Exhaust = 7.01          # MMBtu/hr
#     Heat_Recovered_From_Cooling_Jacket = 6.28   # MMBtu/hr
#     Heat_Recovered_From_Lube_System = 1.94      # MMBtu/hr
#     Total_Heat_Recovered_MMBtu = 15.23          # MMBtu/hr
#     Total_Heat_Recovered_kW = 7510.0            # kW equivalent
#     Total_CHP_Efficiency = 74.0                 # Percent, HHV
# #    Power_Heat_Ratio = 1.17                     # Dimensionless
#     Net_Heat_Rate = 3818.4                      # Btu/kWh
#     Effective_Electrical_Efficiency = 89.3      # Percent
#     Ramp_Rate = 1900.0                          # kW/min
#     Total_O_and_M_Cost = 0.0009                 # $/kWh
# #    NOx = 1.24                                  # lbs/MWh
# #    CO = 0.75                                   # lbs/MWh
#     VOC = 0.22                                  # lbs/MWh
#     CO2 = 1024.0                                # lbs/MWh
# 
#     # Store hourly electricity
#     Hourly_Electrical_Consumption = Hourly_Electricity
# 
#     # Derate available electrical capacity for altitude
#     Updated_Electrical_Capacity = (-1.0/300*Altitude+100.0)/100*Electrical_Capacity
#     Altitude_Derate = Updated_Electrical_Capacity/Electrical_Capacity
#     Electrical_Capacity = Updated_Electrical_Capacity
# 
#     # Derate available electrical capacity for ambient temperature
#     Electrical_Capacity = (-1.0/6*Ambient_Temperature+110)/100*Electrical_Capacity
#     
#     # Calculate electrical efficiency from part load
#     Num_Engines = mp.ceil(Hourly_Electricity/Electrical_Capacity)
#     if Num_Engines <= Max_Engines:
#         if Hourly_Electricity <= 0:
#             Part_Load = 0.0
#             Updated_Electrical_Efficiency = -0.0000002*Part_Load**3-0.001*Part_Load**2+0.2204*Part_Load+27.487
#         else:
#             Part_Load = Hourly_Electricity/(Num_Engines*Electrical_Capacity)*100    # Percent
#             if Part_Load < 10.0:
#                 Part_Load = 10.0
#                 Updated_Electrical_Efficiency = -0.0000002*Part_Load**3-0.001*Part_Load**2+0.2204*Part_Load+27.487
#             else:
#                 Updated_Electrical_Efficiency = -0.0000002*Part_Load**3-0.001*Part_Load**2+0.2204*Part_Load+27.487
#     else:
#         Part_Load = 100
#         Num_Engines = Max_Engines
#         Updated_Electrical_Efficiency = -0.0000002*Part_Load**3-0.001*Part_Load**2+0.2204*Part_Load+27.487
# 
#     if Hourly_Electricity <= 0:
#         Maximum_Electrical_Production = 0
#     else:
#         Maximum_Electrical_Production = Part_Load*Num_Engines*Electrical_Capacity/100
# 
#     # Derate electrical efficiency from altitude
#     Updated_Electrical_Efficiency = Updated_Electrical_Efficiency*Altitude_Derate
# 
#     # Derate efficiency from ambient air temperature
#     Updated_Electrical_Efficiency = (-9.0/250*Ambient_Temperature+41.16)/Electrical_Efficiency*Updated_Electrical_Efficiency
# 
#     # Calculate upramp or downramp for the hour (which is attributde to this hour solely)
#     if Num_Engines > Num_Engines_Last_T:
#         Delta_Engines = Num_Engines-Num_Engines_Last_T
#         Ramp_Minutes = Part_Load*Electrical_Capacity/100/Ramp_Rate
#         Ramp_Energy = 0.5*Ramp_Minutes*Part_Load*Electrical_Capacity/100*Delta_Engines/60
#         if Part_Load > Part_Load_Last_T:
#             Delta_Part_Load = Part_Load-Part_Load_Last_T
#             Ramp_Minutes = Delta_Part_Load*Electrical_Capacity/100/Ramp_Rate
#             Ramp_Energy += 0.5*Ramp_Minutes*Delta_Part_Load*Electrical_Capacity/100*Num_Engines_Last_T/60
#         else:
#             Delta_Part_Load = Part_Load_Last_T-Part_Load
#             Ramp_Minutes = Delta_Part_Load*Electrical_Capacity/100/Ramp_Rate
#             Ramp_Energy += 0.5*Ramp_Minutes*Delta_Part_Load*Electrical_Capacity/100*Num_Engines_Last_T/60
#     else:
#         Delta_Engines = Num_Engines_Last_T-Num_Engines
#         Ramp_Minutes = Part_Load_Last_T*Electrical_Capacity/100/Ramp_Rate
#         Ramp_Energy = 0.5*Ramp_Minutes*Part_Load_Last_T*Electrical_Capacity/100*Delta_Engines/60
#         if Part_Load > Part_Load_Last_T:
#             Delta_Part_Load = Part_Load-Part_Load_Last_T
#             Ramp_Minutes = Delta_Part_Load*Electrical_Capacity/100/Ramp_Rate
#             Ramp_Energy += 0.5*Ramp_Minutes*Delta_Part_Load*Electrical_Capacity/100*Num_Engines/60
#         else:
#             Delta_Part_Load = Part_Load_Last_T-Part_Load
#             Ramp_Minutes = Delta_Part_Load*Electrical_Capacity/100/Ramp_Rate
#             Ramp_Energy += 0.5*Ramp_Minutes*Delta_Part_Load*Electrical_Capacity/100*Num_Engines/60
# 
#     # Calculate maximum electrical and heat output
#     Heat_Rate = kWh_to_Btu/(Updated_Electrical_Efficiency/100)
#     Fuel_Input = Heat_Rate*(Part_Load/100*Num_Engines*Electrical_Capacity+Ramp_Energy)   # Btu
#     HRR = (Total_CHP_Efficiency-Electrical_Efficiency)/(100-Electrical_Efficiency)
#     Maximum_Heat_Production = (Fuel_Input/kWh_to_Btu-Maximum_Electrical_Production)*HRR    # kWh
#     # Calculate costs and emissions of interest
#     Capital_Cost = Num_Engines*Electrical_Capacity*Total_Installed_Cost
#     Variable_Cost = Hourly_Electrical_Consumption*Total_O_and_M_Cost+Fuel_Input*Natural_Gas_Cost
#     Carbon_Emissions = CO2*(Hourly_Electrical_Consumption/1000)
# 
#     return [Fuel_Input, Hourly_Electrical_Consumption, Maximum_Heat_Production, Maximum_Electrical_Production, Capital_Cost, Variable_Cost, Carbon_Emissions, Num_Engines, Part_Load]
# 
# =============================================================================

def EPA_CHP_Steam_Turbine_1(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Steam Turbine System 1. Simulates a TurboSteam, Inc. 500 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company. Loss in work due to pump estimated from
        http://www.rshanthini.com/tmp/ThermoBook/ThermoChap12.pdf. Efficiency curve from "Thermodynamic
        Simulation and Evaluatoin of a Steam CHP Plant Using Aspen Plus" by Ong'iro, Alfred, et al. in
        Applied Thermal Engineeing, Vol. 16, No. 3 pp. 263-271, 1995.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 500.0                 # kW
#    Equipment_Cost = 657.0                      # $/kW
    Total_Installed_Cost = 1117.0               # 2007 USD/kW
#    Turbine_Isentropic_Efficiency = 50.0        # Percent
#    Generator_Gearbox_Efficiency = 94.0         # Percent
#    Steam_Flow = 21500.0                        # lbs/hr
#    Inlet_Pressure = 500.0                      # psig
#    Inlet_Temperature = 550.0                   # Fahrenheit
#    Outlet_Pressure = 50.0                      # psig
#    Outlet_Temperature = 298.0                  # Fahrenheit
#    Boiler_Efficiency = 80.0                    # Percent, HHV
    Electrical_Efficiency = 6.4                 # Percent
    Fuel_Input = 26.7                           # MMBtu/hr
#    Steam_to_Process = 19.6                     # MMBtu/hr
#    Steam_to_Process = 5740.0                   # kW
    Total_CHP_Efficiency = 79.6                 # Percent
#    Power_Heat_Ratio = 0.09                     # Dimensionless
#    Net_Heat_Rate = 4515.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 75.6      # Percent
#    Heat_Fuel_Ratio = 0.73                      # Dimensionless
#    Electricity_Fuel_Ratio = 0.06               # Dimensionless
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0005                 # $/kWh
#    NOx = 0.07                                  # lbs/MMBtu
#    CO = 0.08                                   # lbs/MMBtu
#    PM = 0.00                                   # lbs/MMBtu
    CO2 = 34.0                                  # lbs/MMBtu
    Conts = [0.000002, -0.0006, 0.0647, 4.0974, 8.56]   # Regression constants
    min_PLR = 45.0
    engine = 'steam1'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Steam_Turbine_2(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Steam Turbine System 1. Simulates a TurboSteam, Inc. 3000 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company. Loss in work due to pump estimated from
        http://www.rshanthini.com/tmp/ThermoBook/ThermoChap12.pdf. Efficiency curve from "Thermodynamic
        Simulation and Evaluatoin of a Steam CHP Plant Using Aspen Plus" by Ong'iro, Alfred, et al. in
        Applied Thermal Engineeing, Vol. 16, No. 3 pp. 263-271, 1995.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 3000.0                # kW
#    Equipment_Cost = 278.0                      # $/kW
    Total_Installed_Cost = 475.0                # 2007 USD/kW
#    Turbine_Isentropic_Efficiency = 70.0        # Percent
#    Generator_Gearbox_Efficiency = 94.0         # Percent
#    Steam_Flow = 126000.0                       # lbs/hr
#    Inlet_Pressure = 600.0                      # psig
#    Inlet_Temperature = 575.0                   # Fahrenheit
#    Outlet_Pressure = 150.0                     # psig
#    Outlet_Temperature = 366.0                  # Fahrenheit
#    Boiler_Efficiency = 80.0                    # Percent, HHV
    Electrical_Efficiency = 6.9                 # Percent
    Fuel_Input = 147.4                          # MMBtu/hr
#    Steam_to_Process = 107.0                    # MMBtu/hr
#    Steam_to_Process = 31352.0                  # kW
    Total_CHP_Efficiency = 79.5                 # Percent
#    Power_Heat_Ratio = 0.10                     # Dimensionless
#    Net_Heat_Rate = 4568.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 75.1      # Percent
#    Heat_Fuel_Ratio = 0.72                      # Dimensionless
#    Electricity_Fuel_Ratio = 0.07               # Dimensionless
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0005                 # $/kWh
#    NOx = 0.19                                  # lbs/MMBtu
#    CO = 0.08                                   # lbs/MMBtu
#    PM = 0.00                                   # lbs/MMBtu
    CO2 = 34.0                                  # lbs/MMBtu
    Conts = [0.000002, -0.0007, 0.0697, 4.4176, 9.06]   # Regression constants
    min_PLR = 45.0
    engine = 'steam2'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Steam_Turbine_3(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Steam Turbine System 1. Simulates a TurboSteam, Inc. 15000 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company. Loss in work due to pump estimated from
        http://www.rshanthini.com/tmp/ThermoBook/ThermoChap12.pdf. Efficiency curve from "Thermodynamic
        Simulation and Evaluatoin of a Steam CHP Plant Using Aspen Plus" by Ong'iro, Alfred, et al. in
        Applied Thermal Engineeing, Vol. 16, No. 3 pp. 263-271, 1995.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 15000.0               # kW
#    Equipment_Cost = 252.0                      # $/kW
    Total_Installed_Cost = 429.0                # 2007 USD/kW
#    Turbine_Isentropic_Efficiency = 80.0        # Percent
#    Generator_Gearbox_Efficiency = 97.0         # Percent
#    Steam_Flow = 450000.0                       # lbs/hr
#    Inlet_Pressure = 700.0                      # psig
#    Inlet_Temperature = 650.0                   # Fahrenheit
#    Outlet_Pressure = 150.0                     # psig
#    Outlet_Temperature = 366.0                  # Fahrenheit
#    Boiler_Efficiency = 80.0                    # Percent, HHV
    Electrical_Efficiency = 9.3                 # Percent
    Fuel_Input = 549.0                          # MMBtu/hr
#    Steam_to_Process = 386.6                    # MMBtu/hr
#    Steam_to_Process = 113291.0                 # kW
    Total_CHP_Efficiency = 79.7                 # Percent
#    Power_Heat_Ratio = 0.13                     # Dimensionless
#    Net_Heat_Rate = 4388.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 77.8      # Percent
#    Heat_Fuel_Ratio = 0.70                      # Dimensionless
#    Electricity_Fuel_Ratio = 0.09               # Dimensionless
    Ramp_Rate = 1313.0                          # kW/min
    Total_O_and_M_Cost = 0.0005                 # $/kWh
#    NOx = 0.19                                  # lbs/MMBtu
#    CO = 0.08                                   # lbs/MMBtu
#    PM = 0.00                                   # lbs/MMBtu
    CO2 = 34.0                                  # lbs/MMBtu
    Conts = [0.000003, -0.0009, 0.0939, 5.9541, 11.16]   # Regression constants
    min_PLR = 45.0
    engine = 'steam3'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Fuel_Cell_1(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Fuel Cell System 1. Simulates a UTC PC25 - 200 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 200.0                 # kW
#    Operating_Temperature = 400.0               # Fahrenheit
#    Package_Cost = 4500.0                       # 2007 USD/kW
    Total_Installed_Cost = 6310.0               # 2007 USD/kW
    Total_O_and_M_Cost = 0.038                  # $/kWh
#    Electric_Heat_Rate = 9480.0                 # Btu/kWh
    Electrical_Efficiency = 33.0                # Percent, HHV
    Fuel_Input = 1.9                            # MMBtu/hr
#    Heat_Available_Greater_Than_160_F = 0.375   # MMBtu/hr
#    Heat_Available_Less_Than_160_F = 0.475      # MMBtu/hr
#    Heat_Output_MMBtu = 0.850                   # MMBtu/hr
#    Heat_Output_kW = 249.0                      # kW equivalent
    Total_CHP_Efficiency = 81.0                 # Percent, HHV
#    Power_Heat_Ratio = 0.80                     # Dimensionless
#    Net_Heat_Rate = 4168.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 81.90     # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
#    NOx = 0.035                                 # lbs/MWh
#    CO = 0.042                                  # lbs/MWh
#    VOC = 0.012                                 # lbs/MWh
    CO2 = 0.035                                 # lbs/MWh
    Conts = [0.000009, -0.003, 0.3142, 22.55, 35.772]   # Regression constants
    min_PLR = 25.0
    engine = 'cell1'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Fuel_Cell_2(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Fuel Cell System 2. Simulates a Demonstration 10 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 10.0                  # kW
#    Operating_Temperature = 150.0               # Fahrenheit
#    Package_Cost = 8000.0                       # 2007 USD/kW
    Total_Installed_Cost = 9100.0               # 2007 USD/kW
    Total_O_and_M_Cost = 0.038                  # $/kWh
#    Electric_Heat_Rate = 11370.0                # Btu/kWh
    Electrical_Efficiency = 30.0                # Percent, HHV
    Fuel_Input = 0.1                            # MMBtu/hr
#    Heat_Available_Greater_Than_160_F = 0.0     # MMBtu/hr
#    Heat_Available_Less_Than_160_F = 0.04       # MMBtu/hr
#    Heat_Output_MMBtu = 0.04                    # MMBtu/hr
#    Heat_Output_kW = 11.7                       # kW equivalent
    Total_CHP_Efficiency = 65.0                 # Percent, HHV
#    Power_Heat_Ratio = 0.85                     # Dimensionless
#    Net_Heat_Rate = 6370.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 53.58     # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
#    NOx = 0.06                                  # lbs/MWh
#    CO = 0.07                                   # lbs/MWh
#    VOC = 0.01                                  # lbs/MWh
    CO2 = 0.06                                  # lbs/MWh
    Conts = [0.000008, -0.0027, 0.2856, 20.5, 32.772]   # Regression constants
    min_PLR = 25.0
    engine = 'cell2'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Fuel_Cell_3(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Fuel Cell System 3. Simulates a Demonstration 200 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 200.0                 # kW
#    Operating_Temperature = 150.0               # Fahrenheit
#    Package_Cost = 8000.0                       # 2007 USD/kW
    Total_Installed_Cost = 9100.0               # 2007 USD/kW
    Total_O_and_M_Cost = 0.038                  # $/kWh
#    Electric_Heat_Rate = 9750.0                 # Btu/kWh
    Electrical_Efficiency = 35.0                # Percent, HHV
    Fuel_Input = 2.0                            # MMBtu/hr
#    Heat_Available_Greater_Than_160_F = 0.0     # MMBtu/hr
#    Heat_Available_Less_Than_160_F = 0.72       # MMBtu/hr
#    Heat_Output_MMBtu = 0.72                    # MMBtu/hr
#    Heat_Output_kW = 211.0                      # kW equivalent
    Total_CHP_Efficiency = 72.0                 # Percent, HHV
#    Power_Heat_Ratio = 0.95                     # Dimensionless
#    Net_Heat_Rate = 5250.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 65.01     # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
#    NOx = 0.06                                  # lbs/MWh
#    CO = 0.07                                   # lbs/MWh
#    VOC = 0.01                                  # lbs/MWh
    CO2 = 0.06                                  # lbs/MWh
    Conts = [0.000009, -0.0032, 0.3332, 23.916, 37.772]   # Regression constants
    min_PLR = 25.0
    engine = 'cell3'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Fuel_Cell_4(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Fuel Cell System 4. Simulates a Fuel Cell Energy DFC300MA - 300 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 300.0                 # kW
#    Operating_Temperature = 1200.0              # Fahrenheit
#    Package_Cost = 4000.0                       # 2007 USD/kW
    Total_Installed_Cost = 5580.0               # 2007 USD/kW
    Total_O_and_M_Cost = 0.035                  # $/kWh
#    Electric_Heat_Rate = 8022.0                 # Btu/kWh
    Electrical_Efficiency = 43.0                # Percent, HHV
    Fuel_Input = 2.4                            # MMBtu/hr
#    Heat_Available_Greater_Than_160_F = 0.0     # MMBtu/hr
#    Heat_Available_Less_Than_160_F = 0.48       # MMBtu/hr
#    Heat_Output_MMBtu = 0.48                    # MMBtu/hr
#    Heat_Output_kW = 140.6                      # kW equivalent
    Total_CHP_Efficiency = 62.0                 # Percent, HHV
#    Power_Heat_Ratio = 2.13                     # Dimensionless
#    Net_Heat_Rate = 6022.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 56.67     # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
#    NOx = 0.02                                  # lbs/MWh
#    CO = 0.10                                   # lbs/MWh
#    VOC = 0.01                                  # lbs/MWh
    CO2 = 0.02                                  # lbs/MWh
    Conts = [0.00001, -0.0039, 0.4049, 29.383, 45.772]   # Regression constants
    min_PLR = 25.0
    engine = 'cell4'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Fuel_Cell_5(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Fuel Cell System 5. Simulates a Fuel Cell Energy DFC1500MA - 1200 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 1200.0                # kW
#    Operating_Temperature = 1200.0              # Fahrenheit
#    Package_Cost = 3870.0                       # 2007 USD/kW
    Total_Installed_Cost = 5250.0               # 2007 USD/kW
    Total_O_and_M_Cost = 0.032                  # $/kWh
#    Electric_Heat_Rate = 8022.0                 # Btu/kWh
    Electrical_Efficiency = 43.0                # Percent, HHV
    Fuel_Input = 9.6                            # MMBtu/hr
#    Heat_Available_Greater_Than_160_F = 0.0     # MMBtu/hr
#    Heat_Available_Less_Than_160_F = 1.90       # MMBtu/hr
#    Heat_Output_MMBtu = 1.90                    # MMBtu/hr
#    Heat_Output_kW = 556.7                      # kW equivalent
    Total_CHP_Efficiency = 62.0                 # Percent, HHV
#    Power_Heat_Ratio = 2.16                     # Dimensionless
#    Net_Heat_Rate = 6043.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 56.48     # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
#    NOx = 0.02                                  # lbs/MWh
#    CO = 0.10                                   # lbs/MWh
#    VOC = 0.01                                  # lbs/MWh
    CO2 = 0.02                                  # lbs/MWh
    Conts = [0.00001, -0.0039, 0.4049, 29.383, 45.772]   # Regression constants
    min_PLR = 25.0
    engine = 'cell5'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def EPA_CHP_Fuel_Cell_6(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Catalog of CHP Technologies Fuel Cell System 6. Simulates a Siemens Westinghouse SFC-200 - 125 kW CHP
        prime mover. Data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and
        Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 125.0                 # kW
#    Operating_Temperature = 1750.0              # Fahrenheit
#    Package_Cost = 5000.0                       # 2007 USD/kW
    Total_Installed_Cost = 6500.0               # 2007 USD/kW
    Total_O_and_M_Cost = 0.038                  # $/kWh
#    Electric_Heat_Rate = 8024.0                 # Btu/kWh
    Electrical_Efficiency = 43.0                # Percent, HHV
    Fuel_Input = 1.0                            # MMBtu/hr
#    Heat_Available_Greater_Than_160_F = 0.0     # MMBtu/hr
#    Heat_Available_Less_Than_160_F = 0.34       # MMBtu/hr
#    Heat_Output_MMBtu = 0.34                    # MMBtu/hr
#    Heat_Output_kW = 100.0                      # kW equivalent
    Total_CHP_Efficiency = 77.0                 # Percent, HHV
#    Power_Heat_Ratio = 1.25                     # Dimensionless
#    Net_Heat_Rate = 4611.0                      # Btu/kWh
#    Effective_Electrical_Efficiency = 74.02     # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
#    NOx = 0.05                                  # lbs/MWh
#    CO = 0.04                                   # lbs/MWh
#    VOC = 0.01                                  # lbs/MWh
    CO2 = 0.05                                  # lbs/MWh
    Conts = [0.00001, -0.0039, 0.4049, 29.383, 45.772]   # Regression constants
    min_PLR = 25.0
    engine = 'cell6'                          # Identifier for the auxiliary function

    ## Total_Installed_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Total_Installed_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, Total_O_and_M_Cost, CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_1(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Stoker Boiler Power Generation System 1. Combined data from the EPA Catalog
        of CHP Technologies. Assumes use of a Back-Pressure Steam Turbine. Data from the EPA Biomass Combined
        Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan Wickwire. Additional
        data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and Environmental
        Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 500.0                 # kW
#    Operating_Temperature = 494.0               # Fahrenheit
#    Boiler_Efficiency = 63.0                    # Percent
    Fuel_Input = 35.4                           # MMBtu/hr
#    Heat_from_Boiler = 22.5                     # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Process_Steam_Flow = 19400.0                # lb/hr
#    Process_Steam_Pressure = 15.0               # psig saturated
    Total_CHP_Efficiency = 62.9                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 9260.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.142               # $/kWh
    Non_Fuel_O_and_M = 0.146                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.407          # $/kWh
#    Net_Power_Cost_with_Credit = 0.277          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000002, -0.0005, 0.0487, 3.0854, 6.98]   # Regression constants
    min_PLR = 45.0
    engine = 'bio1'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, 0, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_2(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Stoker Boiler Power Generation System 2. Combined data from the EPA Catalog
        of CHP Technologies. Assumes use of a Back-Pressure Steam Turbine. Data from the EPA Biomass Combined
        Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan Wickwire. Additional
        data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and Environmental
        Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 5600.0                # kW
#    Operating_Temperature = 750.0               # Fahrenheit
#    Boiler_Efficiency = 71.0                    # Percent
    Fuel_Input = 297.5                          # MMBtu/hr
#    Heat_from_Boiler = 212.0                    # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Process_Steam_Flow = 173000.0               # lb/hr
#    Process_Steam_Pressure = 150.0              # psig saturated
    Total_CHP_Efficiency = 70.5                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 4630.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.106               # $/kWh
    Non_Fuel_O_and_M = 0.036                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.202          # $/kWh
#    Net_Power_Cost_with_Credit = 0.106          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000002, -0.0006, 0.0649, 4.1119, 8.58]   # Regression constants
    min_PLR = 45.0
    engine = 'bio2'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, 0, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_3(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Stoker Boiler Power Generation System 3. Combined data from the EPA Catalog
        of CHP Technologies. Assumes use of a Back-Pressure Steam Turbine. Data from the EPA Biomass Combined
        Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan Wickwire. Additional
        data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and Environmental
        Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 8400.0                # kW
#    Operating_Temperature = 750.0               # Fahrenheit
#    Boiler_Efficiency = 71.0                    # Percent
    Fuel_Input = 446.3                          # MMBtu/hr
#    Heat_from_Boiler = 318.0                    # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Process_Steam_Flow = 260000.0               # lb/hr
#    Process_Steam_Pressure = 150.0              # psig saturated
    Total_CHP_Efficiency = 70.5                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 4000.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.106               # $/kWh
    Non_Fuel_O_and_M = 0.026                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.184          # $/kWh
#    Net_Power_Cost_with_Credit = 0.087          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000002, -0.0006, 0.0649, 4.1114, 8.58]   # Regression constants
    min_PLR = 45.0
    engine = 'bio3'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, 0, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)


def CHP_Biomass_4(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Circulating Fluidized Bed Power Generation System 1. Combined data from the
        EPA Catalog of CHP Technologies. Assumes use of a Back-Pressure Steam Turbine. Data from the EPA
        Biomass Combined Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan
        Wickwire. Additional data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy
        and Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 500.0                 # kW
#    Operating_Temperature = 275.0               # Fahrenheit
#    Boiler_Efficiency = 67.0                    # Percent
    Fuel_Input = 35.4                           # MMBtu/hr
#    Heat_from_Boiler = 23.7                     # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Process_Steam_Flow = 20300.0                # lb/hr
#    Process_Steam_Pressure = 15.0               # psig saturated
    Total_CHP_Efficiency = 66.1                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 20070.0                      # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.142               # $/kWh
    Non_Fuel_O_and_M = 0.146                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.407          # $/kWh
#    Net_Power_Cost_with_Credit = 0.276          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000002, -0.0005, 0.0487, 3.0854, 6.98]   # Regression constants
    min_PLR = 45.0
    engine = 'bio4'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, 0, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_5(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Circulating Fluidized Bed Power Generation System 2. Combined data from the
        EPA Catalog of CHP Technologies. Assumes use of a Back-Pressure Steam Turbine. Data from the EPA
        Biomass Combined Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan
        Wickwire. Additional data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy
        and Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 5900.0                # kW
#    Operating_Temperature = 750.0               # Fahrenheit
#    Boiler_Efficiency = 75.0                    # Percent
    Fuel_Input = 297.5                          # MMBtu/hr
#    Heat_from_Boiler = 223.1                    # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Process_Steam_Flow = 181100.0               # lb/hr
#    Process_Steam_Pressure = 150.0              # psig saturated
    Total_CHP_Efficiency = 73.7                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 5515.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.101               # $/kWh
    Non_Fuel_O_and_M = 0.034                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.192          # $/kWh
#    Net_Power_Cost_with_Credit = 0.100          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000002, -0.00064, 0.0684, 4.3322, 8.93]   # Regression constants
    min_PLR = 45.0
    engine = 'bio5'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, 0, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_6(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Circulating Fluidized Bed Power Generation System 3. Combined data from the
        EPA Catalog of CHP Technologies. Assumes use of a Back-Pressure Steam Turbine. Data from the EPA
        Biomass Combined Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan
        Wickwire. Additional data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy
        and Environmental Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 8800.0                # kW
#    Operating_Temperature = 750.0               # Fahrenheit
#    Boiler_Efficiency = 75.0                    # Percent
    Fuel_Input = 446.3                          # MMBtu/hr
#    Heat_from_Boiler = 334.7                    # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Process_Steam_Flow = 271600.0               # lb/hr
#    Process_Steam_Pressure = 150.0              # psig saturated
    Total_CHP_Efficiency = 73.7                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 4860.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.101               # $/kWh
    Non_Fuel_O_and_M = 0.024                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.175          # $/kWh
#    Net_Power_Cost_with_Credit = 0.083          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000002, -0.00064, 0.068, 4.3072, 8.89]   # Regression constants
    min_PLR = 45.0
    engine = 'bio6'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, 0, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_7(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Gasification Power Generation System 1. Combined data from the EPA Catalog
        of CHP Technologies. Assumes use of a Simple Cycle Steam Turbine. Data from the EPA Biomass Combined
        Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan Wickwire. Additional
        data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and Environmental
        Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 4000.0                # kW
#    Operating_Temperature = 180.0               # Fahrenheit
#    Gasifier_Efficiency = 71.0                  # Percent
    Fuel_Input = 49.6                           # MMBtu/hr
#    Fuel_from_Gasifier = 35.2                   # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Gross_Electric_Capacity = 4.0               # MW
#    Parasitic_Load = 0.0                        # MW
#    Prime_Mover_Efficiency = 38.3               # Percent, HHV
#    Hot_Water = 21.8                            # MMBtu/hr
#    Process_Thermal_Energy = 21.8               # MMBtu/hr
    Electrical_Efficiency = 27.2                # Percent, HHV
#    Heat_Rate = 12551.0                         # Btu/kWh
    Total_CHP_Efficiency = 71.2                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 2333.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.022               # $/kWh
    Non_Fuel_O_and_M = 0.044                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.096          # $/kWh
#    Net_Power_Cost_with_Credit = 0.081          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000009, -0.0027, 0.278, 17.617, 29.68]   # Regression constants
    min_PLR = 45.0
    engine = 'bio7'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_8(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Gasification Power Generation System 2. Combined data from the EPA Catalog
        of CHP Technologies. Assumes use of a Simple Cycle Steam Turbine. Data from the EPA Biomass Combined
        Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan Wickwire. Additional
        data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and Environmental
        Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 4900.0                # kW
#    Operating_Temperature = 500.0               # Fahrenheit
#    Gasifier_Efficiency = 71.0                  # Percent
    Fuel_Input = 127.9                          # MMBtu/hr
#    Fuel_from_Gasifier = 90.8                   # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Gross_Electric_Capacity = 8.2               # MW
#    Parasitic_Load = 3.3                        # MW
#    Prime_Mover_Efficiency = 30.7               # Percent, HHV
#    Steam_Recovery = 34.9                       # Mlb/hr
#    Process_Thermal_Energy = 40.1               # MMBtu/hr
    Electrical_Efficiency = 13.0                # Percent, HHV
#    Heat_Rate = 26249.0                         # Btu/kWh
    Total_CHP_Efficiency = 44.3                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 5188.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.046               # $/kWh
    Non_Fuel_O_and_M = 0.044                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.158          # $/kWh
#    Net_Power_Cost_with_Credit = 0.136          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000004, -0.00124, 0.1321, 8.3689, 15.23]   # Regression constants
    min_PLR = 45.0
    engine = 'bio8'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_9(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Gasification Power Generation System 3. Combined data from the EPA Catalog
        of CHP Technologies. Assumes use of a Simple Cycle Steam Turbine. Data from the EPA Biomass Combined
        Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan Wickwire. Additional
        data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and Environmental
        Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 8600.0                # kW
#    Operating_Temperature = 515.0               # Celsius
#    Gasifier_Efficiency = 71.0                  # Percent
    Fuel_Input = 224.1                          # MMBtu/hr
#    Fuel_from_Gasifier = 159.1                  # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Gross_Electric_Capacity = 14.3              # MW
#    Parasitic_Load = 5.8                        # MW
#    Prime_Mover_Efficiency = 30.7               # Percent, HHV
#    Steam_Recovery = 61.0                       # Mlb/hr
#    Process_Thermal_Energy = 70.0               # MMBtu/hr
    Electrical_Efficiency = 13.0                # Percent, HHV
#    Heat_Rate = 26172.0                         # Btu/kWh
    Total_CHP_Efficiency = 44.3                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/min
    Capital_Cost = 4245.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.046               # $/kWh
    Non_Fuel_O_and_M = 0.033                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.134          # $/kWh
#    Net_Power_Cost_with_Credit = 0.113          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000004, -0.00124, 0.1323, 8.383, 15.25]   # Regression constants
    min_PLR = 45.0
    engine = 'bio9'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)

def CHP_Biomass_10(Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T):
    ''' EPA Biomass CHP Catalog Gasification Power Generation System 4. Combined data from the EPA Catalog
        of CHP Technologies. Assumes use of a Simple Cycle Steam Turbine. Data from the EPA Biomass Combined
        Heat and Power Catalog of Technologies, September 2007 v. 1.1 edited by Susan Wickwire. Additional
        data from U.S. EPA Catalog of CHP Technologies, December 2008 prepared by Energy and Environmental
        Analysis, an ICF International Company.

        Required input units:
            Altitude: Feet
            Ambient Temperature: Fahrenheit
            Gas Line Pressure: psig
            Hourly Electricity: kWh
    '''
    # Parameters
    Electrical_Capacity = 32600.0               # kW
#    Operating_Temperature = 740.0               # Fahrenheit
#    Gasifier_Efficiency = 72.0                  # Percent
    Fuel_Input = 531.9                          # MMBtu/hr
#    Fuel_from_Gasifier = 382.6                  # MMBtu/hr
#    Plant_Capacity_Factor = 0.9                 # Dimensionless
#    Gross_Electric_Capacity = 36.3              # MW
#    Parasitic_Load = 3.79                       # MW
#    Prime_Mover_Efficiency = 32.4               # Percent, HHV
#    Steam_Recovery = 123.0                      # Mlb/hr
#    Process_Thermal_Energy = 170.5              # MMBtu/hr
    Electrical_Efficiency = 20.9                # Percent, HHV
#    Heat_Rate = 16338.0                         # Btu/kWh
    Total_CHP_Efficiency = 52.9                 # Percent, HHV
    Ramp_Rate = 1313.0                          # kW/mins
    Capital_Cost = 2291.0                       # $/kW
#    Biomass_Fuel_Cost_MMBtu = 2.00              # $/MMBtu
    Biomass_Fuel_Cost_kWh = 0.029               # $/kWh
    Non_Fuel_O_and_M = 0.019                    # $/kWh
#    Cost_to_Generate_No_Credit = 0.082          # $/kWh
#    Net_Power_Cost_with_Credit = 0.068          # $/kWh
#    NOx = 0.35                                  # lbs/MWh
#    CO = 0.60                                   # lbs/MWh
#    PM = 0.44                                   # lbs/MWh
    CO2 = 0.0                                   # lbs/MWh
    Conts = [0.000007, -0.0021, 0.2113, 13.388, 23.07]   # Regression constants
    min_PLR = 45.0
    engine = 'bio10'                          # Identifier for the auxiliary function

    ## Capital_Cost == Installed_Cost_SCR from the gas turbines + Basic_Installed_Cost is set to zero in function if not input which is the case for microturbines
    return Computer(engine, Conts, Electrical_Capacity, 0, Capital_Cost, Electrical_Efficiency, Fuel_Input, Total_CHP_Efficiency, Ramp_Rate, (Biomass_Fuel_Cost_kWh+Non_Fuel_O_and_M), CO2, Altitude, Ambient_Temperature, Gas_Line_Pressure, Hourly_Electricity, Num_Engines_Last_T, Part_Load_Last_T, min_PLR, 0)