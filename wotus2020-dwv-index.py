#!/usr/bin/python

import pandas as pd
import os
import time
from datetime import datetime
from math import ceil as ceil

pws=pd.read_csv('data/pws.csv')

# keep PWS with active water systems data (Surce: New Mexico Drinking Water Bureau)
data=pws[pws["has_nmdwb_data"]=='Yes']

# Compute the PWS's WOTUS water index
data['wotus2020_dwv_index']=-1

# If the PWS is a GW PWS then we assume that they don't have any surface water intakes and hence the vulnerability impact is 1
data.loc[data['d_fed_prim'].isin(['GW','GWP']),'wotus2020_dwv_index']=1

# 	Any SW or GU Water intake impacted? (if none then index=1)
data.loc[data['ratio_impacted_gu_sw_over_all']==0,'wotus2020_dwv_index']=1

# At least one SW or GU Water intake impacted with alternative water types
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all'].between(0,1,inclusive=False)) & (data['total_intakes']>data['total_gu_sw_intakes']) & (data['disadvantage_status_type']=='Non-Disadvantaged'),'wotus2020_dwv_index']=2
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all'].between(0,1,inclusive=False)) & (data['total_intakes']>data['total_gu_sw_intakes']) & (data['disadvantage_status_type']=='Disadvantaged'),'wotus2020_dwv_index']=3
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all'].between(0,1,inclusive=False)) & (data['total_intakes']>data['total_gu_sw_intakes']) &  (data['disadvantage_status_type']=='Severely Disadvantaged'),'wotus2020_dwv_index']=4
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all'].between(0,1,inclusive=False)) & (data['total_intakes']>data['total_gu_sw_intakes']) &  (data['disadvantage_status_type'].isnull()),'wotus2020_dwv_index']=3

# Subset of SW and GU water intakes impacted with no alternative water types
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all'].between(0,1,inclusive=False)) & (data['total_intakes']==data['total_gu_sw_intakes']) & (data['disadvantage_status_type']=='Non-Disadvantaged'),'wotus2020_dwv_index']=5
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all'].between(0,1,inclusive=False)) & (data['total_intakes']==data['total_gu_sw_intakes']) & (data['disadvantage_status_type']=='Disadvantaged'),'wotus2020_dwv_index']=6
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all'].between(0,1,inclusive=False)) & (data['total_intakes']==data['total_gu_sw_intakes']) &  (data['disadvantage_status_type']=='Severely Disadvantaged'),'wotus2020_dwv_index']=7
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all'].between(0,1,inclusive=False)) & (data['total_intakes']==data['total_gu_sw_intakes']) &  (data['disadvantage_status_type'].isnull()),'wotus2020_dwv_index']=6

# All SW and GU water intakes impacted with no alternative water types
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all']==1) & (data['total_intakes']==data['total_gu_sw_intakes']) & (data['disadvantage_status_type']=='Non-Disadvantaged'),'wotus2020_dwv_index']=5
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all']==1) & (data['total_intakes']==data['total_gu_sw_intakes']) & (data['disadvantage_status_type']=='Disadvantaged'),'wotus2020_dwv_index']=6
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all']==1) & (data['total_intakes']==data['total_gu_sw_intakes']) &  (data['disadvantage_status_type']=='Severely Disadvantaged'),'wotus2020_dwv_index']=7
data.loc[(data['d_fed_prim'].isin(['SW','GU'])) & (data['ratio_impacted_gu_sw_over_all']==1) & (data['total_intakes']==data['total_gu_sw_intakes']) &  (data['disadvantage_status_type'].isnull()),'wotus2020_dwv_index']=6

# The index for SWP take their seller's index

