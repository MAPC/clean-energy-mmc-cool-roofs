def get_state_pre_process_layer(muni): #consider deleting from this repo

    
    '''
    input = muni name
    output = picks out the right shapefile from the state's municipal land use database;
            makes a subdirectory in intermediate folder w town name and exports land use shapefile to it
            reads that shapefile in as a geodataframe

    '''
    intermediate_path = os.path.join(projects_dir, "Housing\\Section_3A\\Analytical_Toolbox\\Data\\Intermediate")
    path = os.path.join(intermediate_path, muni)


    #set land  use variable
    town_lu_path = get_file(dir_name=path, 
                            fileType='.shp')

    muni_state_parcels = gpd.read_file(town_lu_path)


    return muni_state_parcels
#create land use dataset

def muni_process(muni, 
                 muni_structures_join_parcels):

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



import arcpy
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcpy.sa import *
import numpy


def reclassify_by_quantiles(raster, quantiles):
    '''
    script to reclassify by quantile
    
    '''
    desc = arcpy.Describe(raster)

    # Get the quantile break points
    percentiles = list()
    for i in range(1, quantiles):
        percentiles.append(i * (100.0/quantiles))

    # Ensure that the raster is a raster object, in order to identify the minimum and
    #   maximum values
    if type(raster) != arcpy.Raster:
        raster = arcpy.Raster(raster)

    value_minimum = raster.minimum
    value_maximum = raster.maximum

    # Identify a value that does not occur in the raster
    null_value = value_minimum - 1

    # If the raster is not an integer type, then there is no need to futz with NaNs
    if desc.pixelType.startswith('F'):
        arr = arcpy.RasterToNumPyArray(raster, nodata_to_value=numpy.NaN)
    # Since integer arrays can't contain NaNs, you must do wackiness
    else:
        # Convert to an array, setting NoData cells to the unique value
        arr = arcpy.RasterToNumPyArray(raster, nodata_to_value=null_value)
        # Convert the array of integers to an array of floats
        arr = arr.astype('float')
        # Replace the placeholder null value with NaNs
        arr[arr==null_value] = numpy.NaN

    # Compile the quantile breaks
    breakpoints = list(numpy.nanpercentile(arr, percentiles))
    breakpoints.insert(0, value_minimum)
    breakpoints.append(value_maximum)

    # You no longer need the array...though you could do the remaining calculations
    #   on the array instead of one the raster
    del(arr)

    # Map the ranges to class numbers
    remap_table = list()
    for index, breakpoint in enumerate(breakpoints[:-1]):
        remap_table.append([breakpoint, breakpoints[index+1], index+1])
    remap = arcpy.sa.RemapRange(remap_table)

    result = arcpy.sa.Reclassify(raster, 'Value', remap)
    return result