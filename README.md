# Wastewater_Energy_Optimization
Author: Pouya Rezazadeh Kalehbasti
Based on paper by Best et al. (2015)*
Readme based on https://github.com/othneildrew/Best-README-Template



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
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
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

This GitHub repository contains the files required for reproducing the results published in paper XXXXXXXXXX.



### Built With

This section should list any major frameworks that you built your project using. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.
* [Python](https://www.python.org/)



<!-- GETTING STARTED -->
## Getting Started

Follow the steps below to get a local copy of the project and be able to run it.

### Prerequisites

Install these required packages on your Python.
* pip
  ```sh
  pip install -r requirements.txt
  ```

### Installation

1. Clone the repo onto your local machine
   ```sh
   git clone https://github.com/PouyaREZ/Wastewater_Energy_Optimization.git
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

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Img Shields](https://shields.io)
* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Pages](https://pages.github.com)
* [Animate.css](https://daneden.github.io/animate.css)
* [Loaders.css](https://connoratherton.com/loaders)
* [Slick Carousel](https://kenwheeler.github.io/slick)
* [Smooth Scroll](https://github.com/cferdinandi/smooth-scroll)
* [Sticky Kit](http://leafo.net/sticky-kit)
* [JVectorMap](http://jvectormap.com)
* [Font Awesome](https://fontawesome.com)





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/PouyaREZ/Wastewater_Energy_Optimization/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/PouyaREZ/Wastewater_Energy_Optimization/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/PouyaREZ/Wastewater_Energy_Optimization/stargazers

[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/PouyaREZ/Wastewater_Energy_Optimization/blob/main/LICENSE














* Best, Robert E., Forest Flager, and Michael D. Lepech. "Modeling and optimization of building mix and energy supply technology for urban districts." Applied energy 159 (2015): 161-177.