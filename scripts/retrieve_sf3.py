from scripts.build_census_api import make_census_api_call, build_census_url
import pandas as pd
import numpy as np
def retrieve_sf3(attribute_ids, key):
    # set geo variables for api call
    state_code = "06"
    county_code = "075"
    tract_code = "*"
    level = 'tract'
    # split attributes into groups of 45, run a census query for each, merge outputs into a single df
    df = pd.DataFrame({'ID': attribute_ids})
    df['Key'] = df['ID'].str[:6]
    split_attribute_ids = df.groupby('Key')['ID'].apply(list).tolist()
    split_attribute_ids = [item for sublist in split_attribute_ids for item in sublist]

    # split_attribute_ids = [sf3_attribute_ids[i:i+45] for i in range(0, len(sf3_attribute_ids), 45)]
    # print(split_attribute_ids)
    df = None
    first = True
    num = 0
    year = 2000
    sf3_df_temp = pd.read_csv(r'./census_raw/sf32000df.csv')

    for ids in split_attribute_ids:
        # print(ids)
        if ids in sf3_df_temp.columns:
            continue
        ids = [ids]
        census_url = build_census_url(year, 'dec', 'sf3', county_code, state_code, tract_code, level, ids, key)
        # print(census_url)
        try:

            returned_df = make_census_api_call(census_url)
            num += 1
            if first:
                df = returned_df
                first = False

            else:
                returned_df = returned_df.drop(columns=['state'])
                df = pd.merge(df, returned_df, on=level, how='left', suffixes=(f'_x{num}', f'_y{num}'))

        except Exception as e:
            print(e)

    try:
        df = df.loc[:, ~df.columns.str.contains('^county')]
    except:
        pass

    df_numerics_only = df.select_dtypes(include=np.number)
    df_numerics_only
    df_numerics_only[df_numerics_only < 0] = None

    sf32000df = pd.concat([df.select_dtypes(include=object), df_numerics_only], axis=1)

    sf3_df_temp.drop(columns=['state', 'tract'], inplace=True)
    sf32000df_full = pd.concat([sf3_df_temp, sf32000df], axis=1)

    sf32000df_full.to_csv(r'./census_raw/sf32000df.csv')