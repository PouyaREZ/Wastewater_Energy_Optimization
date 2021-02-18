from __future__ import division


import json
import math as mp
import numpy as np
import timeit
import random as rp
import sys
import mutPolynomialBoundedInt
import pyDOE as pd
import copy

from deap import base
from deap import creator
from deap import tools
import fitness_with_constraints

import Water_Profiler as wp
import CHPEngines as CHP
import ElectricChillers as EC
import AbsorptionChillers as AC
import WWT as WWT

from scoop import futures


''' Note that to run this code, there must be .csv files for the hourly electricity, hourly heating,
    hourly cooling, and hourly weather. There must be 26 building types used, and the names of the 
    files must be:
        Hourly_Water.csv
        Hourly_Electricity.csv
        Hourly_Heating.csv
        Hourly_Cooling.csv
'''

Start = timeit.default_timer()

'''-----------------------------------------------------------------------------------------------'''
### Universal Constants #
'''-----------------------------------------------------------------------------------------------'''
Btu_to_J = 1055.06                  # Conversion of Btu to J
kWh_to_J = 3600000.00               # Conversion of kWh to J
MWh_to_J = 3600000000.00            # Conversion of MWh to J
tons_to_J_hr = 12660670.23144     #1266067022400.00 WRONG prev value    # Conversion of tons cooling to J/hour
kWh_to_Btu = 3412.14                   # Conversion of kWh to Btu
tons_to_MMBtu_hr = 0.012            # Conversion of tons to MMBtu/hr
tons_to_Btu_hr = 12000              # Conversion of tons to Btu/hr
tons_to_kW = 3.5168525              # Conversion of tons to kWh
meters_to_ft = 3.28084              # Conversion of meters to feet
MT_to_lbs = 2204.62                 # Conversion of metric tonnes to lbs

LHV_Natural_Gas = 47100000.00       # Lower heating value of natural gas (J/kg) ## updated from engineeringtoolbox (Apr 2019)
Specific_Heat_Water = 4216.00       # Specific heat of water at STP (J/kg-C) ## updated from engineeringtoolbox (Apr 2019)
Density_Water = 999.9               # Density of liquid water (kg/m^3)

Const_Carbon_per_Mil_Dollar = 243   # tonnes CO2 equivalent per million 2007 USD from http://www.eiolca.net/cgi-bin/dft/display.pl?hybrid=no&value=6325700065&newmatrix=US388EPAEEIO2007&second_level_sector=233240&first_level_sector=Utilities+Buildings+And+Infrastructure&key=55196567699&incdemand=1&demandmult=1&selectvect=gwp&top=10

Standard_Thermal_Efficiency = 0.8   # Assumed efficiency of heating in a separate system (dimensionless)
Standard_Grid_Efficiency = 0.4      # Assumed grid efficiency of electrical generation and distribution (dimensionless)

Discount_Rate = 0.035                # Discounted rate for future cash flows # from https://www.whitehouse.gov/wp-content/uploads/2018/12/M-19-05.pdf
Project_Life = 20                   # Years to consider future cash flows for the project
Current_Year = 2019

USD_2008_to_2019 = 1.19             # From http://www.in2013dollars.com/2008-dollars-in-2019
USD_2007_to_2019 = 1.23             # From http://www.in2013dollars.com/us/inflation/2007

'''-----------------------------------------------------------------------------------------------'''
### Solar Parameters #
'''-----------------------------------------------------------------------------------------------'''
Tilt = 20                           # degrees
Azimuth = 180                       # degrees

'''-----------------------------------------------------------------------------------------------'''
### Optimization Parameters #
'''-----------------------------------------------------------------------------------------------'''
Population_Size = 200 #288 #4  ## MODIFIED -- Must be a multiple of 4
Mutation_Probability = 0.05
Crossover_Probability = 0.75
Eta = 2.5
Number_Generations = 1000 #10 ## MODIFIED


CWWTP_Mode = 1          # If 1: CWWTP treats the ww; if 0: CCHP-WWT treats the ww


Num_Engines = 32        # Must be updated if new engines are added
Num_Chillers = 16       # Must be updated if new chillers are added
Max_Buildings_per_Type = 10000 
Building_Min = 0
Supply_Min = 1
Vars_Plus_Output = 42  # Must be updated if new chillers, engines, or outputs are added; Must also update optimization initialization
    

Max_Site_GFA = 647497 
Min_GFA = Max_Site_GFA*0.1
Max_FAR = 5.0 # Assumed
Max_GFA = Max_FAR*Max_Site_GFA # Following the paper
Min_Total_Buildings = 1
Min_Solar = 0                    # Per SF Ordinance
Max_Solar = 0                     # Percentage of available solar roof area: from http://www.nrel.gov/docs/fy14osti/60593.pdf
Min_WWT = 1
Num_WWT = 2

Max_Avg_Height = 50 # in ft? Yup! :| The heights in building_info.csv are also in feet

## TES Con'ts ## From the 'storage formula' for a hot water storage tank, from "A comparison of TES models for bldg energy system opt" 
## Question: Does TES require any extra pumping?
# The sensible heat storage type using water is justified, as Heat_Source_Temperature = 100 deg F, and is within the working range of the TES
## **** Note that TES here only stores the excess heat
kv = 0.0534/100  ## Heat loss factor -- 
Hourly_TES_Coeff = (1-kv)**12 # Remaining energy within TES after an hour--Power of 12 is beacause each time step = 300s in the original paper
TES_Max_Hours = 6 # TES can store TES_Max_Hours x max(heat_demand)


## WW Treatment con'ts
#Storage_Cap = 24*7 # hr # Storage capacity for GW treatment system


Min_Res = 0                      # Percentage of total GFA
Max_Res = 100.                     # Percentage of total GFA
Min_Off = 0                     # Percentage of total GFA
Max_Off = 100.                      # Percentage of total GFA
Min_Ret = 0.0                       # Percentage of total GFA
Max_Ret = 100.                       # Percentage of total GFA
Min_Ind = 0.0                      # Percentage of total GFA
Max_Ind = 100.                      # Percentage of total GFA
Min_Lod = 0.0                       # Percentage of total GFA
Max_Lod = 100.                      # Percentage of total GFA
Min_Hosp = 0.0                        # Percentage of total GFA
Max_Hosp = 100.                      # Percentage of total GFA
Min_Edu = 0.0                        # Percentage of total GFA
Max_Edu = 100.                       # Percentage of total GFA
Min_Mix = 0.0                        # Percentage of total GFA
Max_Mix = 100.                       # Percentage of total GFA

