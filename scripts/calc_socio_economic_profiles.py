# base libraries
import requests, json, os
import pandas as pd
import numpy as np
from collections import defaultdict

import warnings

from scripts.calc_fctns import calc_socio_economic_data

warnings.filterwarnings("ignore")

download_path = r'./downloads'
geo_lookup_df = pd.read_csv(r'./lookup_tables/geo_lookup_2000to2020.csv', dtype=str)

acs_race = {'A': 'White Alone', 'B': 'Black or African American Alone',
            'C': 'American Indian and Alaska Native Alone',
            'D': 'Asian Alone', 'E': 'Native Hawaiian and Other Pacific Islander Alone',
            'F': 'Some Other Race Alone', 'G': 'Two or More Races', 'H': 'White Alone, Not Hispanic or Latino',
            'I': 'Hispanic or Latino'}
sf3_race = {'A': 'White Alone', 'B': 'Black or African American Alone',
            'C': 'American Indian and Alaska Native Alone',
            'D': 'Asian Alone', 'E': 'Native Hawaiian and Other Pacific Islander Alone',
            'F': 'Some Other Race Alone', 'G': 'Two or More Races', 'H': 'Hispanic or Latino',
            'I': 'White Alone, Not Hispanic or Latino'}

geo_summary_variable = 'Neighborhood'

