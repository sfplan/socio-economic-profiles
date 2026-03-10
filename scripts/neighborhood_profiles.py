# base libraries
import requests, json, os
import pandas as pd
import numpy as np
from collections import defaultdict

import warnings
warnings.filterwarnings("ignore")

years = [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2000]
warnings.filterwarnings("ignore")
output_path = r'./output'
geo_lookup_df = pd.read_csv(r'./lookup_tables/geo_lookup_2000to2020.csv', dtype=str)

def neighborhood_profiles(years, geo_lookup_df, output_path='./output'):
    # In[]: Generate neighborhood profiles
    import pandas as pd

    import os
    import warnings

    geo_lookup_df_yyyy = geo_lookup_df[geo_lookup_df['year'] == '2020']
    neighborhoods = list(set(geo_lookup_df_yyyy.neighborhood.tolist()))
    neighborhoods.sort() 

    for n in neighborhoods:

        year_columns = []

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

            df_all_calcs = pd.read_csv(os.path.join(output_path,
                                                    'neighborhood' + '_' + 'profiles_by_attribute_' + label + '_{}.csv'.format(
                                                        year)))

            try:

                if year == max(years):

                    df_all_calcs_full = df_all_calcs[['Category', 'Attribute', n]]
                    df_all_calcs_full.rename(columns={n: str(year) + '_' + n}, inplace=True)

                    # CALCULATE AFFORDABILITY
                    ami_breaks = [30, 50, 80, 100]
                    df_all_calcs_full_aff = pd.DataFrame(columns=df_all_calcs_full.columns,
                                                         index=range(12))
                    df_all_calcs_full_aff['Category'] = 'Affordability'

                    c = 0
                    for i in ami_breaks:
                        df_all_calcs_full_aff.loc[c, 'Attribute'] = '%s AMI Annual Income' % i
                        df_all_calcs_full_aff.loc[c + 1, 'Attribute'] = '%s AMI Monthly Affordable Rent' % i
                        df_all_calcs_full_aff.loc[
                            c + 2, 'Attribute'] = '# Units at or below %s AMI Monthly Affordable Rent' % i
                        c += 3

                    rent_levels = df_all_calcs_full[(df_all_calcs_full.Attribute.str.contains("Rent")) & \
                                                    ((df_all_calcs_full.Attribute.str.contains(" to ")) |
                                                     (df_all_calcs_full.Attribute.str.contains(" or ")))].to_dict(
                        'records')
                    max_dict = {}
                    for j in rent_levels:
                        level_j = j
                        key_j = j['Attribute']
                        key_j_split = key_j.split(' ')
                        try:
                            max_dict[key_j] = int(key_j_split[3])
                        except:
                            max_dict[key_j] = 1e6

                    l = list(max_dict.values())

                else:
                    df_all_calcs = df_all_calcs[['Attribute', n]]
                    df_all_calcs.rename(columns={n: str(year) + '_' + n}, inplace=True)
                    df_all_calcs_full = df_all_calcs_full.merge(df_all_calcs, how='left', on='Attribute')

                year_columns.append(year)

            except Exception as e:
                print(n, year, e)

            try:
                median_income = float(df_all_calcs_full[df_all_calcs_full.Attribute.isin([
                    "Median Household Income"
                ])].to_dict('records')[0]['%s' % (str(year) + '_' + n)])

                income_breaks = [(i / 100) * median_income for i in ami_breaks]
                breaks_dict = dict(zip(ami_breaks, income_breaks))

                # print(breaks_dict, income_breaks)
                # Affordable limits for each AMI tier:
                c = 0

                for i in ami_breaks:
                    df_all_calcs_full_aff.loc[c, '%s' % (str(year) + '_' + n)] = breaks_dict[i]
                    df_all_calcs_full_aff.loc[c + 1, '%s' % (str(year) + '_' + n)] = breaks_dict[i] / 12

                    aff_rent = breaks_dict[i] / 12

                    m = [x for x in l if x <= aff_rent]
                    counter = [key for key, value in max_dict.items() if value in m]
                    counter = int(df_all_calcs_full[df_all_calcs_full.Attribute.isin(counter)][
                                      '%s' % (str(year) + '_' + n)].sum())

                    df_all_calcs_full_aff.loc[c + 2, '%s' % (str(year) + '_' + n)] = counter

                    c += 3

            except Exception as e:
                print(e)

        df_all_calcs_full = pd.concat([df_all_calcs_full, df_all_calcs_full_aff], axis=0)

        year_columns.sort()
        columns_plus = [str(x) + '_' + n for x in year_columns]

        # drop na rows
        df_all_calcs_full = df_all_calcs_full.dropna(subset=columns_plus, inplace=False)

        columns_plus.insert(0, 'Attribute')
        columns_plus.insert(0, 'Category')

        df_all_calcs_full = df_all_calcs_full[columns_plus]

        alternates = df_all_calcs_full[df_all_calcs_full['Attribute'].str.contains('alternate')]['Attribute'].tolist()
        # print(alternates)

        if len(alternates) > 0:
            alternates_labels = [x[:-11] for x in alternates]
            for a in alternates_labels:
                df_rows = df_all_calcs_full[df_all_calcs_full['Attribute'].str.startswith(a)]
                df_rows = df_rows.iloc[0].combine_first(df_rows.iloc[1])
                df_all_calcs_full = df_all_calcs_full[(df_all_calcs_full['Attribute'].str.startswith(a)) == False]
                df_all_calcs_full = pd.concat([df_all_calcs_full, df_rows.to_frame().T], axis=0).reset_index(drop=True)

        df_all_calcs_full = df_all_calcs_full.sort_values(by=['Category', 'Attribute'], ascending=[True, True],
                                                          inplace=False)

        n = n.strip().replace('/', '-')
        df_all_calcs_full.to_excel(r'./output/%s_neighborhood_profiles_by_attribute_2000to2023.xlsx' % n, index=False,
                                   sheet_name='census_attributes')
        df_all_calcs_full.to_csv(r'./output/%s_neighborhood_profiles_by_attribute_2000to2023.csv' % n, index=False,
                                 sheet_name='census_attributes')


    def neighborhood_profiles_vs_citywide(years, geo_lookup_df, output_path='./output'):

        geo_lookup_df_yyyy = geo_lookup_df[geo_lookup_df['year'] == '2020']
        neighborhoods = list(set(geo_lookup_df_yyyy.neighborhood.tolist()))
        neighborhoods.sort()

        for n in neighborhoods:

            year_columns = []

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

                df_all_calcs = pd.read_csv(os.path.join(output_path,
                                                        'neighborhood' + '_' + 'profiles_by_attribute_' + label + '_{}.csv'.format(
                                                            year)))
                df_all_calcs_sf = pd.read_csv(os.path.join(output_path,
                                                           'neighborhood' + '_' + 'profiles_by_attribute_' + label + '_{}.csv'.format(
                                                               year)))

                try:

                    if year == 2023:

                        df_all_calcs_full = df_all_calcs[['Category', 'Attribute', n]]
                        df_all_calcs_full.rename(columns={n: str(year) + '_' + n}, inplace=True)

                        # CALCULATE AFFORDABILITY
                        ami_breaks = [30, 50, 80, 100]
                        df_all_calcs_full_aff = pd.DataFrame(columns=df_all_calcs_full.columns, index=range(12))
                        df_all_calcs_full_aff['Category'] = 'Affordability'

                        c = 0
                        for i in ami_breaks:
                            df_all_calcs_full_aff.loc[c, 'Attribute'] = '%s AMI Annual Income' % i
                            df_all_calcs_full_aff.loc[c + 1, 'Attribute'] = '%s AMI Monthly Affordable Rent' % i
                            df_all_calcs_full_aff.loc[
                                c + 2, 'Attribute'] = '# Units at or below %s AMI Monthly Affordable Rent' % i
                            c += 3

                        rent_levels = df_all_calcs_full[(df_all_calcs_full.Attribute.str.contains("Rent")) & 
                                                        ((df_all_calcs_full.Attribute.str.contains(" to ")) |
                                                         (df_all_calcs_full.Attribute.str.contains(" or ")))].to_dict(
                            'records')
                        max_dict = {}
                        for j in rent_levels:
                            level_j = j
                            key_j = j['Attribute']
                            key_j_split = key_j.split(' ')
                            try:
                                max_dict[key_j] = int(key_j_split[3])
                            except:
                                max_dict[key_j] = 1e6

                        l = list(max_dict.values())

                        df_all_calcs_full_sf = df_all_calcs_sf[['Category', 'Attribute', 'San Francisco']]
                        df_all_calcs_full_sf.rename(columns={'San Francisco': str(year) + '_' + 'San Francisco'},
                                                    inplace=True)

                        # CALCULATE AFFORDABILITY
                        ami_breaks = [30, 50, 80, 100]
                        df_all_calcs_full_sf_aff = pd.DataFrame(columns=df_all_calcs_full_sf.columns, 
                                                                index=range(12))
                        df_all_calcs_full_sf_aff['Category'] = 'Affordability'

                        c = 0
                        for i in ami_breaks:
                            df_all_calcs_full_sf_aff.loc[c, 'Attribute'] = '%s AMI Annual Income' % i
                            df_all_calcs_full_sf_aff.loc[c + 1, 'Attribute'] = '%s AMI Monthly Affordable Rent' % i
                            df_all_calcs_full_sf_aff.loc[
                                c + 2, 'Attribute'] = '# Units at or below %s AMI Monthly Affordable Rent' % i
                            c += 3

                        rent_levels = df_all_calcs_full_sf[(df_all_calcs_full_sf.Attribute.str.contains("Rent")) &
                                                           ((df_all_calcs_full_sf.Attribute.str.contains(" to ")) | 
                                                            (df_all_calcs_full_sf.Attribute.str.contains(" or ")))].to_dict(
                            'records')
                        max_dict = {}
                        for j in rent_levels:
                            level_j = j
                            key_j = j['Attribute']
                            key_j_split = key_j.split(' ')
                            try:
                                max_dict[key_j] = int(key_j_split[3])
                            except:
                                max_dict[key_j] = 1e6

                        l = list(max_dict.values())

                    else:
                        df_all_calcs = df_all_calcs[['Attribute', n]]
                        df_all_calcs.rename(columns={n: str(year) + '_' + n}, inplace=True)
                        df_all_calcs_full = df_all_calcs_full.merge(df_all_calcs, how='left', on='Attribute')

                        df_all_calcs_sf = df_all_calcs_sf[['Attribute', 'San Francisco']]
                        df_all_calcs_sf.rename(columns={'San Francisco': str(year) + '_' + 'San Francisco'}, inplace=True)
                        df_all_calcs_full_sf = df_all_calcs_full_sf.merge(df_all_calcs_sf, how='left', on='Attribute')

                    year_columns.append(year)

                except Exception as e:
                    print(n, year, e)

                try:
                    median_income = float(df_all_calcs_full[df_all_calcs_full.Attribute.isin([
                        "Median Household Income"
                    ])].to_dict('records')[0]['%s' % (str(year) + '_' + n)])

                    income_breaks = [(i / 100) * median_income for i in ami_breaks]
                    breaks_dict = dict(zip(ami_breaks, income_breaks))

                    # print(breaks_dict, income_breaks)
                    # Affordable limits for each AMI tier:
                    c = 0
                    for i in ami_breaks:
                        df_all_calcs_full_aff.loc[c, '%s' % (str(year) + '_' + n)] = breaks_dict[i]
                        df_all_calcs_full_aff.loc[c + 1, '%s' % (str(year) + '_' + n)] = breaks_dict[i] / 12

                        aff_rent = breaks_dict[i] / 12

                        m = [x for x in l if x <= aff_rent]
                        counter = [key for key, value in max_dict.items() if value in m]
                        counter = int(df_all_calcs_full[df_all_calcs_full.Attribute.isin(counter)][
                                          '%s' % (str(year) + '_' + n)].sum())

                        df_all_calcs_full_aff.loc[c + 2, '%s' % (str(year) + '_' + n)] = counter

                        c += 3
                except Exception as e:

                    print('aff %s, %s' % (n, e))

                try:

                    median_income = float(df_all_calcs_full_sf[df_all_calcs_full_sf.Attribute.isin([
                        "Median Household Income"
                    ])].to_dict('records')[0]['%s' % (str(year) + '_' + 'San Francisco')])

                    income_breaks = [(i / 100) * median_income for i in ami_breaks]
                    breaks_dict = dict(zip(ami_breaks, income_breaks))

                    # print(breaks_dict, income_breaks)
                    # Affordable limits for each AMI tier:
                    c = 0
                    for i in ami_breaks:
                        df_all_calcs_full_sf_aff.loc[c, '%s' % (str(year) + '_' + 'San Francisco')] = breaks_dict[i]
                        df_all_calcs_full_sf_aff.loc[c + 1, '%s' % (str(year) + '_' + 'San Francisco')] = breaks_dict[
                                                                                                              i] / 12

                        aff_rent = breaks_dict[i] / 12

                        m = [x for x in l if x <= aff_rent]
                        counter = [key for key, value in max_dict.items() if value in m]
                        counter = int(df_all_calcs_full_sf[df_all_calcs_full_sf.Attribute.isin(counter)][
                                          '%s' % (str(year) + '_' + 'San Francisco')].sum())

                        df_all_calcs_full_sf_aff.loc[c + 2, '%s' % (str(year) + '_' + 'San Francisco')] = counter
                        # print(df_all_calcs_full_sf_aff.loc[c:c+2])
                        c += 3

                except Exception as e:

                    print('aff sf, %s' % (e))

            df_all_calcs_full = pd.concat([df_all_calcs_full, df_all_calcs_full_aff], axis=0)
            df_all_calcs_full_sf = pd.concat([df_all_calcs_full_sf, df_all_calcs_full_sf_aff], axis=0)

            year_columns.sort()
            columns_plus = [str(x) + '_' + n for x in year_columns]
            columns_plus_sf = [str(x) + '_' + 'San Francisco' for x in year_columns]

            # drop na rows
            df_all_calcs_full = df_all_calcs_full.dropna(subset=columns_plus, inplace=False)
            df_all_calcs_full_sf = df_all_calcs_full_sf.dropna(subset=columns_plus_sf, inplace=False)

            columns_plus.insert(0, 'Attribute')
            columns_plus.insert(0, 'Category')
            columns_plus_sf.insert(0, 'Attribute')
            columns_plus_sf.insert(0, 'Category')

            df_all_calcs_full = df_all_calcs_full[columns_plus]
            df_all_calcs_full_sf = df_all_calcs_full_sf[columns_plus_sf]

            alternates = df_all_calcs_full[df_all_calcs_full['Attribute'].str.contains('alternate')]['Attribute'].tolist()
            if len(alternates) > 0:
                alternates_labels = [x[:-11] for x in alternates]
                for a in alternates_labels:
                    df_rows = df_all_calcs_full[df_all_calcs_full['Attribute'].str.startswith(a)]
                    df_rows = df_rows.iloc[0].combine_first(df_rows.iloc[1])
                    df_all_calcs_full = df_all_calcs_full[(df_all_calcs_full['Attribute'].str.startswith(a)) == False]
                    df_all_calcs_full = pd.concat([df_all_calcs_full, df_rows.to_frame().T], axis=0).reset_index(drop=True)

            df_all_calcs_full = df_all_calcs_full.sort_values(by=['Category', 'Attribute'], ascending=[True, True],
                                                              inplace=False)

            # SF
            alternates = df_all_calcs_full_sf[df_all_calcs_full_sf['Attribute'].str.contains('alternate')][
                'Attribute'].tolist()
            if len(alternates) > 0:
                alternates_labels = [x[:-11] for x in alternates]
                for a in alternates_labels:
                    df_rows = df_all_calcs_full_sf[df_all_calcs_full_sf['Attribute'].str.startswith(a)]
                    df_rows = df_rows.iloc[0].combine_first(df_rows.iloc[1])
                    df_all_calcs_full_sf = df_all_calcs_full_sf[
                        (df_all_calcs_full_sf['Attribute'].str.startswith(a)) == False]
                    df_all_calcs_full_sf = pd.concat([df_all_calcs_full_sf, df_rows.to_frame().T], axis=0).reset_index(
                        drop=True)

            df_all_calcs_full_sf = df_all_calcs_full_sf.sort_values(by=['Category', 'Attribute'], ascending=[True, True],
                                                                    inplace=False)

            year_columns = [2000, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
            comparative_columns = [[str(x) + '_' + n, str(x) + '_' + 'San Francisco'] for x in year_columns]
            comparative_columns = [x for xs in comparative_columns for x in xs]
            comparative_columns.insert(0, 'Attribute')
            comparative_columns.insert(0, 'Category')

            df_comparative = pd.merge(df_all_calcs_full, df_all_calcs_full_sf, on='Attribute', how='left')
            df_comparative = df_comparative.rename(columns={'Category_x': 'Category'})

            try:
                df_comparative = df_comparative[comparative_columns]
            except Exception as e:
                df_comparative = df_comparative

            n = n.strip().replace('/', '-')
            df_comparative.to_excel(r'%s%s_neighborhood_v_sf_by_attribute_2000to2023.xlsx' %(output_path, n), index=False,
                                    sheet_name='census_attributes')
            df_comparative.to_csv(r'%s%s_neighborhood_v_sf_by_attribute_2000to2023.csv' %(output_path, n), index=False,
                                  sheet_name='census_attributes')