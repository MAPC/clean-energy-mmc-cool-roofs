==============================

The goal of Task 4 of the Metro Boston Cool Roofs Project is to develop a site suitability analysis that identifies prime locations for cool roof installations in the Metro Mayors region. The analysis assesses each rooftop based on key physical characteristics of the roofs themselves as well as the environmental, economic, and social characteristics of the land parcels and census geographies in which they reside. 

This methodology uses LIDAR data, provided by MassGIS, to extract roof shapes and color intensity to identify flat and dark roofs on buildings in the 16 Metro Mayors communities. Once potential cool roof sites (i.e., flat, dark roofs) are identified, MAPC used Python to join the sites with parcel data and summarized statistics (e.g., total number and square footage of residential vs commercial vs municipal cool roof sites).  

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    │    
    ├── notebooks          <- Jupyter notebooks.
    │   ├── 01-running-cool-roof-process.ipynb    <- runs scripts for MMC communities
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py  <-reads in data layers from MAPC's network drives
    │   │   └── public_uses.py   <- lists land uses that are associated with public and municipal ownership
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── create_rasters.py   <- ArcPy-based functions for transforming Lidar into rasters
    │   │   └── custom_functions.py <- Functions that enrich roofprint data with cool roof fields
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