def calc_socio_economic_profiles(attribute_df, years, geo_lookup_df, output_path='./output'):
    '''
    base_ids_long = list(set(attribute_df['acs_base_id'].tolist() + attribute_df['sf3_base_id'].tolist()))
    base_ids_long = [x.split(',') for x in base_ids_long if str(x) != 'nan']
    base_ids_long = [item.strip() for sublist in base_ids_long for item in sublist]
    attribute_df_temp = attribute_df.copy()
    #RL HERE
    attribute_df_temp['acs_attribute_id'] = attribute_df_temp['acs_attribute_id'].apply(lambda x: [y.strip() for y in x.split(',')] if len(x.split(',')) > 1)
    attribute_df_temp['sf3_attribute_id'] = attribute_df_temp['sf3_attribute_id'].apply(lambda x: [x])

    attribute_df = attribute_df_temp.explode('acs_attribute_id').explode('sf3_attribute_id')
    attribute_df_base_dict = dict(zip(attribute_df[attribute_df['acs_attribute_id'].isin(base_ids_long)]['acs_attribute_id'], \
                                      attribute_df[attribute_df['acs_attribute_id'].isin(base_ids_long)]['attribute_name']))
    attribute_df_base_dict_v2 = dict(zip(attribute_df[attribute_df['sf3_attribute_id'].isin(base_ids_long)]['sf3_attribute_id'], \
                                      attribute_df[attribute_df['sf3_attribute_id'].isin(base_ids_long)]['attribute_name']))
    attribute_df_base_dict = attribute_df_base_dict | attribute_df_base_dict_v2
    '''

    for year in years:

        if year <= 2009:
            geo_year = '2000'
            survey = 'dec'
            table_name = 'sf3'
            label = 'DEC_SF3'
            ext = ''
        elif year >= 2010 and year <= 2019:
            geo_year = '2010'
            survey = 'acs'
            table_name = 'acs'
            label = 'ACS5YR'
            ext = 'E'
        elif year >= 2020:
            geo_year = '2020'
            survey = 'acs'
            table_name = 'acs'
            label = 'ACS5YR'
            ext = 'E'

        dict_race = {}
        exec ('dict_race = %s_race' % table_name)

        # import median tables from median_ranges csv and add empty columns for rows 'households and 'cumulative_totals'
        range_df = pd.read_csv(r'./lookup_tables/%s_median_ranges.csv' % table_name)

        print(table_name, year)
        df = pd.read_csv(r'./census_raw/%s%sdf.csv' % (table_name, year))
        for i in df['tract'].index:
            j = str(df.loc[i, 'tract'])
            j = '0' + j
            while len(j) < 6:
                j = j + '0'
            df.loc[i, 'tract'] = j

        # import geo_lookup csv
        geo_lookup_df_yyyy = geo_lookup_df[geo_lookup_df['year'] == geo_year]
        neighborhoods = list(set(geo_lookup_df_yyyy.neighborhood.tolist()))
        neighborhoods.sort()
        neighborhoods.remove('San Francisco')
        # print(geo_lookup_df_yyyy)
        tract_nb_lookup = defaultdict(list)
        all_tracts = list(set(df['tract'].tolist()))

        # create tract lookup dictionary for neighborhoods
        for i, j in zip(geo_lookup_df_yyyy['neighborhood'], geo_lookup_df_yyyy['tractid']):
            if len(j) == 5:
                tract_nb_lookup[i].append('0' + j)
            else:
                tract_nb_lookup[i].append(j)

        # tract_nb_lookup["sf"]= all_tracts
        # create tract lookup dictionary for supervisor districts
        first_4 = list(tract_nb_lookup.items())
        # first_4

        geo_summary_variable = 'neighborhood'

        tract_lookup = tract_nb_lookup
        # print(tract_lookup)

        ## Calculate Socioeconomic Profiles

        all_calc_data = defaultdict(dict)
        all_calc_data_by_tract = defaultdict(dict)
        attribute_names = []

        for j in attribute_df.index:
            # print(j)
            attribute_name = attribute_df.loc[j, 'attribute_name']

            attribute_id = [attribute_df.loc[j, '%s_attribute_id' % table_name]]

            print(attribute_name, attribute_id)
            if str(attribute_id) == "[nan]" or str(attribute_id) == "[None]":
                continue

            base_id = [attribute_df.loc[j, '%s_base_id' % table_name]]

            race = attribute_df.loc[j, '%s_race' % table_name]
            treatment = attribute_df.loc[j, '%s_treatment' % table_name]

            attribute_ids = [x.strip().split(", ") for x in attribute_id][0]
            attribute_ids = list(set([x + ext for x in attribute_ids]))

            try:
                base_ids = [x.strip().split(", ") for x in base_id][0]
                base_ids = list(set([x + ext for x in base_ids]))
            except:
                base_ids = None

            if str(race) == 'nan':
                race = None
            # print(attribute_name, attribute_id, race, base_ids, attribute_ids, treatment)

            if race is not None:
                if 'CT' in attribute_ids[0] or attribute_ids[0].startswith('B') or attribute_ids[0].startswith('C'):
                    group_length = 6
                else:
                    group_length = 4

                for r in dict_race.keys():
                    # print(r)
                    attribute_name_by_r = attribute_name + ', ' + dict_race[r]

                    attribute_ids_by_r = list(
                        set([x[:group_length] + l + x[group_length:] for l in r for x in attribute_ids]))

                    if base_ids is not None:
                        base_ids_by_r = list(
                            set([x[:group_length] + l + x[group_length:] for l in r for x in base_ids]))
                    else:
                        base_ids_by_r = None

                    # print(attribute_name_by_r, attribute_ids_by_r, base_ids_by_r, treatment)
                    attribute_names.append(attribute_name_by_r)
                    try:
                        # print(attribute_name_by_r, attribute_ids_by_r, base_ids_by_r, treatment, year)
                        all_calc_data, all_calc_data_by_tract = calc_socio_economic_data(df, tract_lookup,
                                                                                         all_calc_data,
                                                                                         all_calc_data_by_tract,
                                                                                         attribute_name_by_r,
                                                                                         attribute_ids_by_r,
                                                                                         base_ids_by_r, treatment, year,
                                                                                            all_tracts, range_df
                                                                                         )

                    except Exception as e:
                        print(e)
                        print(attribute_name, attribute_ids, base_ids)

            elif treatment == 'loop':
                idx = 0
                for r in dict_race.keys():

                    if r == 'H' or r == 'I':
                        print('skip')
                    else:
                        # print(r)
                        attribute_name_by_r = attribute_name + ', ' + dict_race[r]

                        attribute_ids_by_r = [attribute_ids[
                                                  idx]]  # list(set([x[:group_length] + l + x[group_length:] for l in r for x in attribute_ids]))
                        idx += 1
                        if base_ids is not None:
                            base_ids_by_r = base_ids  # list(set([x[:group_length] + l + x[group_length:] for l in r for x in base_ids]))
                        else:
                            base_ids_by_r = None

                        # print(attribute_name_by_r, attribute_ids_by_r, base_ids_by_r, treatment)
                        attribute_names.append(attribute_name_by_r)
                        treatment = 'as is'
                        try:
                            all_calc_data, all_calc_data_by_tract = calc_socio_economic_data(df, tract_lookup,
                                                                                             all_calc_data,
                                                                                             all_calc_data_by_tract,
                                                                                             attribute_name_by_r,
                                                                                             attribute_ids_by_r,
                                                                                             base_ids_by_r, treatment,
                                                                                             year, all_tracts, range_df)
                        except Exception as e:
                            print(e)
                            print(attribute_name, attribute_ids, base_ids)


            else:
                attribute_names.append(attribute_name)
                # print(attribute_name, attribute_ids, base_ids)
                try:
                    all_calc_data, all_calc_data_by_tract = calc_socio_economic_data(df, tract_lookup, \
                                                                                     all_calc_data,
                                                                                     all_calc_data_by_tract,
                                                                                     attribute_name, \
                                                                                     attribute_ids, base_ids, treatment,
                                                                                     year, all_tracts, range_df)
                except Exception as e:
                    print(e)
                    print(attribute_name, attribute_ids, base_ids)


        # code segment to account for alternates
        # def remove_alternate_text(x):
        #    return x.replace(', alternate','')

        cat_dict = dict(zip(attribute_df.attribute_name, attribute_df.category_dag))
        # print(df_all_calcs['Attribute'])

        df_all_calcs = pd.DataFrame.from_dict(all_calc_data).reset_index()
        df_all_calcs.rename(columns={'index': 'Attribute'}, inplace=True)

        # Alternates:
        print(df_all_calcs.Attribute)
        # df_all_calcs['Attribute'] = df_all_calcs['Attribute'].apply(lambda x: remove_alternate_text(x))
        print(df_all_calcs)
        # df_all_calcs = df_all_calcs.fillna(0)
        # zero_sum_attributes = df_all_calcs[df_all_calcs.sum(axis=1) == 0].index
        # df_all_calcs.loc[zero_sum_attributes,neighborhoods] = np.nan
        # df_all_calcs.loc[zero_sum_attributes,'San Francisco'] = np.nan

        # Sort to prioritize rows with non-null 'Value'
        df_all_calcs = df_all_calcs.sort_values(by='San Francisco', na_position='last')

        # Drop duplicate attributes, keeping the first occurrence (non-null prioritized)
        print(df_all_calcs)
        df_all_calcs = df_all_calcs.drop_duplicates(subset='Attribute', keep='first')

        # Reset index if needed
        df_all_calcs = df_all_calcs.reset_index(drop=True)

        df_all_calcs['Category'] = df_all_calcs['Attribute'].map(cat_dict)
        temp = df_all_calcs[df_all_calcs['Category'].isnull()]

        if len(temp['Attribute'].str.split(', ', n=1, expand=True)):
            temp['Race delimiter'] = None
            temp[['Attribute 2', 'Race delimiter 2']] = temp['Attribute'].str.split(', ', n=1, expand=True)
            temp[['Attribute', 'Race delimiter']] = temp['Attribute'].str.split(' by', n=1, expand=True)
            df_all_calcs['Category'] = df_all_calcs['Category'].fillna(temp['Attribute'].map(cat_dict))

        column_order = ['Category', 'Attribute', 'San Francisco'] + neighborhoods
        df_all_calcs = df_all_calcs[column_order]

        df_all_calcs_by_tract = pd.DataFrame.from_dict(all_calc_data_by_tract).reset_index()
        df_all_calcs_by_tract.rename(columns={'index': 'Attribute'}, inplace=True)
        # df_all_calcs_by_tract['Attribute'] = df_all_calcs_by_tract['Attribute'].apply(lambda x: remove_alternate_text(x))

        df_all_calcs_by_tract['Category'] = df_all_calcs_by_tract['Attribute'].map(cat_dict)

        temp = df_all_calcs_by_tract[df_all_calcs_by_tract['Category'].isnull()]
        if len(temp['Attribute'].str.split(', ', n=1, expand=True)):
            temp['Race delimiter'] = None
            temp[['Attribute 2', 'Race delimiter 2']] = temp['Attribute'].str.split(', ', n=1, expand=True)
            temp[['Attribute', 'Race delimiter']] = temp['Attribute'].str.split(' by', n=1, expand=True)
            df_all_calcs_by_tract['Category'] = df_all_calcs_by_tract['Category'].fillna(
                temp['Attribute'].map(cat_dict))

        df_numerics_only = df_all_calcs_by_tract.select_dtypes(include=np.number)

        # Sort to prioritize rows with non-null 'Value'
        # zero_sum_attributes = df_all_calcs_by_tract[df_all_calcs_by_tract.sum(axis=1) == 0].index
        # df_all_calcs_by_tract.loc[zero_sum_attributes,df_numerics_only.columns] = np.nan

        try:
            df_all_calcs_by_tract = df_all_calcs_by_tract.sort_values(by='010100', na_position='last')
        except:
            df_all_calcs_by_tract = df_all_calcs_by_tract.sort_values(by='030800', na_position='last')

        # Drop duplicate attributes, keeping the first occurrence (non-null prioritized)
        df_all_calcs_by_tract = df_all_calcs_by_tract.drop_duplicates(subset='Attribute', keep='first')

        # Reset index if needed
        df_all_calcs_by_tract = df_all_calcs_by_tract.reset_index(drop=True)

        df_numerics_only = df_all_calcs_by_tract.select_dtypes(include=np.number)

        df_cat_columns = df_all_calcs_by_tract.select_dtypes(include=object)
        df_cat_columns = df_cat_columns[['Category', 'Attribute']]
        df_all_calcs_by_tract = pd.concat([df_cat_columns, df_numerics_only], axis=1)

        df_all_calcs = df_all_calcs.sort_values(by=['Category', 'Attribute'], ascending=[True, True], inplace=False)

        df_all_calcs.to_csv(os.path.join(download_path,
                                         'Neighborhood' + '_' + 'profiles_by_attribute_' + label + '_{}.csv'.format(
                                             year)), index=False)

        # transpose dataset for second geo view of dataset
        df_all_calcs_tp = df_all_calcs.T.reset_index()
        df_all_calcs_tp.columns = df_all_calcs_tp.iloc[0]
        df_all_calcs_tp = df_all_calcs_tp[1:].rename(columns={'Category': geo_summary_variable})
        df_all_calcs_tp.to_csv(
            os.path.join(download_path, 'Neighborhood' + '_' + 'profiles_by_geo_' + label + '_{}.csv'.format(year)),
            index=False)

        ####################################
        df_all_calcs_by_tract = df_all_calcs_by_tract.sort_values(by=['Category', 'Attribute'], ascending=[True, True],
                                                                  inplace=False)
        df_all_calcs_by_tract.to_csv(
            os.path.join(download_path, 'Tract' + '_' + 'profiles_by_attribute_' + label + '_{}.csv'.format(year)),
            index=False)

        # transpose dataset for second geo view of dataset
        df_all_calcs_tp = df_all_calcs_by_tract.T.reset_index()
        df_all_calcs_tp.columns = df_all_calcs_tp.iloc[0]
        df_all_calcs_tp = df_all_calcs_tp[1:].rename(columns={'Category': "tract"})
        df_all_calcs_tp = df_all_calcs_tp.sort_values(by=["tract"])
        df_all_calcs_tp.to_csv(
            os.path.join(download_path, 'Tract' + '_' + 'profiles_by_geo_' + label + '_{}.csv'.format(year)),
            index=False)