# Consider updating to inputs above. Use for now for calculation of Low/High Seqs.

'''-----------------------------------------------------------------------------------------------'''
### Demand import framework for bringing in data from outside sources and ModelCenter. #
'''-----------------------------------------------------------------------------------------------'''
# Define the function that will remove unnecessary lines from the input arrays
def RemoveHeaders(Demand_Array):
    ''' Removes the headers from an array of hourly demand values if any are present. THe input is an array of
        demand values and the output is an array stripped of all leading lines that do not contain numeric
        values.
    '''
    if mp.isnan(Demand_Array[0,1]) == 1:
        Demand_Array = Demand_Array[1:]
        Demand_Array = RemoveHeaders(Demand_Array)

    if mp.isnan(Demand_Array[1,0]) == 1:
        Demand_Array = Demand_Array[:, 1:]
        Demand_Array = RemoveHeaders(Demand_Array)

    return Demand_Array



# Defining cmp from older versions of Python ## ADDED
def cmp(a, b):
    return (a > b) - (a < b) 



# Create input arrays for electricity, heating, and cooling
Electricity_Input = np.genfromtxt('Hourly_Electricity.csv', 'float', delimiter=',')
Electricity_Input = RemoveHeaders(Electricity_Input)
Heating_Input = np.genfromtxt('Hourly_Heating.csv', 'float', delimiter=',')
Heating_Input = RemoveHeaders(Heating_Input)
Cooling_Input = np.genfromtxt('Hourly_Cooling.csv', 'float', delimiter=',')
Cooling_Input = RemoveHeaders(Cooling_Input)
GW_Input = wp.Water_Demand() # in L


# Create input arrays for weather
Weather = np.genfromtxt('Hourly_Weather.csv', 'float', delimiter=',')
Weather = RemoveHeaders(Weather)
Hourly_Temperature = Weather[:,0]
Hourly_Wet_Bulb = Weather[:,1]
Hourly_DNI = Weather[:,2]
Hourly_DHI = Weather[:,3]
Hourly_GHI = Weather[:,4]
Hourly_Albedo = Weather[:,5]
Hourly_Wind_Speed = Weather[:,6]

# Create input array for building metadata
Building_Info = np.genfromtxt('Building_Info.csv', 'float', delimiter=',')
Building_Info = RemoveHeaders(Building_Info)


# Input the table of CHP information
CHP_Info = np.genfromtxt('CHP_Info.csv', 'float', delimiter=',')
CHP_Info = RemoveHeaders(CHP_Info)

# Set up dictionaries that will hold CHP info
Power_to_Heat = {}
CHP_Variable_Cost = {}
Max_Unit_Size = {}
CHP_Capital_Cost = {}
CHP_Fuel_Type = {}
CHP_Heat_Rate = {}

# Populate the dictionary
for i in range(Num_Engines):
    j=i+1
    Power_to_Heat[j] = CHP_Info[i,1]
    CHP_Variable_Cost[j] = CHP_Info[i,6]
    Max_Unit_Size[j] = CHP_Info[i,0]
    CHP_Capital_Cost[j] = CHP_Info[i,8]
    CHP_Fuel_Type[j] = CHP_Info[i,9]
    CHP_Heat_Rate[j] = CHP_Info[i,4]


# Create input array for the electricity pricing
Grid_Parameters = np.genfromtxt('Grid_Parameters.csv', 'float', delimiter=',')
Grid_Parameters = RemoveHeaders(Grid_Parameters)

# Storing the grid info
Buy_Price = Grid_Parameters[:,0]
Sell_Price = Grid_Parameters[:,1]
Grid_Emissions = Grid_Parameters[:,2]
Demand_Charge = Grid_Parameters[:,3]   #####            HOW ABOUT THE TOU (time of use) CHARGE? ## GRID EMISSIONS ARE EXCLUDED FROM THIS FILE: SELL-BACK ONLY LEADS TO FINANCIAL GAINS, NOT POLLUTION SETBACK

# Create inputs for site parameters
Site_Info = np.genfromtxt('Site_Info.csv', 'float', delimiter=',')
Site_Info = Site_Info[1,:]
Latitude = Site_Info[0]
Longitude = Site_Info[1]
Site_Altitude = Site_Info[2]
UTC = Site_Info[3]

# Create inputs for hours bookending days
Hours = np.genfromtxt('Hours.csv', 'int', delimiter=',')
Hours = RemoveHeaders(Hours)
Day_Starts = Hours[:,0]
Day_Ends = Hours[:,1]


#** CHANGED ITS LOCATION --> IT WAS REPEATED EVERY TIME IN THE SUPPLYDEMAND OPT!
'''-----------------------------------------------------------------------------------------------'''
### Generate dictionaries of supply engine, chiller, solar panel, and WWT types. #
'''-----------------------------------------------------------------------------------------------'''
Supply_Types = {}
Supply_Types[1] = CHP.EPA_CHP_Gas_Turbine_1
Supply_Types[2] = CHP.EPA_CHP_Gas_Turbine_2
Supply_Types[3] = CHP.EPA_CHP_Gas_Turbine_3
Supply_Types[4] = CHP.EPA_CHP_Gas_Turbine_4
Supply_Types[5] = CHP.EPA_CHP_Gas_Turbine_5
Supply_Types[6] = CHP.EPA_CHP_Microturbine_1
Supply_Types[7] = CHP.EPA_CHP_Microturbine_2
Supply_Types[8] = CHP.EPA_CHP_Microturbine_3
Supply_Types[9] = CHP.EPA_CHP_Reciprocating_Engine_1
Supply_Types[10] = CHP.EPA_CHP_Reciprocating_Engine_2
Supply_Types[11] = CHP.EPA_CHP_Reciprocating_Engine_3
Supply_Types[12] = CHP.EPA_CHP_Reciprocating_Engine_4
Supply_Types[13] = CHP.EPA_CHP_Reciprocating_Engine_5
Supply_Types[14] = CHP.EPA_CHP_Steam_Turbine_1
Supply_Types[15] = CHP.EPA_CHP_Steam_Turbine_2
Supply_Types[16] = CHP.EPA_CHP_Steam_Turbine_3
Supply_Types[17] = CHP.EPA_CHP_Fuel_Cell_1
Supply_Types[18] = CHP.EPA_CHP_Fuel_Cell_2
Supply_Types[19] = CHP.EPA_CHP_Fuel_Cell_3
Supply_Types[20] = CHP.EPA_CHP_Fuel_Cell_4
Supply_Types[21] = CHP.EPA_CHP_Fuel_Cell_5
Supply_Types[22] = CHP.EPA_CHP_Fuel_Cell_6
Supply_Types[23] = CHP.CHP_Biomass_1
Supply_Types[24] = CHP.CHP_Biomass_2
Supply_Types[25] = CHP.CHP_Biomass_3
Supply_Types[26] = CHP.CHP_Biomass_4
Supply_Types[27] = CHP.CHP_Biomass_5
Supply_Types[28] = CHP.CHP_Biomass_6
Supply_Types[29] = CHP.CHP_Biomass_7
Supply_Types[30] = CHP.CHP_Biomass_8
Supply_Types[31] = CHP.CHP_Biomass_9
Supply_Types[32] = CHP.CHP_Biomass_10

