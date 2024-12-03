# socio-economic-profiles (in progress)

This code creates the socio-economic profile data for the San Francisco Planning Department's Neighborhood Socio-Economic Profiles. Socio-economic profiles data is derived from the American Community Survey 5-year data and is created annually by the Planning Department. Tract level socio-economic data is combined at the neighborhood and district level for the City of San Francisco. This code is based off methods created by Michael Webster and others. Launch the Jupyter Notebook to calculate socio-economic profiles data, visualize results, and download.  

<iframe allow="geolocation" src="https://data.sfgov.org/dataset/Analysis-Neighborhoods/p5b7-5n3h/embed?width=800&height=600" width="800" height="600" style="border:0; padding: 0; margin: 0;"></iframe>

## Installation

Set up a [Python virtual environment](https://docs.python.org/3/library/venv.html) and activate

```bash
pip install virtualenv
python3 -m venv /path/to/new/virtual/environment/env
source env/bin/activate
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Python packages via requirements.txt.

```bash
pip install requirements.txt
```

To visualzed results on a map the Geopandas Python library is used. Geopandas requires special attention to install on Windows. Install Fiona, GDAL, Geopandas, pyproj, and Shapely via windows Binaries by following the instructions [here](https://towardsdatascience.com/geopandas-installation-the-easy-way-for-windows-31a666b3610f). Alternatively install Geopandas via Conda. 

## Usage

Launch the Jupyter Notebook
```bash
jupyter notebook
```

## Files
- /build_socioeconomic_profiles - dec and acs.ipynb: Python Notebook for calculating socio-economic profiles (historical to present)
- /Data_Items_And_Sources_2019.xlsx: Excel file containing attribute calculations that profile calculations are based on
- /attribute_lookup - master - include dec.csv: Lookup table with attribute categories, attributes names and attribute IDs for all attributes needed to calculate the profile data. Includes definition of how to calculate (median, as is, weighted average, or other)
- /geo_lookup_2000to2020.csv: Lookup table with neighborhood for each tract in San Francisco for 2000, 2010, and 2020. Census tracts are subject to change every 10 years.  
- /acs_median_lookup.csv: Lookup table needed for calculating medians. Contains name, id, range_start, and range_end for median calcs. (ACS)
- /sf3_median_lookup.csv: Lookup table needed for calculating medians. Contains name, id, range_start, and range_end for median calcs. (DEC, Summary Files 3 Table (SF3))

