# Wastewater_Energy_Optimization
Author: Pouya Rezazadeh Kalehbasti (PhD Candidate in CEE | CS @ Stanford University)

Based on paper by Best et al. (2015)*




<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![MIT License][license-shield]][license-url]





<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
	<li><a href="#references">References</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
This GitHub repository contains the files required for reproducing the results published in paper XXXXXXXXXX.



### Built With

* [Python](https://www.python.org/)



<!-- GETTING STARTED -->
## Getting Started

Follow the steps below to get a local copy of the project and be able to run it.


### Installation

1. Clone the repo onto your local machine
   ```sh
   git clone https://github.com/PouyaREZ/Wastewater_Energy_Optimization.git
   ```
   1.1. Install these required packages on your Python.
	   ```
	   pip install -r requirements.txt
	   ```
   
2. If you want to rerun the optimization and regenerate the optimization solutions, follow steps 3 to 4 below. Otherwise, go to step 5.
   
3. Solve the optimization problem with genetic algorithm by running the following command in `./Main` directory.
```sh
python3 -m scoop Main.py
```
To run the scenario with a Central Wastewater Treatment plant, set the "CWWTP_Mode" flag to `1` in line 85 of `Main.py`.
Copy the `SDO_LHS_TestRuns288_Constraint_SF_Test.txt` (from `./Main` directory) resulting from the run to some other place.

To run the scenario with integrated water-energy system, set this flag to `0`.
Copy the `SDO_LHS_TestRuns288_Constraint_SF_Test.txt` (from `./Main` directory) resulting from the run to some other place.
   
4. Copy `SDO_LHS_TestRuns288_Constraint_SF_Test.txt` file for the segregated scenario into `./Plotters/RQ1_W_CWWTP_ModConsts_Feb17/`,
and for the integrated scenario into `./Plotters/RQ1_WO_CWWTP_ModConsts_Feb17/`.

5. Run `Plots_Clusters.py` and `Plots_Paper_One.py` from `./Plotters/Results/`.

6. View the figures in `./Plotters/Results/` directory.


<!-- CONTRIBUTING -->
## Contributing

To expand this project, you can do the following:
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


Some of the things you can update or modify in the project:
1. Modify or add a chiller model:
Either in `./Main/AbsorptionChillers.py` or `./Main/ElectricChillers.py`, you need to both modify 
the `Computer` function and add a new function named as your new chiller model, similar to the
existing models.

You also need to update lines 89 and 93 of `./Main/Main.py` with the new count of chiller models.
[E.g., increase the number on line 93 by 1 if you add one chiller]


2. Modify or add a CHP engine model:

In `./Main/CHPEngines.py`, you need to both modify the `Computer` function and add a new function
named as your new CHP model, similar to the existing models.

You also need to update `./Main/CHP_Info.csv` file with the new/modified CHP engine information.

You also need to update lines 88 and 93 of `./Main/Main.py` with the new count of chiller models.
[E.g., increase the number on line 93 by 1 if you add one CHP engine]

2. Modify or add a wastewater treatment model:

Add a new function or modify the existing functions in `./Main/WWT.py`.


3. Modify or add a building archetype:

You need to add/update the 8760-hour demand of cooling, heating, and electricity for the new/updated
archetype to these three files, respectively: `./Main/Hourly_Cooling.csv`, `./Main/Hourly_Heating.csv`,
and `./Main/Hourly_Electricity.csv`. The building type corresponding to each column in these files follows
the order of building types listed in `./Main/Building_Info.csv`.

You also need to add/update the average daily demand, monthly coefficients, and hourly coefficients of
wastewater treatment demand for the new building archetype to `./Main/Profiles.csv`. The building type
corresponding to each column in these files follows the order of building types listed in
`./Main/Building_Info.csv`.

You also need to update `./Main/Building_Info.csv` with the new/modified building archetype information.

You also need to update line 93 of `./Main/Main.py` with the new count of building types, e.g., increase
the number on line 93 by 1 if you add one building type.


3.1 Be careful: your model might consider a building-level chiller to
satisfy the cooling demand of the building. In this case, you need to subtract the cooling demand
satisfied by the electric chiller from the electric load and add it instead to the cooling load.
Same goes for the heating demand of the building.


4. Change the geographic location of running the model:

Modify `./Main/Site_Info.csv` according to the new location. Then update `./Main/Hourly_Weather.csv` with
the meteorological information of the new location.


5. Change the eletricity tariff:

Modify `./Main/Grid_Parameters.csv` with the new electricity tariff. The headings of the columns in the 
existing csv file mentions references used for obtaining the listed data; you can use them for easier
data gathering.






<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Pouya Rezazadeh Kalehbasti - rezazadeh.pouya@gmail.com

Project Link: [https://github.com/PouyaREZ/Wastewater_Energy_Optimization](https://github.com/PouyaREZ/Wastewater_Energy_Optimization)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

Readme based on https://github.com/othneildrew/Best-README-Template






<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/PouyaREZ/Wastewater_Energy_Optimization.svg?style=for-the-badge
[contributors-url]: https://github.com/PouyaREZ/Wastewater_Energy_Optimization/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/PouyaREZ/Wastewater_Energy_Optimization.svg?style=for-the-badge
[forks-url]: https://github.com/PouyaREZ/Wastewater_Energy_Optimization/network/members
[stars-shield]: https://img.shields.io/github/stars/PouyaREZ/Wastewater_Energy_Optimization.svg?style=for-the-badge
[stars-url]: https://github.com/PouyaREZ/Wastewater_Energy_Optimization/stargazers

[license-shield]: https://img.shields.io/github/license/PouyaREZ/Wastewater_Energy_Optimization.svg?style=for-the-badge
[license-url]: https://github.com/PouyaREZ/Wastewater_Energy_Optimization/blob/main/LICENSE





<!-- References -->
## References

* Best, Robert E., Forest Flager, and Michael D. Lepech. "Modeling and optimization of building mix and energy supply technology for urban districts." Applied energy 159 (2015): 161-177.