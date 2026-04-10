'''
Define functions for calculating socio-economic data
The calc_socio_economic_data function takes tract level data from the API call and the
tract/neighborhood lookup dictionary. This function creates all of the socio-economic
data calcs and returns a dictionary. The calcs in this function are derived from the
Data_Items_and_Sources.xlsx file developed by Michael Webster
'''

def check_attribute_ids(available_attribute_ids, attribute_ids):
    ATTRIBUTE_IDS = []
    for i in attribute_ids:
        if i in available_attribute_ids:
            ATTRIBUTE_IDS.append(i)
    return ATTRIBUTE_IDS


# function runs all calcs for each neighborhood
# function runs all calcs for each neighborhood
def calc_socio_economic_data(df, tract_lookup, all_calc_data, all_calc_data_by_tract, \
                             attribute_name, \
                             attribute_ids, base_ids, treatment, year, all_tracts, range_df):
    # nb_name = 'Western Addition/Fillmore Community Boundary'
    # tracts = tract_lookup[nb_name]

    for nb_name, tracts in tract_lookup.items():
        # print(nb_name, tracts)

        # extract attribute information for tracks associated with a neighborhood
        tract_df = df[df['tract'].isin(tracts)]
        available_attribute_ids = tract_df.columns
        # build dictionary with all stats for a neighborhood
        all_calc_data_nb = all_calc_data[nb_name]

        attribute_ids.sort()
        attribute_ids = check_attribute_ids(available_attribute_ids, attribute_ids)
        attribute = tract_df[attribute_ids]
        # print(treatment)
        # print(attribute)
        # print(attribute_ids,base_ids)
        if treatment == 'as is' and base_ids:
            base = tract_df[base_ids]
            null_idx = attribute[pd.isnull(attribute).any(axis=1)].index.tolist() + base[
                pd.isnull(base).any(axis=1)].index.tolist()
            attribute = attribute[attribute.index.isin(null_idx) == False]
            base = base[base.index.isin(null_idx) == False]
            all_calc_data_nb['%s' % attribute_name] = attribute.sum().sum() / base.sum().sum()

        elif treatment == 'wa' and base_ids:
            base = tract_df[base_ids]
            null_idx = attribute[pd.isnull(attribute).any(axis=1)].index.tolist() + base[
                pd.isnull(base).any(1)].index.tolist()
            # print(null_idx)
            attribute = attribute[attribute.index.isin(null_idx) == False]
            base = base[base.index.isin(null_idx) == False]
            # print(attribute,base)
            all_calc_data_nb['%s' % attribute_name] = (attribute.values * base.values).sum() / base.sum().sum()

        elif treatment == 'as is' and not base_ids:
            null_idx = attribute[pd.isnull(attribute).any(axis=1)].index.tolist()
            attribute = attribute[attribute.index.isin(null_idx) == False]
            all_calc_data_nb['%s' % attribute_name] = attribute.sum().sum()

        elif treatment == 'median':
            # print(attribute_name,attribute_ids)
            all_calc_data_nb['%s' % attribute_name] = calc_median(tract_df, range_df, \
                                                                  median_dict[attribute_name.split(',')[0]],
                                                                  attribute_ids, year)

        # try:

        #     print(all_calc_data_nb['%s' %attribute_name])

        # except:

        #     pass

    for tract_name in all_tracts:
        # print(tract_name)
        tract_df = df[df['tract'].isin([tract_name])]

        all_calc_data_nb = all_calc_data_by_tract[tract_name]

        if treatment == 'as is' and base_ids:
            all_calc_data_nb['%s' % attribute_name] = tract_df[attribute_ids].sum().sum() / tract_df[
                base_ids].sum().sum()

        elif treatment == 'as is' and not base_ids:
            all_calc_data_nb['%s' % attribute_name] = tract_df[attribute_ids].sum().sum()

        elif treatment == 'median':
            # print(range_df, attribute_name)
            all_calc_data_nb['%s' % attribute_name] = calc_median(tract_df, range_df,
                                                                  median_dict[attribute_name.split(' by')[0]],
                                                                  attribute_ids, year)

        # try:
        #     print(all_calc_data_nb['%s' %attribute_name])
        # except:
        #     pass
    # print('all_calc_data_nb')
    # print(all_calc_data_nb)
    # print('all_calc_data')
    # print(all_calc_data)
    # print('all_calc_data_by_tract')
    # print(all_calc_data_by_tract)

    return all_calc_data, all_calc_data_by_tract


'''
Calculating Medians
To calculate median values of aggregated geographies you cannot use the mean of component geographies. 
Instead a statistical approximation of the median must be calculated from range tables.

Range variables in the ACS have a unique ID like any other Census variable. They represent the amount 
of a variable within a select range. e.g. number of households with household incomes between $45000-50000.
 Range variable ID's and range information is stored in the median_ranges.csv file in the repository. 
 These range variables and ranges are needed for calculating the median at the neighborhood level.

The below function calculates a median based on range data. This method follows the offical ACS 
documentation for calculating a median

'''

