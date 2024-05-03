
import arcpy
from arcpy import env
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcpy.sa import *
import os
import geopandas as gpd

from src.data.make_dataset import munis


#define variables

#town name
#town_name = 'Revere'

#project geodatabase
env.workspace = r'K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP\ArcGIS\CoolRoofs_Analysis.gdb'
env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
sampling_value = .75

def create_las_dataset(town_name, las_folder):
    '''
    description
    '''
    #input variables

    env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    out_las_dataset = os.path.join(las_folder, (town_name + '_lasd.lasd'))

    ### get a list of las tiles that intersect with the muni ###

    muni_gdf = munis.loc[munis['municipal'] == town_name]
    index_fp = r'I:\Imagery\MassGIS_LAS_files\goodies\goodies\indices\USGS_MA_CentralEastern_1_2021_TileIndex.shp'
    index = gpd.read_file(index_fp)

    #reproject all to mass mainland
    mass_mainland_crs = "EPSG:26986"

    index = index.to_crs(mass_mainland_crs)
    muni_gdf = muni_gdf.to_crs(mass_mainland_crs)

    intersecting = index.sjoin(muni_gdf, how='inner')
    intersecting_list =  intersecting['Tile_ID'].tolist()

    las_list = []

    for item in intersecting_list:
        for dirpath, dirnames, filenames in os.walk(las_folder):
            for filename in filenames:
                if item in filename: #ignores case
                    if filename.endswith('.las'): #search for file type
                        las_list.append(os.path.join(dirpath,filename))

    #now create las dataset based on list of indexed tiles
    arcpy.CreateLasDataset_management(input=las_list,
                                    out_las_dataset=out_las_dataset,
                                    compute_stats='COMPUTE_STATS')
    
    return out_las_dataset

def create_ndsm_raster(town_name, las_dataset):
    '''
    description
    '''

    env.workspace = r'K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP\ArcGIS\CoolRoofs_Analysis.gdb'
    env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    
    #DTM
    ground_layer = town_name + '_ground_layer'
    ground_code = [1]
    ground_return_values = ['LAST', 'LAST_OF_MANY']
    out_dtm_raster = town_name + '_dtm_surface'

    
    #DSM
    surface_layer = town_name + '_surface_layer'
    surface_return_values = [1, 'FIRST_OF_MANY']
    out_dsm_raster = town_name + '_building_dsm_surface'
    building_code = [6]

    #NDSM
    in_raster1 = out_dsm_raster
    in_raster2 = out_dtm_raster
    out_ndsm_raster = town_name + '_ndsm_buildings'

    ## DIGITAL TERRAIN MODEL (DTM) ##
    dtm_layer = arcpy.management.MakeLasDatasetLayer(in_las_dataset=las_dataset, 
                                                    out_layer = ground_layer, 
                                                    class_code = ground_code,
                                                    return_values = ground_return_values)

    
    arcpy.conversion.LasDatasetToRaster(in_las_dataset=dtm_layer, 
                                        out_raster=out_dtm_raster, 
                                        value_field='ELEVATION', 
                                        interpolation_type = 'BINNING AVERAGE LINEAR',
                                        sampling_type='CELLSIZE', 
                                        sampling_value=sampling_value)
    
    ## DIGITAL SURFACE MODEL (DSM) ##
    

    dsm_layer = arcpy.management.MakeLasDatasetLayer(in_las_dataset=las_dataset, 
                                                    out_layer = surface_layer, 
                                                    class_code = building_code,
                                                    return_values = surface_return_values)


    arcpy.conversion.LasDatasetToRaster(in_las_dataset=dsm_layer, 
                                        out_raster=out_dsm_raster, 
                                        value_field='ELEVATION',
                                        interpolation_type = 'BINNING MAXIMUM NONE',
                                        sampling_type='CELLSIZE', 
                                        sampling_value=sampling_value)

    

    ## NORMALIZED DIGITAL SURFACE MODEL (NDSM) ##

    # Excuate RasterCalculator(Minus) function
    out_ndsm_raster = RasterCalculator(rasters= [in_raster1, in_raster2], 
                                        input_names = ["x", "y"],
                                        expression="x-y")
    return out_ndsm_raster

    
def create_slope_raster (town_name, ndsm_raster):
    '''
    describe
    '''
    env.workspace = r'K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP\ArcGIS\CoolRoofs_Analysis.gdb'
    env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    
    out_slope_raster = town_name + '_slope_buildings'

    ## SLOPE ##
    slope = Slope(in_raster=ndsm_raster, 
                    output_measurement='PERCENT_RISE')

    slope.save(out_slope_raster)

    return out_slope_raster

def create_aspect_raster (town_name, ndsm_raster):
    '''
    describe
    '''
    env.workspace = r'K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP\ArcGIS\CoolRoofs_Analysis.gdb'
    env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    
    out_aspect_raster = town_name + '_aspect_buildings'

    ## ASPECT ##
    aspect = Aspect(in_raster=ndsm_raster)

    aspect.save(out_aspect_raster)

    return out_aspect_raster


def create_intensity_raster (town_name, las_dataset):
    '''
    describe
    '''
    env.workspace = r'K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP\ArcGIS\CoolRoofs_Analysis.gdb'
    env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    

    #intensity inputs
    out_intensity_raster = town_name + '_intensity'
    surface_layer = town_name + '_surface_layer'
    building_code = [6]
    surface_return_values = [1, 'FIRST_OF_MANY']


    ## INTENSITY ## 
    intensity_layer = arcpy.management.MakeLasDatasetLayer(in_las_dataset=las_dataset, 
                                                    out_layer = surface_layer, 
                                                    class_code = building_code,
                                                    return_values = surface_return_values)


    arcpy.conversion.LasDatasetToRaster(in_las_dataset=intensity_layer, 
                                        interpolation_type = 'BINNING AVERAGE NONE',
                                        out_raster=out_intensity_raster, 
                                        value_field='INTENSITY',
                                        sampling_type='CELLSIZE', 
                                        sampling_value=sampling_value)
    
    return intensity_layer