'''

Retrieve data from Census API
All socio-economic data comes from the Census ACS 5-year estimates and is available at the tract level through the
census API. API documentation and data for the 2023 ACS data and previous years is available
(https://www.census.gov/data/developers/data-sets/acs-5year.html). DEC 2000, 2010, and 2020 data is also
 available (https://www.census.gov/data/developers/data-sets/decennial-census.2000.html#list-tab-517985795)

Build Census API URL and Make Query
The code below builds the URL for the census API call to get relevant attribute data at the tract level
 for San Francisco County. The Census API accepts up to 50 attributes at a time. Therefore the attribute
  list is first grouped into sublists of 45 attribute IDs. An API call is. Below define:

Tract code is '*' to collect all tracts
State code is '06' for CA
County code is '075' for San Francisco County
Attributes are defined by the attribute id list and includes all relevant attributes for the socio-economic data calcs
'''
# base libraries
import requests, json, os
import pandas as pd
import numpy as np
from collections import defaultdict

import warnings
warnings.filterwarnings("ignore")

CENSUS_KEY = os.environ.get('CENSUS_KEY')

# function builds the api URL from tract_code, state_code, county_code, and attribute ids. Requires Census key (free)
def build_census_url(year, survey, tablename, county_code, state_code, tract_code, level, attribute_ids, CENSUS_KEY):
    attributes = ','.join(attribute_ids)
    if level == 'tract':
        census_url = r'https://api.census.gov/data/{}/{}/{}?get={}&for=tract:{}&in=state:{}&in=county:{}&key={}'.format(year, survey, tablename, attributes, tract_code, state_code, county_code, CENSUS_KEY)
    else:
        census_url = r'https://api.census.gov/data/{}/{}/{}?get={}&for=county:{}&in=state:{}&key={}'.format(year, survey, tablename, attributes, county_code, state_code, CENSUS_KEY)
    return census_url

def build_census_url_economic_chars(year, survey, tablename, county_code, state_code, tract_code, level, attribute_ids, CENSUS_KEY):
    attributes = ','.join(attribute_ids)
    if level == 'tract':
        census_url = r'https://api.census.gov/data/{}/{}/{}/profile/groups/?get=group({})&for=tract:{}&in=state:{}&in=county:{}&key={}'.format(year, survey, tablename, attributes, tract_code, state_code, county_code, CENSUS_KEY)
    else:
        census_url = r'https://api.census.gov/data/{}/{}/{}/profile/groups/?get=group({})&for=county:{}&in=state:{}&key={}'.format(year, survey, tablename, attributes, county_code, state_code, CENSUS_KEY)
    return census_url

def build_census_url_subject_tables(year, survey, tablename, county_code, state_code, tract_code, level, attribute_ids, CENSUS_KEY):
    attributes = ','.join(attribute_ids)
    if level == 'tract':
        census_url = r'https://api.census.gov/data/{}/{}/{}?get=group({})&for=tract:{}&in=state:{}&in=county:{}&key={}'.format(year, survey, tablename, attributes, tract_code, state_code, county_code, CENSUS_KEY)
    else:
        census_url = r'https://api.census.gov/data/{}/{}/{}?get=group({})&for=county:{}&in=state:{}&key={}'.format(year, survey, tablename, attributes, county_code, state_code, CENSUS_KEY)
    return census_url

# function makes a single api call and collects results in a pandas dataframe
def make_census_api_call(census_url):
    # make API call to Census
    resp = requests.get(census_url)

    if resp.status_code != 200:
        # this means something went wrong
        resp.raise_for_status()

    # retrieve data as json and convert to Pandas Dataframe
    data = resp.json()
    headers = data.pop(0)

    df = pd.DataFrame(data, columns=headers)

    # convert values that are not state, county, or tract to numeric type
    try:
        cols = [i for i in df.columns if i not in ["state", "county", "tract"]]
    except:
        cols = [i for i in df.columns if i not in ["state", "county"]]

    for col in cols:
        df[col] = pd.to_numeric(df[col])

    return df