#heat_fp = 'K:\\DataServices\\Projects\\Current_Projects\\Climate_Change\\MVP_MMC_Heat_MVP\\00 Task 2 Deliverables\\2.1 Attachments\\00 Uploaded to Sharepoint\\Shapefile_LSTIndex\\LSTindex.tif'

import pandas as pd
import geopandas as gpd
from src.data.make_dataset import *
from src.data.public_uses import *
import numpy as np
import matplotlib.pyplot as plt
import textwrap
import rasterio
import rasterstats
import os
import zipfile36 as zipfile
from io import BytesIO
from urllib.request import urlopen
import shutil




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



def get_landuse_data(muni):
    

    '''
    input = muni name
    process = picks out the right shapefile from the state's municipal land use database;
             makes a subdirectory in intermediate folder w town name and exports land use shapefile to it
             reads that shapefile in as a geodataframe
             merges with mapc land parcel database 
    output = state detailed parcel layer, merged with mapc land parcel database
    '''
    from src.data.make_dataset import mapc_lpd_folder    
    from datetime import datetime

    def get_most_updated_state_assessors_data(muni):
        '''
        pulls parcel data from the state's assessors website
        '''
        #get shapefile from a massgis link
        shapefile_excel = 'https://www.mass.gov/doc/massgis-parcel-data-download-links-table/download'
        shapefile_lookup = pd.read_excel(shapefile_excel)

        town_shp_lookup_link = shapefile_lookup.loc[shapefile_lookup['Town Name'] == muni.upper()]

        #extract into a temporary folder for use
        cool_roofs_project_dir = r'K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP'
        path = os.path.join(cool_roofs_project_dir, 'Data', muni) #make a subdirectory in ortho folder w town name
        os.makedirs(path, exist_ok=True) 

        for url in town_shp_lookup_link['Shapefile Download URL'].tolist():
            with urlopen(url) as zipresp:
                with zipfile.ZipFile(BytesIO(zipresp.read())) as zfile:
                    zfile.extractall(path)


        layer = get_file(path, 'TaxPar', '.shp')
        parcel_layer = gpd.read_file(layer)

        parcel_layer = parcel_layer.loc[parcel_layer['POLY_TYPE']=='FEE']
        return(parcel_layer)
    

    #get the most updated parcel data from massgis
    muni_state_parcels = get_most_updated_state_assessors_data(muni)

    #now delete the temporary folder that was made for that layer
    path = os.path.join(cool_roofs_project_dir, 'Data', muni)
    shutil.rmtree(path)

    #read in land parcel database
    file_name = get_file(dir_name=mapc_lpd_folder, 
                         muni=muni)

    #file_name = lpd_prefix + muni + lpd_suffix
    muni_lpd_path = os.path.join(mapc_lpd_folder, file_name)
    mapc_lpd = pd.read_csv(muni_lpd_path)  

    #merge land parcel database with state muni parcels
    #only keep the loc_id from state parcel database because we only want the MAPC lpd fields
    muni_lpd_preprocess = muni_state_parcels[['LOC_ID', 'geometry']].merge(mapc_lpd, 
                                                                           on='LOC_ID', 
                                                                           how='inner')

    return(muni_lpd_preprocess)  
    


# adding in the following scripts in case we want to re-run a new parcel dataset 

def get_heat_score_mmc(heat_index_fp):

    '''
    For each census block  in the municipality, determines the relative heat index score compared to all other block groups. 
    Parcels within those block groups can then be prioritized higher.

    Inputs: Muni boundary (gdf), heat index raster (geotiff), comparitive geography

    '''
    from rasterstats import zonal_stats
    from src.data.make_dataset import mapc_blocks, mmc_munis, munis


    with rasterio.open(heat_index_fp) as raster:
        transform = raster.transform
        lst = raster.read(1).astype('float64')

    ## PREPARE GDF OF MMC REGION ## 
    
    mmc_gdf = munis.loc[munis['municipal'].isin(mmc_munis)]

    #retain census blocks within mmc
    mapc_blocks['og_area'] = mapc_blocks['geometry'].area #get original area to do sliver analysis

    mmc_blocks = mapc_blocks.clip(mmc_gdf)
    mmc_blocks['pct_bg'] = ((mmc_blocks['geometry'].area) / (mmc_blocks['og_area'])) * 100
    mmc_blocks['pct_bg'] = ((mmc_blocks['geometry'].area) / (mmc_blocks['og_area'])) * 100
    mmc_blocks = mmc_blocks.loc[mmc_blocks['pct_bg'] > 5].reset_index()    #only keep block groups where 5% or more of the bg remains. Reset index for zonal stats

    ## ZONAL STATS ## 
    #run zonal stats on heat index for mmc - what is the mean lst index score across census block?
    lst_stats = pd.DataFrame(zonal_stats(mmc_blocks, 
                                        lst, 
                                        affine=transform, 
                                        stats='mean'))
    
    #join back to blocks, rename field
    mmc_blocks_heat = mmc_blocks[['geoid20', 'geometry']].join(lst_stats)
    mmc_blocks_heat = mmc_blocks_heat.rename(columns={'mean':'lst_mean'})

    ## COMPARE LST MEAN TO REST OF MMC REGION ##    
    #rank each block based on relative lst index score
    mmc_blocks_heat['rnk_heat_mmc'] = mmc_blocks_heat['lst_mean'].rank(method='min', pct=True)

    return mmc_blocks_heat

