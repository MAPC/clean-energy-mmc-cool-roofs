#heat_fp = 'K:\\DataServices\\Projects\\Current_Projects\\Climate_Change\\MVP_MMC_Heat_MVP\\00 Task 2 Deliverables\\2.1 Attachments\\00 Uploaded to Sharepoint\\Shapefile_LSTIndex\\LSTindex.tif'

import pandas as pd
import geopandas as gpd
from src.data.make_dataset import *
import numpy as np
import matplotlib.pyplot as plt
import textwrap
import rasterio
import rasterstats
import os

'''
#set defaults for matplotlib
plt.rcParams.update({'font.family':'Tw Cen MT'})
plt.rcParams["figure.figsize"] = (8, 8)
plt.rcParams.update({'font.size': 12})
'''


def get_file(dir_name:str,
             muni:str=None,
             fileType:str=None):
    '''
    some town names are substrings of other town names (ex: Reading is a substring of North Reading,
        or Dover in Andover)
    this causes errors when trying to pull the right muni's file from a directory.
    this function pulls the correct matching file.
    can  also pull just the correct file type out (ie, a .shp from a whole shapefile)

    inputs:
    - dir_name: directory name to search through
    - muni(str): muni name, as seen in file paths (ie, with any included underscores). Not case sensitive.
    - filetype(str): optional, could be .shp, .csv, etc.

    output:
    correct file name to read from
    '''

    #search through all file names in the directory for those that include the muni name
    #outputs a list of file names
    

    if muni:

        list_of_files = []
        if fileType: #if there is a specified file type to draw from
            for dirpath, dirnames, filenames in os.walk(dir_name):
                for filename in filenames:
                    if muni.casefold() in filename.casefold(): #ignores case
                        if filename.endswith(fileType): #search for file type
                            list_of_files.append(filename)
        else:
            for dirpath, dirnames, filenames in os.walk(dir_name):
                for filename in filenames:
                    if muni.casefold() in filename.casefold(): #ignores case
                        list_of_files.append(filename)
        
        
        if len(list_of_files) == 1: #for towns that don't trigger multiple file names, can stop here
            file = os.path.join(dirpath, list_of_files[0])
        

        else: #otherwise, match muni prefix or name depending on type of substring conflict
            #start with names (cases where muni names are substrings of others, not related to prefix)
            non_prefix_munis = ['Lynn', 'Dover', 'Milton', 'Stow']
            if muni in non_prefix_munis:
                if muni.casefold() == 'Lynn'.casefold():
                   list_of_files = list(filter(lambda x: 'Lynnfield'.casefold() not in x.casefold(), list_of_files))
                   file = os.path.join(dirpath, list_of_files[0])  
                elif muni.casefold() == 'Dover'.casefold():
                    list_of_files = list(filter(lambda x: 'Andover'.casefold() not in x.casefold(), list_of_files))
                    file = os.path.join(dirpath, list_of_files[0])  
                elif muni.casefold() == 'Milton'.casefold():
                    list_of_files = list(filter(lambda x: 'Hamilton'.casefold() not in x.casefold(), list_of_files))
                    file = os.path.join(dirpath, list_of_files[0])  
                elif muni.casefold() == 'Stow'.casefold():
                    list_of_files = list(filter(lambda x: 'Williamstown'.casefold() not in x.casefold(), list_of_files))
                    file = os.path.join(dirpath, list_of_files[0])  
            else: #move on to prefixes
                prefixes = ['East', 'North', 'West', 'South', 'New']
                for prefix in prefixes: #loop through prefixes
                    #if a town has a prefix, find the matching prefix in the fle name
                    if prefix.casefold() in muni.casefold(): 
                        #search through list of files for that prefix
                        list_of_files = list(filter(lambda x: prefix.casefold() in x.casefold(), list_of_files))
                        file = os.path.join(dirpath, list_of_files[0]) 
                    #if no prefix in town name, find the file name without the prefix
                    else: 
                        list_of_files = list(filter(lambda x: prefix.casefold() not in x.casefold(), list_of_files))
                        file = os.path.join(dirpath, list_of_files[0]) 
    else:
        for dirpath, dirnames, filenames in os.walk(dir_name):
            for filename in filenames:
                if filename.endswith(fileType):
                    file = os.path.join(dirpath, filename)
    return(file)