Chiller_Types = {}
Chiller_Types[1] = EC.Electric_Chiller_1
Chiller_Types[2] = EC.Electric_Chiller_2
Chiller_Types[3] = EC.Electric_Chiller_3
Chiller_Types[4] = EC.Electric_Chiller_4
Chiller_Types[5] = EC.Electric_Chiller_5
Chiller_Types[6] = EC.Electric_Chiller_6
Chiller_Types[7] = EC.Electric_Chiller_7
Chiller_Types[8] = EC.Electric_Chiller_8
Chiller_Types[9] = EC.Electric_Chiller_9
Chiller_Types[10] = AC.Absorption_Chiller_1
Chiller_Types[11] = AC.Absorption_Chiller_2
Chiller_Types[12] = AC.Absorption_Chiller_3
Chiller_Types[13] = AC.Absorption_Chiller_4
Chiller_Types[14] = AC.Absorption_Chiller_5
Chiller_Types[15] = AC.Absorption_Chiller_6
Chiller_Types[16] = AC.Absorption_Chiller_7
Chiller_Types[17] = AC.Absorption_Chiller_8


WWT_Types = {}
WWT_Types[1] = WWT.FO_MD
WWT_Types[2] = WWT.FO_RO
WWT_Types[3] = WWT.WWTP
 
'''-----------------------------------------------------------------------------------------------'''


# Define an index for the number of buildings in the simulation
Num_Buildings = len(Electricity_Input[1])

# Set up the dictionary that will hold the demand information
Demand_Types = {}

# Populate the dictionary with arrays of Electricity, Heating, and Cooling in that order
for i in range(Num_Buildings):
    j=i+1
    Demand_Types[j] = np.column_stack((Electricity_Input[:,i:i+1], Heating_Input[:,i:i+1], Cooling_Input[:,i:i+1], GW_Input[j]))    # Populate the dictionary with 8760x4 arrays of demand values per building

Results = np.zeros(shape=((Number_Generations+1)*Population_Size, Vars_Plus_Output))
counter = 0

# Create additional dictionaries that have the metadata for use in calculating constraints
# Note that the order below should be the order of the columns in the Building_Info.csv sheet
GFA = {}
Site_GFA = {}
Stories = {}
Dimensions = {}
Site_Dimensions = {}
Solar_Roof_Area = {}
Type = {}
Height = {}

for i in range(Num_Buildings):
    j=i+1
    GFA[j] = Building_Info[i,0] # in m2
    Site_GFA[j] = Building_Info[i,1] # in m2
    Stories[j] = Building_Info[i,2]
    Dimensions[j] = (Building_Info[i,3], Building_Info[i,4]) # in m
    Site_Dimensions[j] = (Building_Info[i,5], Building_Info[i,6]) # in m
    Type[j] = Building_Info[i,7]
    Solar_Roof_Area[j] = Building_Info[i,8]
    Height[j] = Building_Info[i,9] ### in ft!!

# Create the Low and High Sequence values that control mutation in optimization
Low_Seq = []
High_Seq = []
for i in range(Num_Buildings): ## TO DO: CAN INCLUDE THE MAX & MIN BLDG TYPES IN THE LOW AND HIGH SEQ
    Low_Seq += [0]
    High_Seq += [min(Max_Buildings_per_Type, np.floor(Max_GFA/GFA[i+1]), np.floor(Max_Site_GFA/Site_GFA[i+1]), np.floor(Max_FAR*Max_Site_GFA/GFA[i+1]))]
    if High_Seq[i] == 0.0:
        print ("Warning: Building "+str(i)+" has an invalid site or floor area constraint given the problem space. Check inputs and try again.")
        sys.exit()
Low_Seq += [Supply_Min]
Low_Seq += [Supply_Min]
High_Seq += [Num_Engines]
High_Seq += [Num_Chillers]
#Low_Seq += [Min_Solar]
#High_Seq += [Max_Solar]
if CWWTP_Mode == 0:
    Low_Seq += [Min_WWT]
    High_Seq += [Num_WWT]

def SupplyandDemandOptimization(Building_Var_Inputs):    
    Internal_Start = timeit.default_timer()

    '''-----------------------------------------------------------------------------------------------'''
    ### Use the input variables to create an overall demand file and then call the required functions. #
    '''-----------------------------------------------------------------------------------------------'''
    # First create a dictionary of building input variables
    Building_Vars = {}
    for i in range(Num_Buildings): ## MODIFIED it was 21 and it wasn't a loop
        Building_Vars[i+1] = Building_Var_Inputs[i] ###### Building_Vars = number of each building type
    Engine_Var = Building_Var_Inputs[Num_Buildings]
    Chiller_Var = Building_Var_Inputs[Num_Buildings+1]
    Comm_Solar_Var = 0 #Building_Var_Inputs[Num_Buildings+2]
    if CWWTP_Mode == 0:
        WWT_Var = Building_Var_Inputs[Num_Buildings+2]
    else:
        WWT_Var = 3
