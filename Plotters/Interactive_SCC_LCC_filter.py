# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29, 2019
Updated on Sun June 2, 2019

*** Don't run directly, use pareto_front_finder to run this script.

Interactive 2-dimensional figure for analyzing the simulation results from Ch3_SF_CaseStudy_TES_WWT.py
LCC/m2 & CO2/m2 are unlimited

@Author: PouyaRZ
"""

# import random
import numpy as np
import pandas as pd
from bokeh.palettes import d3
from bokeh.layouts import row, widgetbox
from bokeh.io import reset_output
# from bokeh.palettes import plasma
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool, CustomJS, Slider, Button, RangeSlider, CheckboxButtonGroup#, CheckboxGroup, 
from bokeh.models.tools import BoxZoomTool, ResetTool, SaveTool #PanTool#, TapTool
# from bokeh.transform import transform

reset_output # Clean up the catch


## Markers and colors Vector -> SHOULD BE UPDATED IF THE NUMBER OF CHPs OR CHILLERS CHANGES
marks = ['*', 'diamond', 'o+', 'inverted_triangle', 'x', '+', 'square_cross',
        'o', 'square_x', 'ox', 'square', 'triangle', '*',
        'o', 'diamond', 'inverted_triangle', '+'] # The last one is repeated as there's only 15 markers in Bokeh
###### COULD NOT BE USED DUE TO THE LIBRARY'S BUG IN USING DIFFERENT ARROWS FOR A SINGLE COLUMN-->CHECK BACK LATER


colors = d3['Category20b'][20] + d3['Category20c'][12]


# =============================================================================
## CHP/Chiller/Solar Types used in the individual neighborhood
CHP_Types = {}
CHP_Types[1] = 'Gas_Turbine_1'
CHP_Types[2] = 'Gas_Turbine_2'
CHP_Types[3] = 'Gas_Turbine_3'
CHP_Types[4] = 'Gas_Turbine_4'
CHP_Types[5] = 'Gas_Turbine_5'
CHP_Types[6] = 'Microturbine_1'
CHP_Types[7] = 'Microturbine_2'
CHP_Types[8] = 'Microturbine_3'
CHP_Types[9] = 'Reciprocating_Engine_1'
CHP_Types[10] = 'Reciprocating_Engine_2'
CHP_Types[11] = 'Reciprocating_Engine_3'
CHP_Types[12] = 'Reciprocating_Engine_4'
CHP_Types[13] = 'Reciprocating_Engine_5'
CHP_Types[14] = 'Steam_Turbine_1'
CHP_Types[15] = 'Steam_Turbine_2'
CHP_Types[16] = 'Steam_Turbine_3'
CHP_Types[17] = 'Fuel_Cell_1'
CHP_Types[18] = 'Fuel_Cell_2'
CHP_Types[19] = 'Fuel_Cell_3'
CHP_Types[20] = 'Fuel_Cell_4'
CHP_Types[21] = 'Fuel_Cell_5'
CHP_Types[22] = 'Fuel_Cell_6'
CHP_Types[23] = 'Biomass_1'
CHP_Types[24] = 'Biomass_2'
CHP_Types[25] = 'Biomass_3'
CHP_Types[26] = 'Biomass_4'
CHP_Types[27] = 'Biomass_5'
CHP_Types[28] = 'Biomass_6'
CHP_Types[29] = 'Biomass_7'
CHP_Types[30] = 'Biomass_8'
CHP_Types[31] = 'Biomass_9'
CHP_Types[32] = 'Biomass_10'


Chiller_Types = {}
Chiller_Types[1] = 'Electric_Chiller_1'
Chiller_Types[2] = 'Electric_Chiller_2'
Chiller_Types[3] = 'Electric_Chiller_3'
Chiller_Types[4] = 'Electric_Chiller_4'
Chiller_Types[5] = 'Electric_Chiller_5'
Chiller_Types[6] = 'Electric_Chiller_6'
Chiller_Types[7] = 'Electric_Chiller_7'
Chiller_Types[8] = 'Electric_Chiller_8'
Chiller_Types[9] = 'Electric_Chiller_9'
Chiller_Types[10] = 'Absorption_Chiller_1'
Chiller_Types[11] = 'Absorption_Chiller_2'
Chiller_Types[12] = 'Absorption_Chiller_3'
Chiller_Types[13] = 'Absorption_Chiller_4'
Chiller_Types[14] = 'Absorption_Chiller_5'
Chiller_Types[15] = 'Absorption_Chiller_6'
Chiller_Types[16] = 'Absorption_Chiller_7'
Chiller_Types[17] = 'Absorption_Chiller_8'


WWT_Types = {}
WWT_Types[1] = "FO_MD"
WWT_Types[2] = "FO_RO"
WWT_Types[3] = "CWWTP"
# =============================================================================


def main(df, filename):
    ## Input data
    # =============================================================================
    # rnd_range = random.sample(range(1, 295200-1), 100)
    # file = np.loadtxt('SDO_LHS_TestRuns288_Constraint_SF_Test.txt')[rnd_range]  ## TOY RUN
    # =============================================================================
    #file = np.loadtxt('SDO_LHS_TestRuns288_Constraint_SF_Test.txt')  ## Main RUN
    #df = pd.read_csv('SDO_LHS_TestRuns288_Constraint_SF_Test.txt', delimiter=' ', header=None, dtype='float')
    
    ## TEST CASES
    #df = pd.read_csv('Pareto_front.csv', header=None, dtype='float')
    #df = pd.read_csv('SDO_LHS_FullHallofFame288_Constraint_SF_Test.txt', delimiter=' ', header=None, dtype='float')
    #df = pd.read_csv('Pareto_front_LCC_Eff.csv', header=None, dtype='float')
#    df = pd.read_csv('Pareto_front_PyGMO_LCC_Eff.csv', header=None, dtype='float')
    ## END OF TEST CASES
    df = pd.DataFrame(df) # If input is numpy array
    
    ## Initial filtering of the data
    df = df[df[38] > 0] # Filtering out individuals with GFA = 0 ## Zero GFA=0's after normalizing the objectives and using near zero GFA for trivial answers
    duplicates = df.duplicated() # Dropping the duplicate values ## 226 originally
    df = df[duplicates==False]
    df = df.fillna(0) ## Filling in the NaN's (861 occurrences) with zero. All the NaNs are in building percent ratios
    
    df[26] /= df[38] # Normalized LCC in $ per m2 GFA
    df[27] /= df[38] # Normalized CO2 in tonnes per m2 GFA
    
    #df = df[df[26] <= 10**4] # Filtering out individuals with $/m2 > 10^6
    #df = df[df[27] <= 2*10**3] # Filtering out individuals with tonnes/m2 > 2*10^3
    
    df[25] *= 100 # Converting % total eff to fraction
    df[28] *= 100 # Converting % CHP eff to fraction
    
    ### X and Y parameters of the graph
    #list_x = df[25]*100 # Overall Eff
    #list_y = df[26] # LCC
    
    ## Define alpha values for the glyphs
    alpha=np.ones(len(df[25]))
    #muted_alpha=np.ones(len(list_x))*0.2
    
    
    ## Type Percentages
    # Helper fxn
    def Type_Percent_Maker(j): ## Function for creating the ||||| bar indicators of percent types
    #    return np.array([int(np.round(100*df.iloc[i,j]))*'|' if ~np.isnan(df.iloc[i,j]) else 0 for i in range(len(list_y))])
        test = (np.round(df[j]*100)).apply(int) # getting percentages for the decimal perent ratios
        return test.apply(lambda x: x*'|') # Multiplying the integer by | to get the bar indicator
    # Creating the '|||||' strings for type_percents
    Residential = Type_Percent_Maker(29)
    Office = Type_Percent_Maker(30)
    Commercial = Type_Percent_Maker(31)
    Warehouse = Type_Percent_Maker(32)
    Hotel = Type_Percent_Maker(33)
    Hospital = Type_Percent_Maker(34)
    School = Type_Percent_Maker(35)
    
    # Total Gross Floor Area
    GFA = df[38]
    
    ## Point performance attributes
    Overall_Efficiency = df[25]
    LCC_Nrm = df[26] # Normalized LCC in $ per m2 GFA
    SCC_Nrm = df[27] # Normalized CO2_e in tonnes per m2 GFA
    CHP_Efficiency = df[28]
    
    ## CHP, Chiller and Solar % assignments
    CHP = np.array([CHP_Types[int(i)] for i in df[21]]) # Making strings of CHP names instead of integers
    Chiller = np.array([Chiller_Types[int(i)] for i in df[22]]) # Making strings of Chiller names instead of integers
    WWT = np.array([WWT_Types[int(i)] for i in df[24]]) # Making strings of WWT module names instead of integers
    #CHP_Chiller = np.array([CHP_Types[int(i)]+' & '+Chiller_Types[int(j)] for (i,j) in zip(df[21],df[22])]) # Combined chiller_CHP name
    Solar = df[23]
    
    ## Defining colors based on 
    color0 = np.array([colors[int(i)-1] for i in df[21]]) # Colors based on CHP
    #marker0 = np.array([marks[int(i)-1] for i in df[22]]) # Markers based on Chillers # Marker does not work as color does for a column
    
    ## Clean-up
    df = None
    #list_x = None
    #list_y = None
    
    ## Defining data-source of the points # REMOVED: marker = marker0, CHP_Chiller=CHP_Chiller, 
    source = ColumnDataSource(data=dict(x=SCC_Nrm, y=LCC_Nrm,
                                color=color0, alpha=alpha,
                                Overall_Efficiency=Overall_Efficiency, CHP_Efficiency=CHP_Efficiency,
                                Residential=Residential, Office=Office, Commercial=Commercial,
                                Warehouse=Warehouse, Hotel=Hotel, Hospital=Hospital, School=School,
                                GFA=GFA, CHP=CHP, Chiller=Chiller, WWT=WWT, Solar=Solar)) ## CHANGE WHEN CHANGING AXES
    
    
    ## Defining the hover tooltip ## REMOVED: ,('Alpha', '@alpha')
    hover = HoverTool(tooltips=[
        ('Overall_Efficiency (%)','@Overall_Efficiency{f}'),
        ('CHP_Efficiency (%)','@CHP_Efficiency{f}'),
        ('LCC ($/m2)','@y{e}'),
        ('SCC ($/m2)','@x{e}'),
        ('GFA (m2)','@GFA{e}'),
        ('Solar R_Area (%)', '@Solar{f}'),
        ('Residential', '@Residential'),
        ('Office', '@Office'),
        ('Commercial', '@Commercial'),
        ('Warehouse', '@Warehouse'),
        ('Hotel', '@Hotel'),
        ('Hospital', '@Hospital'),
        ('School', '@School'),
        ('CHP Type', '@CHP'),
        ('WWT Type', '@WWT'),
        ('Chiller Type', '@Chiller')], attachment='vertical')  ## CHANGE WHEN CHANGING AXES
    
    # =============================================================================
    # ## Color mapping the glyphs (points)
    # mapper = LinearColorMapper(palette=plasma(256), low=min(list_y)+min(list_x), high=max(list_y)+max(list_x))
    # =============================================================================
    
    ## Creating and formatting the figure
    p = figure(sizing_mode='stretch_both', tools=[hover, BoxZoomTool(), ResetTool(), SaveTool()],
                                         title="Life Cycle Cost vs Social Cost of Carbon",
                                         x_axis_label="SCC ($/m2)",
                                         y_axis_label="LCC ($/m2)",
                                         output_backend="webgl") ## CHANGE WHEN CHANGING AXES
    
    ## Plotting the points from the data source and in the defined figure
    # p.circle('x', 'y', size=5, source=source, fill_color=transform('y', mapper))
    
    
    p.scatter(source=source, x='x', y='y',
              size=3, legend='CHP', color='color', alpha='alpha')
    
    p.legend.location = "bottom_right"
    p.legend.orientation = "vertical"
    p.legend.background_fill_alpha = 0.5
    p.legend.label_text_font_size = '6pt'
    p.legend.spacing = 0
    p.legend.margin = 0
    #p.legend.click_policy="hide"
    
    ## Defining the sliders' callback js
    #Slider_Callback = CustomJS(args=dict(sources=sources), code="""
    #Slider_Callback = CustomJS(args=dict(source=ColumnDataSource(df)), code="""
    Slider_Callback = CustomJS(args=dict(source=source), code="""
            var data = source.data;
            
            var chps = CHP_Types;
            var chillers = Chiller_Types;
            var wwts = WWT_Types;
            
            var lcc_max = lcc.value;
            var carb_max = carb.value;
            var gfa = gfa.value;
            var res = res.value;
            var off = off.value;
            var com = com.value;
            var war = war.value;
            var hot = hot.value;
            var hos = hos.value;
            var sch = sch.value;
            var chp_choice = chp_choice.active;
            var chiller_choice = chiller_choice.active;
            var wwt_choice = wwt_choice.active;
            
            
            // CHANGE WHEN CHANGING AXES
            var alpha = data['alpha'];
            var LCC = data['y'];
            var Carbon_Emission = data['x'];
            var GFA = data['GFA'];
            var Residential = data['Residential'];
            var Office = data['Office'];
            var Commercial = data['Commercial'];
            var Warehouse = data['Warehouse'];
            var Hotel = data['Hotel'];
            var Hospital = data['Hospital'];
            var School = data['School']; 
            var CHP = data['CHP'];
            var Chiller = data['Chiller'];
            var WWT = data['WWT'] 
            
            //var filtered = new Set([]) // Set of filtered indices
            
            const alpha_min = 0.0
            
            // Filtering function
            function Filter(i) {
                    alpha[i] = alpha_min;
                    //old filter: x[i] = y[i] = null
                    //filtered.add(i)
            }
            
            // Un-filtering function
            function Unfilter(i) {
                    alpha[i] = 1.0;
            }
            
            
            
            
            // Max filtering function
            function MaxFilter(i, variable, limit) {
                return (variable[i] > limit)
            }
            
            //function MaxFilter(variable, limit) {
            //    for (var i = 0; i < variable.length; i++) {
            //            //old filter: if (variable[i]==null) continue; 
            //            if ((variable[i] > limit) && (alpha[i]!=alpha_min)) {
            //                    Filter(i);
            //            }
            //            //if ((variable[i] <= limit) && (alpha[i]==alpha_min)) {
            //            //        Unfilter(i);
            //            //}
            //    }
            //}
            
            
            
            
            // Range filtering function
            function RangeFilter(i, variable, limit) {
                return (variable[i].length < limit[0] || variable[i].length > limit[1])
            }
            
            function RangeFilter_GFA(i, variable, limit) {
                return (variable[i]/1000000 < limit[0] || variable[i]/1000000 > limit[1])
            }
            
            
            //function RangeFilter(variable, limit) {
            //    for (var i = 0; i < variable.length; i++) {
            //        //if (variable[i]==null) continue;
            //        if ((variable[i].length < limit[0] || variable[i].length > limit[1]) && (alpha[i]!=alpha_min)) {
            //                Filter(i);
            //        }
            //        //if ((variable[i].length >= limit[0] && variable[i].length <= limit[1]) && (alpha[i]==alpha_min)) {
            //        //        Unfilter(i);
            //        //}
            //    }
            //}
                    
                        
            // CHP/Chiller/WWT list-based filtering
            function ListFilter(i, variable, choice, list_all, active_list) {
                var flag = !(active_list.includes(variable[i]));
                return flag
            }
            
            //function ListFilter(variable, choice, list_all) {
            //    active_list = []
            //    for (var i = 0; i < Object.keys(list_all).length; i++) {
            //            if (i in choice) active_list.push(list_all[i]);
            //    }
            //    
            //    for(var i = 0; i < variable.length; i++) {
            //            //if (variable[i]==null) continue;
            //            var flag = !(active_list.includes(variable[i]));
            //            if (flag && (alpha[i]!=alpha_min)) Filter(i);
                        //if (active_list.includes(variable[i]) && (alpha[i]==alpha_min)) Unfilter(i);
            //    }
            
            //}
            
            
            
            
            // Applying filters
            // Creating list of active CHP and Chiller names
            var active_CHPs = []
            for (var i = 0; i < (Object.keys(chps)).length; i++) {
                    if (chp_choice.includes(i)) active_CHPs.push(chps[i+1]);
            }
    
            var active_Chillers = []
            for (var i = 0; i < (Object.keys(chillers)).length; i++) {
                    if (chiller_choice.includes(i)) active_Chillers.push(chillers[i+1]);
            }
            
            var active_WWTs = []
            for (var i = 0; i < (Object.keys(wwts)).length; i++) {
                    if (wwt_choice.includes(i)) active_WWTs.push(wwts[i+1]);
            }
            
            
            
            // Filtering
            for (var i = 0; i < alpha.length; i++) {
                var cond = []
                cond[0] = MaxFilter(i, LCC, lcc_max); // Filtering the data based on lcc_max
                cond[1] = MaxFilter(i, Carbon_Emission, carb_max);
                cond[2] = RangeFilter_GFA(i, GFA, gfa); // ++++NOTE THE UNIT OF GFA AND ITS CONVERSION++++
                cond[3] = RangeFilter(i, Residential, res); // Filtering the data based on res range  
                cond[4] = RangeFilter(i, Office, off);
                cond[5] = RangeFilter(i, Commercial, com);
                cond[6] = RangeFilter(i, Warehouse, war);
                cond[7] = RangeFilter(i, Hotel, hot);
                cond[8] = RangeFilter(i, Hospital, hos);
                cond[9] = RangeFilter(i, School, sch);
                cond[10] = ListFilter(i, CHP, chp_choice, chps, active_CHPs); // Filtering the data based on active CHP values 
                cond[11] = ListFilter(i, Chiller, chiller_choice, chillers, active_Chillers);
                cond[12] = ListFilter(i, WWT, wwt_choice, wwts, active_WWTs);
                
                var flag2 = !cond.includes(true)
                
                if (cond.includes(true) && alpha[i]!=alpha_min){
                    Filter(i);
                } else if (flag2 && alpha[i]==alpha_min) {
                    Unfilter(i);
                } 
            }
            
            
            // Filtering the data based on lcc_max
            //MaxFilter(LCC, lcc_max);  
            //MaxFilter(Carbon_Emission, carb_max);
            // ++++NOTE THE UNIT OF GFA AND ITS CONVERSION++++
            //RangeFilter(GFA, gfa*43560);  
            //RangeFilter(Residential, res);
            //RangeFilter(Office, off);
            //RangeFilter(Commercial, com);
            //RangeFilter(Warehouse, war); 
            //RangeFilter(Hotel, hot);   
            //RangeFilter(Hospital, hos);  
            //RangeFilter(School, sch);   
            //ListFilter(CHP, chp_choice, chps);             
            //ListFilter(Chiller, chiller_choice, chillers);
            
            // Unfiltering
            //for(var i = 0; i < alpha.length; i++) {
            //    flag = !filtered.has(i)
            //    if (flag && (alpha[i] == alpha_min)) Unfilter(i)
            //}
                    
            source.change.emit();
    """)
        
    ## Defining the sliders and the buttons
    Num_Steps = 20
    Max_LCC_Nrm = np.max(LCC_Nrm)
    Max_SCC_Nrm = np.max(SCC_Nrm)
    Min_GFA = np.min(GFA)
    Max_GFA = np.max(GFA)
    
    lcc_slider = Slider(start=0, end=Max_LCC_Nrm, value=Max_LCC_Nrm, step=Max_LCC_Nrm/Num_Steps, title="Max LCC/GFA ($/m2)")
    carb_slider = Slider(start=0, end=Max_SCC_Nrm, value=Max_SCC_Nrm, step=Max_SCC_Nrm/Num_Steps, title="Max SCC/GFA ($/m2)")
    gfa_slider = RangeSlider(start=Min_GFA/10**6, end=Max_GFA/10**6, value=(Min_GFA/10**6,Max_GFA/10**6), step=(Max_GFA-Min_GFA)/10**6/Num_Steps, title="Total-GFA Range (km2)")
    res_slider = RangeSlider(start=0, end=100, value=(0,100), step=2, title="Residential-GFA Ratio Range (%)")
    off_slider = RangeSlider(start=0, end=100, value=(0,100), step=2, title="Office-GFA Ratio Range (%)")
    com_slider = RangeSlider(start=0, end=100, value=(0,100), step=2, title="Commercial-GFA Ratio Range (%)")
    war_slider = RangeSlider(start=0, end=100, value=(0,100), step=2, title="Warehouse-GFA Ratio Range (%)")
    hot_slider = RangeSlider(start=0, end=100, value=(0,100), step=2, title="Lodging-GFA Ratio Range (%)")
    hos_slider = RangeSlider(start=0, end=100, value=(0,100), step=2, title="Hospital-GFA Ratio Range (%)")
    sch_slider = RangeSlider(start=0, end=100, value=(0,100), step=2, title="Educational-GFA Ratio Range (%)")
    
    checkbox_chp = CheckboxButtonGroup(
            labels=list(CHP_Types.values()), active=list(range(32)))
    checkbox_chiller = CheckboxButtonGroup(
            labels=list(Chiller_Types.values()), active=list(range(17)))
    checkbox_wwt = CheckboxButtonGroup(
            labels=list(WWT_Types.values()), active=list(range(3)))
    
    
    
    apply_button = Button(label="Apply", button_type="success", callback=Slider_Callback)
    Slider_Callback.args["lcc"] = lcc_slider
    Slider_Callback.args["carb"] = carb_slider
    Slider_Callback.args["gfa"] = gfa_slider
    Slider_Callback.args["res"] = res_slider
    Slider_Callback.args["off"] = off_slider
    Slider_Callback.args["com"] = com_slider
    Slider_Callback.args["war"] = war_slider
    Slider_Callback.args["hot"] = hot_slider
    Slider_Callback.args["hos"] = hos_slider
    Slider_Callback.args["sch"] = sch_slider
    Slider_Callback.args["chp_choice"] = checkbox_chp
    Slider_Callback.args["chiller_choice"] = checkbox_chiller
    Slider_Callback.args["wwt_choice"] = checkbox_wwt
    Slider_Callback.args["Chiller_Types"] = Chiller_Types  # Dictionary of Chiller names
    Slider_Callback.args["CHP_Types"] = CHP_Types # Dictionary of CHP names
    Slider_Callback.args["WWT_Types"] = WWT_Types # Dictionary of WWT module names
    
    
    ## Defining the layout to be shown in the figure
    layout = row(children=[p, widgetbox(lcc_slider, carb_slider, gfa_slider, 
                              res_slider, off_slider, com_slider, war_slider,
                              hot_slider, hos_slider, sch_slider, apply_button),
                              row(checkbox_chp, checkbox_chiller, checkbox_wwt)],
                sizing_mode='scale_height')
    
    #output_file('LCC_Overall_Eff_Filter.html', title='PRK') ## CHANGE WHEN CHANGING THE AXES
    #output_file('Pareto_LCC_Overall_Eff_Filter.html', title='PRK') ## CHANGE WHEN CHANGING THE AXES
    SavedFileName = filename + '.html'
    output_file(SavedFileName, title='PRK') ## CHANGE WHEN CHANGING THE AXES
    show(layout)
