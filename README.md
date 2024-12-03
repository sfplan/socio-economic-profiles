# socio-economic-profiles 

This code creates the socio-economic profile data for the San Francisco Planning Department's Neighborhood Socio-Economic Profiles. Socio-economic profiles data is derived from the American Community Survey 5-year data and is created annually by the Planning Department. Tract level socio-economic data is combined at the neighborhood and district level for the City of San Francisco. This code is based off methods created by Michael Webster and others. Launch the Jupyter Notebook to calculate socio-economic profiles data, visualize results, and download.  

## Neighborhood summaries
The [Neighborhoods](https://data.sfgov.org/-/Analysis-Neighborhoods/p5b7-5n3h) dataset was created by grouping 2010 Census tracts, using common real estate and resident's definitions for the purpose of providing consistency in the analysis and reporting of socio-economic, demographic, and environmental data, and data on City-funded programs and services. These neighborhoods are not codified in Planning Code nor Administrative Code, although this map is referenced in Planning Code Section 415 as the American Community Survey Neighborhood Profile Boundaries Map.
Note: These are NOT statistical boundaries as they are not controlled for population size. This is also NOT an official map of neighborhood boundaries in SF but an aggregation of Census tracts and should be used in conjunction with other spatial boundaries for decision making.

This dataset is produced by assigning Census tracts to neighborhoods based on existing neighborhood definitions used by Planning and MOHCD. A qualitative assessment is made to identify the appropriate neighborhood for a given tract based on understanding of population distribution and significant landmarks. Once all tracts have been assigned a neighborhood, the tracts are dissolved to produce this dataset, Analysis Neighborhoods.

This dataset is static. Changes to the analysis neighborhood boundaries will be evaluated as needed by the Analysis Neighborhood working group led by DataSF and the Planning department and includes staff from various other city departments. 

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

