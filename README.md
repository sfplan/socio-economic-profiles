# socio-economic-profiles (in progress)

This code creates the socio-economic profile data for the San Francisco Planning Department's Neighborhood Socio-Economic Profiles. Socio-economic profiles data is derived from the American Community Survey 5-year data and is created annually by the Planning Department. Tract level socio-economic data is combined at the neighborhood and district level for the City of San Francisco. This code is based off methods created by Michael Webster and others. Launch the Jupyter Notebook to calculate socio-economic profiles data, visualize results, and download.  

<script type="text/javascript" charset="UTF-8" data-locale="en" data-socrata-domain="data.sfgov.org" src="https://data.sfgov.org/component/visualization/v1/socrata-visualizations-loader.js"></script>
<a class="socrata-visualization-embed" data-embed-version="1" data-height="600" data-socrata-domain="data.sfgov.org" data-vizcan-uid="p5b7-5n3h" data-vif="{&quot;configuration&quot;:{&quot;viewSourceDataLink&quot;:true,&quot;mapCenterAndZoom&quot;:{&quot;center&quot;:{&quot;lng&quot;:-122.44245688017713,&quot;lat&quot;:37.76179471162882},&quot;zoom&quot;:11.581334358938244},&quot;showLegendForMap&quot;:false,&quot;showDataTableControl&quot;:false,&quot;basemapOptions&quot;:{&quot;searchBoundaryLowerRightLongitude&quot;:-122.35696687665975,&quot;searchBoundaryUpperLeftLongitude&quot;:-122.51494757950903,&quot;searchBoundaryUpperLeftLatitude&quot;:37.833297639488315,&quot;navigationControl&quot;:true,&quot;basemapStyle&quot;:&quot;mapbox://styles/mapbox/streets-v9&quot;,&quot;geoCoderControl&quot;:false,&quot;geoLocateControl&quot;:false,&quot;searchBoundaryLowerRightLatitude&quot;:37.70813199967893},&quot;mapPitchAndBearing&quot;:{&quot;bearing&quot;:0,&quot;pitch&quot;:0},&quot;datasetMetadata&quot;:false,&quot;panAndZoom&quot;:true,&quot;showMultiplePointsSymbolInLegend&quot;:true,&quot;locateUser&quot;:false},&quot;series&quot;:[{&quot;visible&quot;:true,&quot;color&quot;:{&quot;primary&quot;:&quot;#eb6900&quot;},&quot;mapOptions&quot;:{&quot;shapeOutlineColor&quot;:&quot;#636363&quot;,&quot;simplificationLevel&quot;:&quot;1&quot;,&quot;shapeFillOpacity&quot;:53,&quot;mapType&quot;:&quot;boundaryMap&quot;,&quot;shapeFillColor&quot;:&quot;#969696&quot;,&quot;shapeOutlineWidth&quot;:1,&quot;additionalFlyoutColumns&quot;:[&quot;nhood&quot;]},&quot;showLegend&quot;:true,&quot;type&quot;:&quot;map&quot;,&quot;dataSource&quot;:{&quot;measure&quot;:{&quot;aggregationFunction&quot;:&quot;count&quot;},&quot;name&quot;:&quot;Analysis Neighborhoods&quot;,&quot;type&quot;:&quot;socrata.soql&quot;,&quot;datasetUid&quot;:&quot;j2bu-swwd&quot;,&quot;dimension&quot;:{&quot;columnName&quot;:&quot;the_geom&quot;,&quot;aggregationFunction&quot;:null},&quot;filters&quot;:[]},&quot;primary&quot;:true,&quot;label&quot;:null}],&quot;format&quot;:{&quot;type&quot;:&quot;visualization_interchange_format&quot;,&quot;version&quot;:4},&quot;description&quot;:&quot;A. SUMMARY\nThe Department of Public Health and the Mayor’s Office of Housing and Community Development, with support from the Planning Department, created these 41 neighborhoods by grouping 2010 Census tracts, using common real estate and residents’ definitions for the purpose of providing consistency in the analysis and reporting of socio-economic, demographic, and environmental data, and data on City-funded programs and services. These neighborhoods are not codified in Planning Code nor Administrative Code, although this map is referenced in Planning Code Section 415 as the “American Community Survey Neighborhood Profile Boundaries Map.\nNote: These are NOT statistical boundaries as they are not controlled for population size. This is also NOT an official map of neighborhood boundaries in SF but an aggregation of Census tracts and should be used in conjunction with other spatial boundaries for decision making.\nB. HOW THE DATASET IS CREATED\nThis dataset is produced by assigning Census tracts to neighborhoods based on existing neighborhood definitions used by Planning and MOHCD. A qualitative assessment is made to identify the appropriate neighborhood for a given tract based on understanding of population distribution and significant landmarks. Once all tracts have been assigned a neighborhood, the tracts are dissolved to produce this dataset, Analysis Neighborhoods.\nC. UPDATE PROCESS\nThis dataset is static. Changes to the analysis neighborhood boundaries will be evaluated as needed by the Analysis Neighborhood working group led by DataSF and the Planning department and includes staff from various other city departments. Contact us\nfor any questions.\nD. HOW TO USE THIS DATASET\nDownloading this dataset and opening it in Excel may cause some of the data values to be lost or not display properly (particularly the Analysis Neighborhood column). For a simple list of Analysis Neighborhoods without geographic coordinates, click here: https://data.sfgov.org/resource/xfcw-9evu.csv?$select=nhood\nE. RELATED DATASETS\n2020 Census tracts assigned a neighborhood\n2010 Census tracts assigned a neighborhood&quot;,&quot;id&quot;:&quot;7ccf29a2-1e4d-411b-a264-d4024f5ab02c&quot;,&quot;title&quot;:&quot;Analysis Neighborhoods&quot;,&quot;currentMapLayerIndex&quot;:0}" data-width="800" href="https://data.sfgov.org/-/Analysis-Neighborhoods/j2bu-swwd?referrer=embed" rel="external" target="_blank">View the data</a>
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