def get_muni_heat_score(mmc_blocks_heat, 
                        town_name, 
                        muni_parcels):
    '''
    describe
    '''
   

    ## COMPARE LST MEAN TO REST OF MUNI ## 
    muni_gdf = munis.loc[munis['municipal'] == town_name]
    
    #clip mmc blocks (with heat field) to muni and eliminate sliver blocks that remain
    mmc_blocks_heat['og_area'] = mmc_blocks_heat['geometry'].area
    muni_blocks = mmc_blocks_heat.clip(muni_gdf)
    muni_blocks['pct_bg'] = ((muni_blocks['geometry'].area) / (muni_blocks['og_area'])) * 100
    muni_blocks = muni_blocks.loc[muni_blocks['pct_bg'] > 5].reset_index()  #only keep block groups where 5% or more of the bg remains. Reset index for zonal stats


    #rank each block based on relative lst index score
    muni_blocks['rnk_ht_muni'] = muni_blocks['lst_mean'].rank(method='min', pct=True)

    ## JOIN BACK TO MUNI PARCELS ## 

    muni_parcels = gpd.sjoin(muni_parcels, 
                             muni_blocks[['geometry', 'lst_mean', 'rnk_heat_mmc', 'rnk_ht_muni']],
                             how='left').groupby(by='LOC_ID').agg('first').reset_index()

    return(muni_parcels)



def public_ownership(parcel_data, use_desc_field, owner_field):
    '''
    description coming

    '''

    parcel_dataset = parcel_data.copy()
    #does it have a listed public use?
    parcel_dataset['pblc_use'] = parcel_dataset[use_desc_field].apply(lambda x: 1 if x in public_land_uses else 0).astype(int)

    #does it have a listed public owner type
    parcel_dataset['pblc_owner'] = parcel_dataset[owner_field].str.contains('|'.join(owner_types), na=False).astype(int)

    parcel_dataset['muni_owner'] = parcel_dataset[owner_field].str.contains('|'.join(muni_types), na=False).astype(int)

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