#create land use dataset
def get_landuse_data(muni):
       #move these to make_dataset script eventually
    projects_dir = 'K:\\DataServices\\projects\\Current_Projects' 

    mapc_lpd_folder = os.path.join(datasets_dir, 'Parcel_DB\\Data\\LPDB_Update_Dec.23_Jan.24\\parcels_by_muni')
    
    #path for where state parcel layers can be unzipped to and read from
    intermediate_path = os.path.join(projects_dir, "Housing\\Section_3A\\Analytical_Toolbox\\Data\\Intermediate")

    '''
    input = muni name
    process = picks out the right shapefile from the state's municipal land use database;
             makes a subdirectory in intermediate folder w town name and exports land use shapefile to it
             reads that shapefile in as a geodataframe
             merges with mapc land parcel database 
    output = state detailed parcel layer, merged with mapc land parcel database
    '''

    def get_state_pre_process_layer(muni):

     
        '''
        input = muni name
        output = picks out the right shapefile from the state's municipal land use database;
                makes a subdirectory in intermediate folder w town name and exports land use shapefile to it
                reads that shapefile in as a geodataframe

        '''

        path = os.path.join(intermediate_path, muni)


        #set land  use variable
        town_lu_path = get_file(dir_name=path, 
                                fileType='.shp')

        muni_state_parcels = gpd.read_file(town_lu_path)

        return muni_state_parcels
    
    muni_state_parcels = get_state_pre_process_layer(muni)
    

    #read in land parcel database
    file_name = get_file(dir_name=mapc_lpd_folder, 
                         muni=muni)

    #file_name = lpd_prefix + muni + lpd_suffix
    muni_lpd_path = os.path.join(mapc_lpd_folder, file_name)
    

    mapc_lpd = pd.read_csv(muni_lpd_path)  

    #merge land parcel database with state muni parcels
    muni_lpd_preprocess = muni_state_parcels.merge(mapc_lpd, on='LOC_ID', how='inner')

 
    return(muni_lpd_preprocess)  
    