#    Comm_Solar_Type_Var = 1 ## ?? WHAT IS IT? Only the first solar type is used! NOT OPTIMIZING FOR SOLAR PANEL TYPE

    '''-----------------------------------------------------------------------------------------------'''
    ## Trivial Case Avoidance
    '''-----------------------------------------------------------------------------------------------'''
    if np.sum(Building_Var_Inputs[:Num_Buildings]) == 0: ## TRIVIAL CASE AVOIDANCE
        Run_Result = np.zeros((1,Vars_Plus_Output))
        Run_Result[0][Num_Buildings] = Engine_Var # i.e. element 21
        Run_Result[0][Num_Buildings+1] = Chiller_Var # i.e. element 22
        Run_Result[0][Num_Buildings+2] = Comm_Solar_Var # i.e. element 23
        Run_Result[0][Num_Buildings+3] = WWT_Var # i.e. element 24
        return ((0, 0,),
        ((Max_Site_GFA-0)/Max_Site_GFA,
         (0-Min_GFA)/Min_GFA,
         (Max_GFA-0)/Max_GFA, ), Run_Result) # Update based on whatever needs to be optimized



    # Use the Building_Vars dictionary and the dictionary of demands to create an aggregate function of demand
    # Note that the Diversifier Peak is an assumption
    Diversifier_Peak = 0.8 ## ??
    Aggregate_Demand = 0
    for i in range(Num_Buildings):
        j = i+1
        Aggregate_Demand += Diversifier_Peak*(Building_Vars[j]*Demand_Types[j][:,0:4]) ## MODIFIED for water demand+syntax shortened (columnstack replaced)
    
    
    '''-----------------------------------------------------------------------------------------------'''
    ### Adding the municipal demands to the created aggregate demands #
    '''-----------------------------------------------------------------------------------------------'''
    # Calculate total length and width of building sites
    Total_Site_Length = 0
    Total_Site_Width = 0
    for i in range(Num_Buildings):
        j = i+1
        Total_Site_Length += Building_Vars[j]*Site_Dimensions[j][0]
        Total_Site_Width += Building_Vars[j]*Site_Dimensions[j][1]

    # Add in municipal loads # MODIFIED--WAS ERRONEOUS BEFORE
    Curfew_Modifier = 0.50
    Light_Spacing = 48.8        # m
    Lights_Per_Side = 2
    Light_Power = .190           # kW
    Width_to_Length_Ratio = 1/8
    
    hours = np.array(range(8760))
    hours %= 24
    hours_lights_on = np.logical_or(((hours >= 19) * (hours <= 23)), ((hours >= 0) * (hours <= 6)))
    hours_lights_half_power = ((hours >= 2) * (hours <= 6))*(1-Curfew_Modifier)
    ## hours_lights_on-hours_lights_half_power results in 1 for hours with lights on, and curfew_modifier for half-powered hours
    Aggregate_Demand[:,0] += (hours_lights_on-hours_lights_half_power)*(np.ceil((Total_Site_Length+Width_to_Length_Ratio*Total_Site_Width)/Light_Spacing)*Lights_Per_Side*Light_Power)
    

    # Save the loads at this point for use later
    Final_Demand = copy.deepcopy(Aggregate_Demand)


    '''-----------------------------------------------------------------------------------------------'''
    ### Initiate TES based on the max raw hourly thermal demand #
    '''-----------------------------------------------------------------------------------------------'''
    TES_Max = np.max(Aggregate_Demand[:,1]) * TES_Max_Hours ## Storage capacity = TES_Max_Hours hours x peak annual hour heat load
    TES_Capex = 95*TES_Max/1000 * USD_2008_to_2019 # In 2019 USD # Averaged based on Table 8 from Cost for Sensible and other heat storage... @ D:\PhD\+Main Research Directory\W&WW+low-heat applications\+++ TES

    '''-----------------------------------------------------------------------------------------------'''
    ### Adding the losses to the demands #
    '''-----------------------------------------------------------------------------------------------'''
    Heat_Loss = 0.003               # kW/m
    Cooling_Loss = 0.017            # kW/m
    Electrical_Loss = 0.8568*0.06  # Decimal

    ''' See ISSST paper for losses on thermal side. For electrical, data is a combination of 6% loss on average
        in the U.S. and calculations by Mungkung, et al. on the percentage makeup of those losses at the low
        voltage level. References are:
            Munkung, et al.: http://www.wseas.us/e-library/conferences/2009/istanbul/TELE-INFO/TELE-INFO-02.pdf
            EIA: http://www.eia.gov/tools/faqs/faq.cfm?id=105&t=3
    '''
    ## MODIFIED: For loop -> in-place conversion
    Aggregate_Demand[:,0] += Aggregate_Demand[:,0]*Electrical_Loss
    Aggregate_Demand[:,1] += (Total_Site_Length+Total_Site_Width)*2*Heat_Loss*np.ones(len(Aggregate_Demand[:,0]))
    Aggregate_Demand[:,2] += (Total_Site_Length+Total_Site_Width)*2*Cooling_Loss*np.ones(len(Aggregate_Demand[:,0]))

    '''-----------------------------------------------------------------------------------------------'''
    ### Adding the chiller electrical/thermal demand to the aggregate electrical and thermal demands #
    '''-----------------------------------------------------------------------------------------------'''
#    Chiller_Hourly_Cooling_Results = np.zeros((8760)) ## MODIFIED for performance
    Chiller_COP_Results = np.zeros((8760)) ## MODIFIED for performance
#    UNUSED: Electrical_Demand = np.zeros((8760)) ## MODIFIED for performance
    Chiller_Costs = np.zeros((8760)) ## MODIFIED for performance

    Chilled_Water_Supply_Temperature = 44.0 # in deg F ## WHERE DID THIS COME FROM?
    Number_Iterations = 1 ## why??
    Heat_Source_Temperature = 100 ## And this? IS it in deg C or F?? It's in deg F

    Engine_Demand = np.zeros(shape=(8760,2))

    for i in range(len(Aggregate_Demand[:,0])):
        Hourly_Chiller_Result = Chiller_Types[Chiller_Var](Chilled_Water_Supply_Temperature, Hourly_Wet_Bulb[i]*9/5+32, Hourly_Temperature[i]*9/5+32, Aggregate_Demand[i,2], Number_Iterations, Heat_Source_Temperature)[0:6]
