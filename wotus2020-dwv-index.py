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

# For Systems that Purchase water, merge the DWV index of their seller's index
wotus_index_prov=data[['number0','wotus2020_dwv_index']].copy()
wotus_index_prov.rename(columns={'wotus2020_dwv_index':'seller_wotus2020_dwv_index_1', 'number0':'seller_number0_1'}, inplace=True)
data=pd.merge(data, wotus_index_prov, on='seller_number0_1', how='left')
wotus_index_prov.rename(columns={'seller_wotus2020_dwv_index_1':'seller_wotus2020_dwv_index_2', 'seller_number0_1':'seller_number0_2'}, inplace=True)
data=pd.merge(data, wotus_index_prov, on='seller_number0_2', how='left')

# Update the index of SWP systems to the the minimum index of its sellers
swp_prov=data[data['d_fed_prim']=='SWP'].copy()
swp_prov[['seller_wotus2020_dwv_index_1','seller_wotus2020_dwv_index_2']].min(axis=1)
data.loc[data['d_fed_prim']=='SWP','wotus2020_dwv_index']=swp_prov[['seller_wotus2020_dwv_index_1','seller_wotus2020_dwv_index_2']].min(axis=1)
data[['seller_wotus2020_dwv_index_1','seller_wotus2020_dwv_index_2']].min(axis=1)

# Create the index summary impact type
data.loc[data['wotus2020_dwv_index']==1,'index_summary']='No Direct Impact'
data.loc[(data['d_pws_fed_']!='C') & (data['wotus2020_dwv_index']>1),'index_summary']='Direct Impact Non-Community Water System'
data.loc[(data['d_pws_fed_']=='C') & (data['wotus2020_dwv_index']>1) & (data['wotus2020_dwv_index']<5),'index_summary']='Direct Impact with Alternative Sources of Water'
data.loc[(data['d_pws_fed_']=='C') & (data['wotus2020_dwv_index']>=5) & (data['wotus2020_dwv_index']<=10),'index_summary']='Direct Impact with No Alternative Sources of Water'

# Export the index and data to a CSV
data.to_csv(r'data/wotus2020-DWV-Index_all_pws.csv', index = False)