def muni_process(muni, file_path):
    '''
    Analyzes the breakdown of structures located in high heat areas in a municipality of interest.

    INPUTS
    - muni name (string)
    - file path for shapefile of parcels with ownership and heat info (can replicate if need be)

    OUTPUTS 
    - creates a crosstab bar chart comparing the percentage of all buildings in the muni that fall under/
    different real estate typologies compared to the percentage of buildings *in high heat areas* that/
    fall under those typologies. Exports chart to "charts" folder in project K drive folder
    - returns a data frame with summary information about:
        1. the count of structures in the muni that are publicly owned, in high heat areas, and in EJ communities
        2. the top 5 real estate typologies that are in high heat areas, with associated structure counts and proportions
        3. the breakdown of privately owned vs publicly owned structures in high heat areas

    In this script, "high heat" areas refers to the census blocks that are in the top 20% of hottest census blocks in /
    the municipality.

    '''

    #read in municipal parcels from ms4, eliminate ROW segments
    muni_parcels_gdf=gpd.read_file(file_path)
    muni_gdf = muni_parcels_gdf.loc[muni_parcels_gdf['UseDesc'] != 'ROW segment']
    
    
    #reformat use code to match with real estate lookup codes
    land_use_lookup['USE_CODE'] = land_use_lookup['USE_CODE'].apply(lambda x: '{0:0>3}'.format(x))
    real_estate_lookup['use_code_3dg'] = real_estate_lookup['use_code_3dg'].str.replace('"', '') 

    ## JOIN PARCELS, CODES, AND STRUCTURES ##

    #merge parcels with use descriptions to get use codes
    muni_gdf = muni_gdf.merge(land_use_lookup, left_on='UseDesc', right_on='USE_DESC', how='left').drop_duplicates()
    
    #merge real estate lookup codes based on land use codes
    muni_gdf = muni_gdf.merge(real_estate_lookup, left_on='USE_CODE', right_on='use_code_3dg', how='left')
    
    #get real estate typology descriptions based on real estate codes
    muni_gdf = muni_gdf.merge(real_estate_lookup_code, on='real_estate_type', how='left')

    #determine highest heat parcels based on 'rnk_heat' value. high heat in this case means being in the
    #top 20% of hottest census blocks
    heat_bnry_rule = [muni_gdf['rnk_heat'] >= 0.8, 
                      muni_gdf['rnk_heat'] < 0.8]
    
    choices = ['in high heat area', 
               'not in high heat area']
    
    #create a new field based on whether or not a parcel is in a high heat area
    muni_gdf['heat_mmc'] = np.select(heat_bnry_rule, choices, default=np.nan)
    
    #read in muni structures, mask by muni boundary
    muni_structures = gpd.read_file(building_structures_gdb, layer=building_structures_layer, mask=muni_gdf)

    #spatially join structures to parcels, group by structure id to eliminate duplicates
    muni_structures_join_parcels = muni_structures.sjoin(muni_gdf, how='left').groupby(by='STRUCT_ID').agg('first').reset_index()
    
    ## CROSSTABS AND CHARTS ##

    #create a crosstab and bar chart for real estate typology in high heat areas vs municipality as a whole
    heat_xtab = pd.crosstab(muni_structures_join_parcels['description'], muni_structures_join_parcels['heat_mmc'], normalize='columns', margins=True, margins_name='All buildings in muni')[['in high heat area', 'All buildings in muni']]
    xtab_plot = heat_xtab.plot.barh(color=['orangered', 'lightgray'])
    plt.title('Property distribution in ' + muni, size=16)
    plt.xlabel('Proportion of buildings', size=14)
    plt.ylabel('Real estate typology',size=14)
    labels = [textwrap.fill(label.get_text(), 50) for label in xtab_plot.get_yticklabels()]
    xtab_plot.set_yticklabels(labels)
    
    # Annotate every single Bar with its value, based on it's width 
    for bars in xtab_plot.containers:
        xtab_plot.bar_label(bars, padding=3, fmt='%.2f', size=10)

    plt.savefig(chart_fp + '\\prop_dist_' + muni + '.jpg', bbox_inches='tight')


    ## CREATE MuNICIPAL SUMMARY TABLES ##

    #first, get a count of structures that are 1) publicly owned, 2) in high heat areas, and 3) in ej communities
    muni_structures_public_heat_ej = muni_structures_join_parcels.loc[(muni_structures_join_parcels['pblc'] == 1) &
                                                                (muni_structures_join_parcels['rnk_heat'] >= 0.8)&
                                                                (muni_structures_join_parcels['ej'] == 1)]
    count_structures = len((muni_structures_public_heat_ej))


    # create a dataframe with muni name and count of ej/heat/public structures
    data = {'muni': [muni],
            'count_ej_public_highheat': [count_structures],
            }

    df = pd.DataFrame(data)

    #now from the structures/parcel join table, select the subset just in high heat areas
    structures_high_heat = muni_structures_join_parcels.loc[muni_structures_join_parcels['rnk_heat'] >= 0.8]

    #get value counts of different real estate typologies
    structure_uses_value_counts = structures_high_heat['description'].value_counts().rename_axis('unique_values').reset_index(name='counts')

    #add to the value count table a field for percent of high-heat parcels that fall under a use category
    structure_uses_value_counts['pct_of_parcels'] = structure_uses_value_counts['counts'] / len(structures_high_heat)

    #add fields to the muni summary table for the highest, second highest, etc real estate typology, count of parcels, and percent of parcels
    df['1_use'] = structure_uses_value_counts['unique_values'][0]
    df['1_count'] = structure_uses_value_counts['counts'][0]
    df['1_pct'] = structure_uses_value_counts['pct_of_parcels'][0]

    df['2_use'] = structure_uses_value_counts['unique_values'][1]
    df['2_count'] = structure_uses_value_counts['counts'][1]
    df['2_pct'] = structure_uses_value_counts['pct_of_parcels'][1]

    df['3_use'] = structure_uses_value_counts['unique_values'][2]
    df['3_count'] = structure_uses_value_counts['counts'][2]
    df['3_pct'] = structure_uses_value_counts['pct_of_parcels'][2]

    df['4_use'] = structure_uses_value_counts['unique_values'][3]
    df['4_count'] = structure_uses_value_counts['counts'][3]
    df['4_pct'] = structure_uses_value_counts['pct_of_parcels'][3]

    df['5_use'] = structure_uses_value_counts['unique_values'][4]
    df['5_count'] = structure_uses_value_counts['counts'][4]
    df['5_pct'] = structure_uses_value_counts['pct_of_parcels'][4]

    #get a breakdown of private vs publicly owned structures in high heat areas
    structure_owner_value_counts = structures_high_heat['par_typ'].value_counts().rename_axis('unique_values').reset_index(name='counts')
    structure_owner_value_counts['par_typ'] = structure_owner_value_counts['counts'] / len(structures_high_heat)

    #add counts to dataframe
    df['private_ownership_pct'] = structure_owner_value_counts['par_typ'][0] #private ownership
    df['public_ownership_pct'] = structure_owner_value_counts['par_typ'][1] #public ownership


    return(df)

