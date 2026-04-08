import pandas as pd
import os
from scripts.format_attributes import format_attributes
from scripts.retrieve_acs import retrieve_acs
from scripts.retrieve_sf3 import retrieve_sf3
from scripts.calc_socio_economic_profiles import calc_socio_economic_profiles

from scripts.neighborhood_profiles import neighborhood_profiles, neighborhood_profiles_vs_citywide, tract_profiles

key = os.environ.get('CENSUS_KEY')

attribute_df = pd.read_csv(r'./lookup_tables/0_attribute_lookup - master - dec.csv', dtype=str)
geo_lookup_df = pd.read_csv(r'./lookup_tables/geo_lookup_2000to2020.csv', dtype=str)

acs_attribute_ids, sf3_attribute_ids = format_attributes(attribute_df)

# these functions pull the attributes and store raw values in csv's per year
retrieve_acs(acs_attribute_ids, range(2010, 2025), key)
retrieve_sf3(sf3_attribute_ids, key)

years = [2000, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
# for each year and neighborhood, this function aggregates variables based on definitions in attribute_df
calc_socio_economic_profiles(attribute_df, years, geo_lookup_df, output_path='./output')

# Generate neighborhood profiles:
neighborhood_profiles(years, geo_lookup_df)
neighborhood_profiles_vs_citywide(years, geo_lookup_df)
tract_profiles(years, geo_lookup_df)