#        Chiller_Hourly_Cooling_Results[i] = Hourly_Chiller_Result[3] ## UNUSED
        Chiller_COP_Results[i] = Hourly_Chiller_Result[4] # MODIFIED
        Chiller_Costs[i] = Hourly_Chiller_Result[5] # MODIFIED
        Engine_Demand[i,0] = Aggregate_Demand[i,0]+Hourly_Chiller_Result[1]
        Engine_Demand[i,1] = Aggregate_Demand[i,1]+Hourly_Chiller_Result[2]
        

    
    ## Creating the total energy and wastewater demand for the neighborhood (used for comparing neighborhoods)
    Total_Energy_Demand = np.sum(Engine_Demand[:,0]) + np.sum(Engine_Demand[:,1])
    Total_WWater_Demand = np.sum(Aggregate_Demand[:,3])
    
    
    
    # additional vars: Hourly_WWT_Results (use later), WWT_Var (add to optimization vars)
    # additional functions: WWT_Types
    '''-----------------------------------------------------------------------------------------------'''
    ### Adding the GW treatment electrical/thermal demand to the aggregate electrical and thermal demands #
    '''-----------------------------------------------------------------------------------------------'''
    if CWWTP_Mode == 0:
        Hourly_WWT_Results = WWT_Types[WWT_Var](Aggregate_Demand[:,3], Hourly_Temperature)
    else:
        Hourly_WWT_Results = WWT_Types[WWT_Var](Aggregate_Demand[:,3], Hourly_Temperature, Grid_Emissions)
    Engine_Demand[:,0] += Hourly_WWT_Results[0]
    Engine_Demand[:,1] += Hourly_WWT_Results[1]
    WWT_Opex_Total = Hourly_WWT_Results[2] ## Annual value
    WWT_Capex_Total = Hourly_WWT_Results[3] ## Annual value
    if CWWTP_Mode == 0:
        WWT_GHG = 0
    else:
        WWT_GHG = Hourly_WWT_Results[4]
    
    
    
    '''-----------------------------------------------------------------------------------------------'''
    ### Solar Production #
    '''-----------------------------------------------------------------------------------------------'''

    Excess_Electricity = np.zeros((8760)) ## Originally: grid_sales
    Capital_Solar_Cost = 0



    # Calculate loads and subtract from total electrical demand; calculate costs and total solar capacity installed
    [Hourly_Solar_Generation, Capital_Solar_Cost] = [0,0]#Commercial_Solar_Types[Comm_Solar_Type_Var](np.array(range(8760)), UTC, Comm_Solar_Area, Tilt, Azimuth, Latitude, Longitude, Hourly_DNI, Hourly_DHI, Hourly_GHI, Hourly_Albedo, Hourly_Temperature, Hourly_Wind_Speed, Site_Altitude)[3:5]
    Engine_Demand[:,0] -= Hourly_Solar_Generation
    Excess_Electricity = np.abs((Engine_Demand[:,0] < 0) * Engine_Demand[:,0]) # Excess electricity no. 1
    Engine_Demand[:,0] += Excess_Electricity ## Hours with excess electricity are zeroed to avoid erroneous calculation in the CHPEngines.py with a negative Engine_Demand[i,0]
    

    # Save the loads with a different name at this point for use later
    Post_Solar_Demand = copy.deepcopy(Engine_Demand)


    '''-----------------------------------------------------------------------------------------------'''
    ### Run the CHP engine with the demands + use the excess heat for ww treatment #
    '''-----------------------------------------------------------------------------------------------'''
    # Now run a control scheme that simply produces to the greatest demand and counts excess as waste
    Power_to_Heat_Ratio = Power_to_Heat[Engine_Var]
    Gas_Line_Pressure = 55.0

    Fuel_Input_Results = np.zeros((8760))

    CCHP_Capex = 0 # in $
    CCHP_Opex = 0
    Carbon_Emissions = np.zeros(8760) ## CHANGED TO ARRAY FOLLOWING IILP_TOY_OPT 
    Last_Part_Load = 0
    Last_Num_Engines = 0
    Excess_Heat = np.zeros((8760)) ## CHANGED TO ARRAY FOLLOWING IILP_TOY_OPT 
    TES = np.zeros((8760)) ## Thermal Energy Storage
    

    
    ## For the previous version of the code in which only the excess heat was used in the WWT, refer to Ch3_SF_CaseStudy_w_Storage_PreE_Consumption_for_WWT
    for i in range(len(Engine_Demand[:,0])): ## MODIFIED: repetitive code excluded from the first if else
        TES[i] = Hourly_TES_Coeff * TES[i-1] ## Depreciating the previous time-step's stored energy; each timestep is defined as 300s ## NOTE: CAPITAL AND O&M for TES is not included yet!
        if Engine_Demand[i,1] < TES[i]: # More Stored heat than needed
            TES[i] -= Engine_Demand[i,1]
            Engine_Demand[i,1] = 0
        else: # All the stored heat should be used and we'll need extra heat from the CCHP
            Engine_Demand[i,1] -= TES[i]
            TES[i] = 0
        Test_Electricity = Engine_Demand[i,1]*Power_to_Heat_Ratio ## Electrical equivalent of the heat demand
        if Engine_Demand[i,0] > Test_Electricity: ## heat is not the controlling load; produce electricity to supply the engine-demand --> We'll have excess heat
            Hourly_Supply_Result = Supply_Types[Engine_Var](Site_Altitude, Hourly_Temperature[i], Gas_Line_Pressure, Engine_Demand[i,0], Last_Num_Engines, Last_Part_Load)
            Last_Num_Engines = Hourly_Supply_Result[7]
            Last_Part_Load = Hourly_Supply_Result[8]
            if Hourly_Supply_Result[2] < Engine_Demand[i,1]: ## Checking the produced heat with the required heat ## HOW IS IT POSSIBLE?
                Hourly_Supply_Result = Supply_Types[Engine_Var](Site_Altitude, Hourly_Temperature[i], Gas_Line_Pressure, Test_Electricity, Last_Num_Engines, Last_Part_Load)
                Last_Num_Engines = Hourly_Supply_Result[7]
                Last_Part_Load = Hourly_Supply_Result[8]
        else: ## Heat is the controlling load, produce to satisfy the heat, we'll have excess electricity
            Hourly_Supply_Result = Supply_Types[Engine_Var](Site_Altitude, Hourly_Temperature[i], Gas_Line_Pressure, Test_Electricity, Last_Num_Engines, Last_Part_Load)
            Last_Num_Engines = Hourly_Supply_Result[7]
            Last_Part_Load = Hourly_Supply_Result[8]
            if Hourly_Supply_Result[3] < Engine_Demand[i,0]: ## Checking electricity with the existing demand ## HOW IS IT POSSIBLE? ## We'll have excess heat
                Hourly_Supply_Result = Supply_Types[Engine_Var](Site_Altitude, Hourly_Temperature[i], Gas_Line_Pressure, Engine_Demand[i,0], Last_Num_Engines, Last_Part_Load)
                Last_Num_Engines = Hourly_Supply_Result[7]
                Last_Part_Load = Hourly_Supply_Result[8]
        
        ## Isn't the if statement below associated with the if statement 24 lines above????
        if Hourly_Supply_Result[2] > Engine_Demand[i,1]: # If produced heat > required heat, i.e. we have excess heat
            Excess_Heat[i] = Hourly_Supply_Result[2] - Engine_Demand[i,1]
            TES[i] = min(TES[i] + Excess_Heat[i], TES_Max) ## Formula from the 'storage formula' from "A comparison of TES models for bldg energy system opt" ## Assuming 100% energy storage efficiency
            Engine_Demand[i,1] = 0 ## following line 3085 of IILP_Toy_Optimization.py # Engine electric demand is responded to and it's zeroed
            ## ^ Why?? It's consumed and subtracted from the remaining demand similar to L 599
            
            # Hourly_Supply_Result[2] = 0 # Seems wrong
        
        
        Fuel_Input_Results[i] = Hourly_Supply_Result[0]/kWh_to_Btu ## a little problematic: we're only considering the energy content of the input fuel # kWh fuel
        CCHP_Capex = max(CCHP_Capex, Hourly_Supply_Result[4])
        CCHP_Opex += Hourly_Supply_Result[5] # CCHP Opex added 10 lines below
        Carbon_Emissions[i] += Hourly_Supply_Result[6] # in lbs
        
        ## Added to include grid sales after solar excess has been subtracted from demand above ^
        Engine_Demand[i,0] -= Hourly_Supply_Result[3]
        ## Isn't the if statement below associated with the else statement 50 lines above????
        if Engine_Demand[i,0] < 0:
            Excess_Electricity[i] += abs(Engine_Demand[i,0]) # Excess electricity number 2
            Engine_Demand[i,0] = 0



    '''-----------------------------------------------------------------------------------------------'''
    ### Calculate the overall efficiency and the hourly efficiencies. #
    '''-----------------------------------------------------------------------------------------------'''
    # Calculate values for constraints
    Total_GFA = 0
    Total_Site_GFA = 0
    Total_Buildings = 0
    Total_Height = 0
    Type_Max = int(np.max(Building_Info[:,7])) - 1 ## SHOULD THE TYPES BE SORTED IN THE FILE THEN? ## What's with the minus 1?? to avoid adding zero for mixed type -> they're separated into their components and added to the respective categories
    Type_Totals = {}
    Type_Areas = {}
    Type_Building_Percents = {}
    Type_Area_Percents = {}

    for i in range(Type_Max):
        j = i+1
        Type_Totals[j] = 0
        Type_Areas[j] = 0

    for i in range(Num_Buildings):
        j = i+1
        Total_GFA += Building_Vars[j]*GFA[j]
        Total_Site_GFA += Building_Vars[j]*Site_GFA[j]
        Total_Buildings += Building_Vars[j]
        Total_Height += Building_Vars[j]*Height[j]
        ## The mixed types are divided into their separate types (Res, Comm, and Off) and added to the respective areas
        if j == Num_Buildings-1:
            Type_Totals[3] += 1/Stories[j]*Building_Vars[j]
            Type_Totals[1] += 1/Stories[j]*(Stories[j]-1)*Building_Vars[j]
            Type_Areas[3] += 1/Stories[j]*Building_Vars[j]*GFA[j]
            Type_Areas[1] += 1/Stories[j]*(Stories[j]-1)*Building_Vars[j]*GFA[j]
        elif j == Num_Buildings:
            Type_Totals[3] += 1/Stories[j]*Building_Vars[j]
            Type_Totals[2] += 1/Stories[j]*(Stories[j]-1)*Building_Vars[j]
            Type_Areas[3] += 1/Stories[j]*Building_Vars[j]*GFA[j]
            Type_Areas[2] += 1/Stories[j]*(Stories[j]-1)*Building_Vars[j]*GFA[j]
        else:
            Type_Totals[Type[j]] = Type_Totals[Type[j]]+Building_Vars[j]
            Type_Areas[Type[j]] = Type_Areas[Type[j]]+GFA[j]*Building_Vars[j]
        

    Site_FAR = np.nan_to_num(Total_GFA/Total_Site_GFA) ## MODIFIED: nan_to_num added
    Average_Height = np.nan_to_num(Total_Height/Total_Buildings) ## MODIFIED: nan_to_num added

    for i in range(Type_Max):
        j = i+1
        Type_Building_Percents[j] = np.nan_to_num(Type_Totals[j]/Total_Buildings) ## MODIFIED: nan_to_num added
        Type_Area_Percents[j] = np.nan_to_num(Type_Areas[j]/Total_GFA) # In percents  ## MODIFIED: nan_to_num added

    # To find Final Demand, add the actual heat or electricity used to do real cooling work
    # on the buildings and calculate totaly hourly demand and efficiency, and keep a running
    # total of fuel use and demand
    Useful_Demand = np.zeros((8760))
    Total_Demand = 0.0
    CHP_Demand = 0.0 ## ADDED
    Total_Fuel = 0.0
    CHP_Fuel = 0.0 ## ADDED


    ## FOR LOOPS converted to DIRECT NUMPY ARRAY MANIPULATIONS
    COP_Flag = (Chiller_COP_Results > 1.0) ## WHY?
    Useful_Demand = (Final_Demand[:,0] + Final_Demand[:,1] +
                     COP_Flag * Final_Demand[:,2]/Chiller_COP_Results +
                     (1-COP_Flag) * Final_Demand[:,2])

    Total_Demand = np.sum(Useful_Demand)
    CHP_Demand = np.sum(Post_Solar_Demand[:,0] + Post_Solar_Demand[:,1]) # + Hourly_GW_Treated*FO_MD_Power_per_m3/1000) ## ADDED ## REMOVED!
    Total_Fuel = np.sum(Fuel_Input_Results) ## MODIFIED

    CHP_Fuel = np.sum(Fuel_Input_Results) ## ADDED


    if Total_Buildings > 0: ## REFER TO PAGE 79 of the thesis for the explanation 
        Overall_Efficiency = np.nan_to_num(Total_Demand/Total_Fuel) ## Added the nan_to_number ## Note: total demand = raw demand + solar power and neglecting the excess electricity from PVs and CHP
        Overall_CHP_Efficiency = np.nan_to_num(CHP_Demand/CHP_Fuel)
    else:
        Overall_Efficiency = 0
        Overall_CHP_Efficiency = 0