# adding in the following scripts in case we want to re-run a new parcel dataset 

def heat_score (muni_parcels, heat_index_fp):

    '''
    For each census block  in the municipality, determines the relative heat index score compared to all other block groups. 
    Those in the top 40% of scores are retained as having heat "vulnerability". 
    Parcels within those block groups can then be prioritized higher.

    Inputs: Muni boundary (gdf), heat index raster (geotiff)

    '''
    from rasterstats import zonal_stats
    from src.data.make_dataset import mapc_blocks

    with rasterio.open(heat_index_fp) as raster:
        transform = raster.transform
        lst = raster.read(1).astype('float64')

    #read in census blocks, clip to muni and eliminate sliver blocks that remain
    mapc_blocks['og_area'] = mapc_blocks['geometry'].area
    muni_blocks = mapc_blocks.clip(muni_parcels)
    muni_blocks['pct_bg'] = ((muni_blocks['geometry'].area) / (muni_blocks['og_area'])) * 100

    #only keep block groups where 5% or more of the bg remains. Reset index for zonal stats
    muni_blocks = muni_blocks.loc[muni_blocks['pct_bg'] > 5].reset_index()

    #run zonal stats on heat index - what is the mean lst index score across census block?
    lst_stats = pd.DataFrame(zonal_stats(muni_blocks, 
                                        lst, 
                                        affine=transform, 
                                        stats='mean'))
    #join back to blocks, rename field
    muni_blocks_heat = muni_blocks[['geoid20', 'geometry']].join(lst_stats)
    muni_blocks_heat = muni_blocks_heat.rename(columns={'mean':'lst_mean'})

    #rank each block based on relative lst index score
    muni_blocks_heat['rnk_heat'] = muni_blocks_heat['lst_mean'].rank(method='min', pct=True)

    #create a categorical ranking for where each block lands relative to one another
    heat_rule = [
                    (muni_blocks_heat['rnk_heat'] > 0.80),
                    (muni_blocks_heat['rnk_heat'] <= 0.80) & (muni_blocks_heat['rnk_heat'] > 0.60),
                    (muni_blocks_heat['rnk_heat'] <= 0.60) & (muni_blocks_heat['rnk_heat'] > 0.40),
                    (muni_blocks_heat['rnk_heat'] <= 0.40) & (muni_blocks_heat['rnk_heat'] > 0.20),
                    (muni_blocks_heat['rnk_heat'] <= 0.20) & (muni_blocks_heat['rnk_heat'] > 0)
            ]

    choices = ['Very high heat index', 'Moderately high heat index', 'Moderate heat index', 'Moderately low heat index', 'Very low heat index']

    muni_blocks_heat['heat_cmp'] = np.select(heat_rule, 
                                             choices#, 
                                             #default=np.nan
                                             )
    

    muni_parcels = gpd.sjoin(muni_parcels, 
                             muni_blocks_heat,
                             how='left').groupby(by='LOC_ID').agg('first').reset_index()

    return(muni_parcels)

from src.data.public_uses import public_land_uses, owner_types