# base libraries
import requests, json, os
import pandas as pd
import numpy as np
from collections import defaultdict

import warnings
warnings.filterwarnings("ignore")

median_dict = {"Median Year Structure Built": 'median_year_structure_built',
               "Median Year Moved In Owner": 'median_year_moved_owner',
               "Median Year Moved In Renter": 'median_year_moved_renter',
               "Median Rent": 'median_rent',
               "Median Contract Rent": 'median_rent_contract',
               "Median Rent as % of Household Income": 'median_rent_percent_of_income',
               "Median Household Income": 'median_household_income',
               "Median Household Income by Race": 'median_household_income_by_race',
               "Median Family Income": 'median_family_income',
               "Median Home Value": 'median_home_value'}


# define median helper function
def calc_median(tract_df, range_df, attribute_name, median_to_calc, ids, year):
    # subset range df for current median variable to calc
    range_df = range_df[range_df['name'] == median_to_calc]
    if year == 2000 or 'income' in median_to_calc:
        range_min_col = 1
        range_max_col = 2
    else:
        l = range_df.iloc[0][2:].values

        range_min_col = range_df.iloc[0][2:].tolist().index(l[l <= year][-1]) + 1
        try:
            range_max_col = range_df.iloc[0][2:].tolist().index(l[l > year][0]) + 1
        except:
            range_max_col = range_df.iloc[0][2:].tolist().index(max(range_df.iloc[0][2:].tolist())) + 2

    if range_min_col == range_max_col:
        print("HUGEEEE ERRRORRRR")
    range_df = range_df.iloc[1:]
    range_df = range_df.rename(columns={str(range_min_col): 'range_start',
                                        str(range_max_col): 'range_end'}, inplace=False)
    # sort dataframe low to high by range start column
    range_df = range_df.sort_values(by=['range_start'])

    # remove nan rwos
    range_df = range_df[range_df['range_start'].notnull()]

    # range_df =  range_df[['name','id','range_start','range_end']]
    range_df['households'] = 0
    range_df['cumulative_total'] = 0

    # calculate households as sum of tract level households for each row based on range id
    if 'by_race' in median_dict[attribute_name.split(',')[0]]:
        ids.sort()
        range_df['id'] = ids
    # print(range_df['id'])

    range_df['households'] = range_df.apply(lambda row: tract_df[row['id']].sum(), axis=1)

    # calculate the cumulative total of households
    range_df['cumulative_total'] = range_df['households'].cumsum()

    # calculate total households and return 0 if total households is 0
    total_households = range_df['households'].sum()

    # if total households is 0 set median to 0
    if total_households == 0:
        return 0

    # calculate midpoint
    midpoint = total_households / 2

    # if midpoint is below first range return median as end of first range value
    if midpoint <= range_df['cumulative_total'].min():
        new_median = range_df['range_end'].min()
        return new_median

    # if midpoint is above last range set median to end of last range value
    if midpoint >= range_df['cumulative_total'].max():
        new_median = range_df['range_end'].max()
        return new_median

    less_midpoint_df = range_df[range_df['cumulative_total'] < midpoint]

    # get the single row containing the range just below the mid range by getting the row with the max range start from the subsetted median df
    range_below_mid_range_df = less_midpoint_df[
        less_midpoint_df['range_start'] == less_midpoint_df['range_start'].max()]

    # get the cumulative total value for the first row of the range below mid range dictionary
    total_hh_previous_range = range_below_mid_range_df['cumulative_total'].iloc[0]
    hh_to_mid_range = midpoint - total_hh_previous_range

    # extract rows above midrange by subsetting median df for rows with cumulative total grearter than midpoint.
    greater_midpoint_df = range_df[range_df['cumulative_total'] > midpoint]

    # get the single row containing the mid range by getting the row with the min range start from the subsetted median df
    mid_range_df = greater_midpoint_df[greater_midpoint_df['range_start'] == greater_midpoint_df['range_start'].min()]

    # get the households value for the first row of the mid range dictionary
    hh_in_mid_range = mid_range_df['households'].iloc[0]

    # calculate proportion of number of households in the mid range that would be needed to get to the mid-point
    prop_of_hh = hh_to_mid_range / hh_in_mid_range

    # calculate width of the mid range
    width = (mid_range_df['range_end'].iloc[0] - mid_range_df['range_start'].iloc[0]) + 1

    # apply proportion to width of mid range
    prop_to_width = prop_of_hh * width
    beginning_of_mid_range = mid_range_df['range_start'].iloc[0]

    # calculate new median
    new_median = beginning_of_mid_range + prop_to_width

    return new_median