#    GW_Efficiency = np.nan_to_num(Total_Treated_GW/Total_GW) ## Added the nan_to_number
    
    # Total Capex # ADDED/ MODIFIED 
    if CWWTP_Mode == 0:
        Capex = CCHP_Capex + np.max(Chiller_Costs) + WWT_Capex_Total + Capital_Solar_Cost + TES_Capex # MODIFIED: Solar added ##MODIFIED # Optimization objective
    else:
        Capex = CCHP_Capex + np.max(Chiller_Costs) + Capital_Solar_Cost + TES_Capex # MODIFIED: Solar added ##MODIFIED # Optimization objective
    Total_Capex = CCHP_Capex + np.max(Chiller_Costs) + WWT_Capex_Total + Capital_Solar_Cost + TES_Capex # MODIFIED: Solar added ##MODIFIED # For recording
    ## Added: sell price usage
    
    
    # Carbon emissions # ADDED/ MODIFIED 
    Construction_Carbon = (Capex / USD_2007_to_2019)/10**6 * Const_Carbon_per_Mil_Dollar # in metric tons CO2 eq # Optimization objective
    Total_Construction_Carbon = (Total_Capex / USD_2007_to_2019)/10**6 * Const_Carbon_per_Mil_Dollar # in metric tons CO2 eq # For recording
    
    Annual_Carbon_Emissions = np.sum(Carbon_Emissions)/MT_to_lbs # in metric tons CO2e # Optimization objective
    Total_Annual_Carbon_Emissions = np.sum(Carbon_Emissions)/MT_to_lbs + WWT_GHG # in metric tons CO2e # For recording
    
    Years = np.arange(Current_Year, Current_Year+Project_Life) # ADDED/ MODIFIED 
    Annual_SCC = 0.8018*Years - 1585.7 # ADDED/ MODIFIED # in 2007 $ per metric tons of CO2
    
    SCC = (Construction_Carbon * Annual_SCC[0] + np.sum(Annual_SCC * Annual_Carbon_Emissions)) * USD_2007_to_2019 # ADDED/ MODIFIED # in 2019 $
    Total_SCC = (Total_Construction_Carbon * Annual_SCC[0] + np.sum(Annual_SCC * Total_Annual_Carbon_Emissions)) * USD_2007_to_2019 # ADDED/ MODIFIED # in 2019 $
    Total_Carbon = Project_Life * Total_Annual_Carbon_Emissions + Total_Construction_Carbon # ADDED/ MODIFIED in metric tons CO2e




    LCC = Capex
    LCC_Total = Total_Capex
    CCHP_Opex -= np.sum(Sell_Price*Excess_Electricity) ## Including the sales price
    for i in range(Project_Life):
        if CWWTP_Mode == 0:
            LCC += (CCHP_Opex+WWT_Opex_Total)/(1+Discount_Rate)**i # Optimization objective
        else:
            LCC += CCHP_Opex/(1+Discount_Rate)**i # Optimization objective
        LCC_Total += (CCHP_Opex+WWT_Opex_Total)/(1+Discount_Rate)**i # Total LCC for the record
    


    '''-----------------------------------------------------------------------------------------------'''
    ### Creating the outputs #
    '''-----------------------------------------------------------------------------------------------'''
    Internal_Stop = timeit.default_timer()
    Internal_Time = Internal_Stop-Internal_Start
    Run_Result = np.zeros((1,Vars_Plus_Output))
    # Add the variables first ## DESCRIPTIONS ADDED FROM IILP_TOY_OOPT
    for i in range(Num_Buildings): # i.e. elements 0 to 20
        Run_Result[0][i] = Building_Var_Inputs[i]
    Run_Result[0][Num_Buildings] = Engine_Var # i.e. element 21
    Run_Result[0][Num_Buildings+1] = Chiller_Var # i.e. element 22
    Run_Result[0][Num_Buildings+2] = Comm_Solar_Var # i.e. element 23
    Run_Result[0][Num_Buildings+3] = WWT_Var # i.e. element 24
    # Now the objectives
    Run_Result[0][Num_Buildings+4] = Overall_Efficiency # i.e. element 25
    Run_Result[0][Num_Buildings+5] = LCC_Total # i.e. element 26
    Run_Result[0][Num_Buildings+6] = Total_SCC # i.e. element 27 # in $
    Run_Result[0][Num_Buildings+7] = Overall_CHP_Efficiency # i.e. element 28
    Run_Result[0][Num_Buildings+7+Type_Max+4] = Total_Carbon # i.e. element 39 # in metric tons CO2e
    # Now the constraint values
    for i in range(Type_Max):
        j = i+1
        Run_Result[0][Num_Buildings+7+j] = Type_Area_Percents[j] # i.e. element 29 to 35
    Run_Result[0][Num_Buildings+7+Type_Max+1] = Site_FAR # i.e. element 36
    Run_Result[0][Num_Buildings+7+Type_Max+2] = Average_Height # i.e. element 37 # in ft!!
    Run_Result[0][Num_Buildings+7+Type_Max+3] = Total_GFA # i.e. element 38 # in m2
    # Now add the watch variables
    Run_Result[0][Num_Buildings+7+Type_Max+5] = Total_Energy_Demand #Old: Total_Excess_Electricity ## originally: Total_Capex # i.e. element 40
    Run_Result[0][Num_Buildings+7+Type_Max+6] = Total_WWater_Demand #Old: Total_Excess_Heat ## originally: CCHP_Opex # i.e. element 41 # in L


    # Return format: fitness values = return[0]; constraint values = return[1]; Results = np.append(Results, [fit[2]], axis=0)
    ## ALL THE CONSTRAINT VALUES ARE NORMALIZED to 0 to 1 range concerning the method of comparing two infeasible individuals in fitness_with_constraints [Look at def dominates(self)]
    if Total_GFA == 0: # Added for avoiding division by zero in the objectives (below) for trivial solutions
        Total_GFA = 0.00001
    return ((LCC/Total_GFA, SCC/Total_GFA, ),
            ((Max_Site_GFA-Total_Site_GFA),
             (Total_GFA-Min_GFA),
             (Max_GFA-Total_GFA), ),Run_Result)