def public_ownership(parcel_data):

    parcel_dataset = parcel_data.copy()
    #does it have a listed public use?
    parcel_dataset['pblc_use'] = parcel_dataset['UseDesc'].apply(lambda x: 1 if x in public_land_uses else 0).astype(int)

    #does it have a listed public owner type
    parcel_dataset['pblc_owner'] = parcel_dataset['Owner'].str.contains('|'.join(owner_types), na=False).astype(int)

    #create a field (pblc), 1 = has a public use or owner, 0 = neither 
    public_rule = [
        ((parcel_dataset['pblc_use'] == 1) | (parcel_dataset['pblc_owner'] == 1)),
        ((parcel_dataset['pblc_use'] != 1) & (parcel_dataset['pblc_owner'] != 1))
    ]

    choices = [1, 0]

    parcel_dataset['pblc'] = np.select(public_rule, choices, default=np.nan)

    #create parcel type field that identifies whether a site is Public, or private
    def conditions(row):
        if row['pblc'] == 1:
            val = 'Public parcel'
        else:
            val = 'Private parcel'
        return val
        
    parcel_dataset['par_typ'] =  parcel_dataset.apply(conditions, axis=1)

    return parcel_dataset




def parcel_process(parcel_data, structures_data):
    #add to make_dataset = 
    heat_fp = 'K:\\DataServices\\Projects\\Current_Projects\\Climate_Change\\MVP_MMC_Heat_MVP\\00 Task 2 Deliverables\\2.1 Attachments\\00 Uploaded to Sharepoint\\Shapefile_LSTIndex\\LSTindex.tif'

    '''
    Analyzes the breakdown of structures located in high heat areas in a municipality of interest.

    INPUTS
    - file path for shapefile of parcels with ownership and heat info (can replicate if need be)

    OUTPUTS 
    - 
    In this script, "high heat" areas refers to the census blocks that are in the top 20% of hottest census blocks in /
    the municipality.

    '''
    #reproject all to mass mainland
    mass_mainland_crs = "EPSG:26986"
    parcel_data = parcel_data.to_crs(mass_mainland_crs)
    structures_data = structures_data.to_crs(mass_mainland_crs)


    #reformat use code to match with real estate lookup codes
    land_use_lookup['USE_CODE'] = land_use_lookup['USE_CODE'].apply(lambda x: '{0:0>3}'.format(x))
    real_estate_lookup['use_code_3dg'] = real_estate_lookup['use_code_3dg'].str.replace('"', '') 

    ## JOIN PARCELS, CODES, AND STRUCTURES ##

    #merge parcels with use descriptions to get use codes
    muni_gdf = parcel_data.merge(land_use_lookup, left_on='LUC_Assign_M', right_on='USE_CODE', how='left').drop_duplicates()
    
    #merge real estate lookup codes based on land use codes
    muni_gdf = muni_gdf.merge(real_estate_lookup, left_on='USE_CODE', right_on='use_code_3dg', how='left').reset_index()
    
    #get real estate typology descriptions based on real estate codes
    muni_gdf = muni_gdf.merge(real_estate_lookup_code, on='real_estate_type', how='left').reset_index()

    #determine highest heat parcels based on 'rnk_heat' value. high heat in this case means being in the
    #top 20% of hottest census blocks
    muni_gdf = heat_score (muni_gdf, heat_fp)

    heat_bnry_rule = [muni_gdf['rnk_heat'] >= 0.8, 
                      muni_gdf['rnk_heat'] < 0.8]
    
    choices = ['in high heat area', 
               'not in high heat area']
    
    #create a new field based on whether or not a parcel is in a high heat area
    muni_gdf['heat_mmc'] = np.select(heat_bnry_rule, choices, default=np.nan)
   
    #reproject all to mass mainland
    mass_mainland_crs = "EPSG:26986"
    muni_gdf = muni_gdf.set_crs(mass_mainland_crs)
    structures_data = structures_data.to_crs(mass_mainland_crs)

    #spatially join structures to parcels, group by structure id to eliminate duplicates
    muni_gdf = muni_gdf.drop(['index_right'], axis=1)
    muni_structures_join_parcels = structures_data.sjoin(muni_gdf, how='left').groupby(by='STRUCT_ID').agg('first').reset_index()
  
    return(muni_structures_join_parcels)

