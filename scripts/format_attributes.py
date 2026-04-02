# In[]:
# base libraries
import requests, json, os
import pandas as pd
import numpy as np
from collections import defaultdict

import warnings
warnings.filterwarnings("ignore")


def format_attributes(attribute_df):

    attribute_df = attribute_df.fillna(np.nan).replace([np.nan], [None])
    #attribute_df = attribute_df[attribute_df['attribute_name'].str.contains('Mortgage')]

    acs_attributes = attribute_df['acs_attribute_id'].tolist() + attribute_df[attribute_df['acs_base_id'].notnull()]['acs_base_id'].tolist()
    sf3_attributes = attribute_df[attribute_df['sf3_attribute_id'].notnull()]['sf3_attribute_id'].tolist() + attribute_df[attribute_df['sf3_base_id'].notnull()]['sf3_base_id'].tolist()

    acs_attributes = [a for a in acs_attributes if str(a) != 'None']
    sf3_attributes = [a for a in sf3_attributes if str(a) != 'None']

    # In[]:
    acs_group_length = 6

    acs_attribute_ids = []
    acs_group_ids = []
    acs_attribute_names = []

    temp_df_main = attribute_df[attribute_df['acs_attribute_id'].notnull()]
    temp_df_base = attribute_df[attribute_df['acs_base_id'].notnull()]

    # print(attribute_ids_extracted)
    ls = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    for attribute_id in acs_attributes:
        # print(attribute_id)
        if len(attribute_id) > acs_group_length:

            acs_attribute_ids.extend(attribute_id.split(", "))

            if temp_df_main[temp_df_main['acs_attribute_id'].str.contains(attribute_id)]['acs_race'].any() or \
                    temp_df_base[temp_df_base['acs_base_id'].str.contains(attribute_id)]['acs_race'].any():
                rs = attribute_id.split(", ")
                acs_attribute_ids.extend(
                    list(set([x[:acs_group_length] + l + x[acs_group_length:] for l in ls for x in rs])))

        elif len(attribute_id) <= acs_group_length:
            acs_group_ids.append(attribute_id)
            if temp_df_main[temp_df_main['acs_attribute_id'].str.contains(attribute_id)]['acs_race'].any() or \
                    temp_df_base[temp_df_base['acs_base_id'].str.contains(attribute_id)]['acs_race'].any():
                rs = attribute_id.split(", ")
                acs_group_ids.extend(
                    list(set([x[:acs_group_length] + l + x[acs_group_length:] for l in ls for x in rs])))

    acs_attribute_ids = list(set([x + "E" for x in acs_attribute_ids]))
    acs_attribute_ids = acs_attribute_ids + acs_group_ids

    acs_attribute_ids.sort()
    acs_attribute_ids = [x.strip() for x in acs_attribute_ids]

    # acs_attribute_ids

    temp_df = attribute_df[attribute_df['sf3_attribute_id'].notnull()]
    temp_df_base = attribute_df[attribute_df['sf3_base_id'].notnull()]
    sf3_attribute_ids = []
    sf3_group_ids = []
    # print(attribute_ids_extracted)
    ls = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    for attribute_id in sf3_attributes:

        if 'CT' in attribute_id:
            sf3_group_length = 6
        else:
            sf3_group_length = 4

        if len(attribute_id) > sf3_group_length:
            sf3_attribute_ids.extend(attribute_id.split(", "))

            if temp_df[temp_df['sf3_attribute_id'].str.contains(attribute_id)]['sf3_race'].any() or \
                    temp_df_base[temp_df_base['sf3_base_id'].str.contains(attribute_id)]['sf3_race'].any():
                rs = attribute_id.split(", ")
                sf3_attribute_ids.extend(
                    list(set([x[:sf3_group_length] + l + x[sf3_group_length:] for l in ls for x in rs])))

        elif len(attribute_id) <= sf3_group_length:
            sf3_group_ids.append(attribute_id)
            if temp_df[temp_df['sf3_attribute_id'].str.contains(attribute_id)]['sf3_race'].any() or \
                    temp_df_base[temp_df_base['sf3_base_id'].str.contains(attribute_id)]['sf3_race'].any():
                rs = attribute_id.split(", ")
                sf3_group_ids.extend(
                    list(set([x[:sf3_group_length] + l + x[sf3_group_length:] for l in ls for x in rs])))

    sf3_attribute_ids = sf3_attribute_ids + sf3_group_ids

    sf3_attribute_ids.sort()
    sf3_attribute_ids = [x.strip() for x in sf3_attribute_ids]

    # sf3_attribute_ids

    acs_attribute_ids = list(set(acs_attribute_ids))
    sf3_attribute_ids = list(set(sf3_attribute_ids))


    return acs_attribute_ids, sf3_attribute_ids