'''-----------------------------------------------------------------------------------------------'''
### Instantiate the optimization. #
'''-----------------------------------------------------------------------------------------------'''
Samples = pd.lhs(len(High_Seq), samples = Population_Size) ## READ AGAIN
for i in range(len(Samples)):
    for j in range(len(Samples[0])):
        Samples[i,j] = np.round(Samples[i,j]*High_Seq[j])
        if Samples[i,j] < Low_Seq[j]:
            Samples[i,j] = Low_Seq[j]
        elif Samples[i,j] > High_Seq[j]:
            Samples[i,j] = High_Seq[j] ## MODIFIED ACCORDING TO IILP_TOY_OPTIMIZATION


seedfile = 'seed_population_288_SF_corn_test.json'
with open(seedfile, 'w') as outfile:
    json.dump(Samples.tolist(), outfile)

creator.create("EfficiencyMax", fitness_with_constraints.FitnessWithConstraints, weights=(-1.0, -1.0))    # Update based on number of objectives
creator.create("Individual", list, fitness=creator.EfficiencyMax)

def initIndividual(icls, content):
    return icls(content)

def initPopulation(pcls, ind_init, filename):
    contents = json.load(open(filename, 'r'))
    return pcls(ind_init(c) for c in contents)

toolbox = base.Toolbox()