def cool_roof_process(town_name, 
                      rooftops_layer,
                      heat_blocks_layer):
    
    from datetime import datetime

    '''
    ## Rachel to fill in ## 
    
    Analyzes the breakdown of structures located in high heat areas in a municipality of interest.

    INPUTS
    - file path for shapefile of parcels with ownership and heat info (can replicate if need be)

    OUTPUTS 
    - 
    In this script, "high heat" areas refers to the census blocks that are in the top 20% of hottest census blocks in /
    the municipality.

    '''
    ## BRING IN PARCEL AND STRUCTURES DATA ##
    #repurpose 3A script to get parcels with MAPC Land Parcel Database info attached
    
    muni_parcels = get_landuse_data(town_name)

    fields_to_keep = ['LOC_ID', 'SITE_ADDR_M', 'CITY', 'OWNER1', 'geometry', 'TOWN_ID', 'BLDG_VAL', 
                      'LOT_SIZE', 'L3_Description_M', 'LUC_Assign_M',
                      'YEAR_BUILT', 'STYLE', 'imputed_units', 'FAR', 'BLDGV_PSF', 'BLDLND_RAT']
    
    muni_parcels = muni_parcels[fields_to_keep]

    #now start joining process
    
    ## ADD LAND USE AND REAL ESTATE CODES ## 


    #reformat use code to match with real estate lookup codes
    land_use_lookup['USE_CODE'] = land_use_lookup['USE_CODE'].apply(lambda x: '{0:0>3}'.format(x))
    real_estate_lookup['use_code_3dg'] = real_estate_lookup['use_code_3dg'].str.replace('"', '') 

    #merge parcels with use descriptions to get use codes
    muni_parcels = muni_parcels.merge(land_use_lookup[['USE_CODE', 'USE_DESC']], 
                                      left_on='LUC_Assign_M', 
                                      right_on='USE_CODE', 
                                      how='left').groupby(
                                          by='LOC_ID').agg('first').reset_index()

    #merge real estate lookup codes based on land use codes
    muni_parcels = muni_parcels.merge(real_estate_lookup, 
                                      left_on='USE_CODE', 
                                      right_on='use_code_3dg', 
                                      how='left').groupby(
                                          by='LOC_ID').agg('first').reset_index()

    #get real estate typology descriptions based on real estate codes
    muni_parcels = muni_parcels.merge(real_estate_lookup_code, 
                                      on='real_estate_type', 
                                      how='left').groupby(
                                          by='LOC_ID').agg('first').reset_index()
    
    
    ## HEAT FIELD ##
    #determine highest heat parcels based on 'rnk_heat' value. high heat in this case means being in the
    #top 20% of hottest census blocks


    mass_mainland_crs = "EPSG:26986"
    muni_parcels = muni_parcels.set_crs(mass_mainland_crs)
    muni_parcels = get_muni_heat_score(mmc_blocks_heat=heat_blocks_layer,
                                       town_name=town_name,
                                       muni_parcels=muni_parcels)

    heat_bnry_rule = [muni_parcels['rnk_ht_muni'] >= 0.8, 
                    muni_parcels['rnk_ht_muni'] < 0.8]

    choices = ['in high heat area (muni)', 
                'not in high heat area (muni)']

    #create a new field based on whether or not a parcel is in a high heat area
    muni_parcels['heat_muni'] = np.select(heat_bnry_rule, 
                                         choices, 
                                         default=np.nan)
    
    # now do it for the whole region
    heat_bnry_rule = [muni_parcels['rnk_heat_mmc'] >= 0.8, 
                    muni_parcels['rnk_heat_mmc'] < 0.8]

    choices = ['in high heat area (mmc)', 
                'not in high heat area (mmc)']

    #create a new field based on whether or not a parcel is in a high heat area
    muni_parcels['heat_mmc'] = np.select(heat_bnry_rule, 
                                         choices, 
                                         default=np.nan)
    
    ## PUBLIC OWNERSHIP ## 
    #add a field for whether or not the parcel is publicly owned
    muni_parcels = public_ownership(muni_parcels,
                                    use_desc_field='USE_DESC',
                                    owner_field='OWNER1').set_crs(mass_mainland_crs) #have to debug why this is losing its crs

    ## ENVIRONMENTAL JUSTICE ## 
    #field for whether or not the parcel is in an EJ census block group
    ej_cols_to_keep = ['geometry', 'EJ', 'EJ_CRITERIA_COUNT', 'EJ_CRIT_DESC']

    ej_parcels = gpd.sjoin(muni_parcels.drop(columns='index_right'), ej_2020[ej_cols_to_keep],
                           how='left').groupby(
                        by='LOC_ID').agg('first').reset_index().set_crs(mass_mainland_crs)


    ej_parcels['EJ'] = ej_parcels['EJ'].fillna('No')

    ## JOIN STRUCTURES TO PARCELS ##

    #spatially join structures to parcels, group by structure id to eliminate duplicates
    #only need the cool roofs-relevant fields from rooftops layer
    structures_fields_to_drop = ['SOURCE', 'SOURCETYPE', 'SOURCEDATA', 'MOVED',
                                 'AREA_SQ_FT', 'TOWN_ID', 'TOWN_ID2', 'TOWN_ID3',
                                 'LOCAL_ID', 'ARCHIVED', 'ARCHIVEDATE', 'EDIT_DATE',
                                 'EDIT_BY', 'COMMENTS', 'join_id', 'SHAPE_Length',
                                 'SHAPE_Area']
    
    #clip structures to muni parcels layer, drop unneeded columns, reproject
    structures_data = rooftops_layer.drop(columns=structures_fields_to_drop).clip(muni_parcels).to_crs(mass_mainland_crs)

    
    muni_structures_join_parcels = structures_data.sjoin(ej_parcels.drop(columns='index_right'), 
                                                         how='left').groupby(
                                                             by='STRUCT_ID').agg(
                                                                 'first').set_crs(
                                                                     mass_mainland_crs).reset_index().drop(columns='index_right')
    

    return(muni_structures_join_parcels)