toolbox.register("individual_guess", initIndividual, creator.Individual)
toolbox.register("population_guess", initPopulation, list, toolbox.individual_guess, seedfile)

def evaluateInd(individual):
    result = SupplyandDemandOptimization(individual)
    return result

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutPolynomialBoundedInt.mutPolynomialBoundedInt, eta=Eta, low=Low_Seq, up=High_Seq, indpb=Mutation_Probability)
toolbox.register("select", tools.selNSGA2)
toolbox.register("evaluate", evaluateInd)
toolbox.register("map", futures.map)

hof = tools.ParetoFront()
stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)
logbook = tools.Logbook()


def main():
    # Creating and evaluating the generation 0
    pop = toolbox.population_guess()
    global Results
    Results = np.zeros((1, Vars_Plus_Output))
    Results = [Results]
    
    # Unregister unpicklable methods before sending the toolbox.
    toolbox.unregister("individual_guess")
    toolbox.unregister("population_guess")

    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    evaluate_result = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, evaluate_result):
        ind.fitness.values = fit[0]
        ind.fitness.cvalues = fit[1]
        ind.fitness.n_constraints = len(fit[1])
        Results = np.append(Results, [fit[2]], axis=0)

    pop = toolbox.select(pop, len(pop))
    record = stats.compile(pop)
    logbook.record(gen= -1, evals=len(invalid_ind), **record)

    for g in range(Number_Generations):
        offspring = tools.selTournamentDCD(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring)) ## MODIFIED to be a list

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if rp.random() < Crossover_Probability:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit[0]
            ind.fitness.cvalues = fit[1]
            ind.fitness.n_constraints = len(fit[1])
            Results = np.append(Results, [fit[2]], axis=0)

        pop = toolbox.select(pop + offspring, Population_Size)
        record = stats.compile(pop)
        logbook.record(gen=g, evals=len(invalid_ind), **record)
        hof.update(pop)

    global logs
    logs = np.zeros(shape=(Number_Generations, 6))
    gens = logbook.select("gen")
    evalnum = logbook.select("evals")
    avgs = logbook.select("avg")
    stds = logbook.select("std")
    mins = logbook.select("min")
    maxs = logbook.select("max")

    for g in range(Number_Generations):
        logs[g,0] = gens[g]+1
        logs[g,1] = evalnum[g]
        logs[g,2] = avgs[g]
        logs[g,3] = stds[g]
        logs[g,4] = mins[g]
        logs[g,5] = maxs[g]


if __name__ == "__main__":
    main()
    TestRuns = Results[:,0,:] ## Summarized (MODIFIED)
    
    full_hof = np.zeros((len(hof),len(Results[0][0])))
    test_hof = np.zeros((len(hof), len(hof[0])))
    for i in range(len(hof)):
        test_hof[i] = hof[i]
    for i in range(len(test_hof)):
        for j in range(len(test_hof[0])):
            test_hof[i,j] = int(test_hof[i,j])
    Mod_Results = TestRuns[:,:len(hof[0])]
    for i in range(len(Mod_Results)):
        for j in range(len(Mod_Results[0])):
            Mod_Results[i,j] = int(Mod_Results[i,j])
    for i in range(len(hof)):
        for j in range(len(Mod_Results)):
            if cmp(Mod_Results[j].tolist(), test_hof[i].tolist()) == 0:
                full_hof[i] = TestRuns[j,:]
                break

    np.savetxt("SDO_LHS_FullHallofFame288_Constraint_SF_Test.txt", full_hof, fmt ='%f')
    np.savetxt("SDO_LHS_TestRuns288_Constraint_SF_Test.txt", TestRuns[1:], fmt='%f')
    np.savetxt("SDO_LHS_Logbook288_Constraint_SF_Test.txt", logs, fmt='%f')
    np.savetxt("SDO_LHSHallofFame288_Constraint_SF_Test.txt", hof, fmt='%f')
    

Stop = timeit.default_timer()

Time = Stop-Start
print(Time)
