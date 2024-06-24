
import arcpy
from arcpy import env
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcpy.sa import *
import os
import geopandas as gpd

from src.data.make_dataset import munis, cool_roofs_gdb, muni_field


#define variables



#project geodatabase
#env.workspace = cool_roofs_gdb

sampling_value = .8 #can change this sampling value (it is in meters)


def create_las_dataset(town_name, las_folder):

    '''
    Creates a las dataset that covers a municipality of interest

    Inputs: 
    - town_name (str): Town Name (not case sensitive)
    - las_folder: location of las data

    Outputs: las dataset covering municipality

    '''
    #input variables

    env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    out_las_dataset = os.path.join(las_folder, (town_name + '_lasd.lasd'))
    out_slope_raster = os.path.join(cool_roofs_gdb, (town_name + '_slope_buildings'))

    if arcpy.Exists(out_slope_raster): #an existing out_slope_raster would mean this town has already been processed, so skip
        pass

    else:

        ### get a list of las tiles that intersect with the muni ###

        muni_gdf = munis.loc[munis[muni_field].str.casefold() == town_name.casefold()]
        index_fp = r'I:\Imagery\MassGIS_LAS_files\goodies\goodies\indices\USGS_MA_CentralEastern_1_2021_TileIndex.shp'
        index = gpd.read_file(index_fp)

        #first, reproject all to mass mainland
        mass_mainland_crs = "EPSG:26986"

        index = index.to_crs(mass_mainland_crs)
        muni_gdf = muni_gdf.to_crs(mass_mainland_crs)

        #then, use spatial join to identify intersection between muni boundary and tiles 
        intersecting = index.sjoin(muni_gdf, how='inner')
        intersecting_list =  intersecting['Tile_ID'].tolist()

        #create list of tiles
        las_list = []

        for item in intersecting_list:
            for dirpath, dirnames, filenames in os.walk(las_folder):
                for filename in filenames:
                    if item in filename: #ignores case
                        if filename.endswith('.las'): #search for file type
                            las_list.append(os.path.join(dirpath,filename))

        #finally, create las dataset based on list of indexed tiles
        arcpy.CreateLasDataset_management(input=las_list,
                                          out_las_dataset=out_las_dataset,
                                        compute_stats='COMPUTE_STATS')
    
    return out_las_dataset

def create_ndsm_raster(town_name, las_dataset):
    '''
    Creates an ndsm raster covering the municipality of interest. The nDSM depicts the difference between the 
    digital surface model (DSM)—which reflects the highest points of objects (tops of structures, vegetation)—
    and the digital terrain model (DTM), which reflects the underlying “bare earth" (State of Vermont).
    In this function, both DSM and DTM are created andused to define a final nDSM.

    Inputs:
    - town_name (str): Town Name (not case sensitive)
    - las_dataset: las dataset created in create_las_dataset()

    Output:
    - ndsm raster covering municipality

    '''

    ### DEFINE VARIABLES ###

    env.workspace = cool_roofs_gdb
    #env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    

    #DTM
    ground_layer = town_name + '_ground_layer'
    ground_code = [1]
    ground_return_values = ['LAST', 'LAST_OF_MANY']
    out_dtm_raster = r"memory\dtm_surface" #+ town_name + '_dtm_surface'


    #DSM
    surface_layer = town_name + '_surface_layer'
    surface_return_values = [1, 'FIRST_OF_MANY']
    out_dsm_raster = r"memory\dsm_surface" #town_name + '_building_dsm_surface'
    building_code = [6]

    #NDSM
    in_raster1 = out_dsm_raster
    in_raster2 = out_dtm_raster
    out_ndsm_raster = r"memory\ndsm_buildings" #town_name + '_ndsm_buildings'

    #SLOPE (for later)
    out_slope_raster = os.path.join(cool_roofs_gdb, (town_name + '_slope_buildings'))

    if arcpy.Exists(out_slope_raster):
         return out_slope_raster
    
    else:

        ## DIGITAL TERRAIN MODEL (DTM) ##

        print('dtm layer creation')

        #create a las dataset layer for ground return values (last/last of many), on ground code
        dtm_layer = arcpy.management.MakeLasDatasetLayer(in_las_dataset=las_dataset, 
                                                        out_layer = ground_layer, 
                                                        class_code = ground_code,
                                                        return_values = ground_return_values)

        #convert to raster, of resolution sampling_value (defined at top of script)
        arcpy.conversion.LasDatasetToRaster(in_las_dataset=dtm_layer, 
                                                out_raster=out_dtm_raster, 
                                                value_field='ELEVATION', 
                                                interpolation_type = 'BINNING AVERAGE LINEAR',
                                                sampling_type='CELLSIZE', 
                                                sampling_value=sampling_value)
        
        
        ## DIGITAL SURFACE MODEL (DSM) ##

        print('dsm layer creation')

        #create a las dataset layer for surface return values (first/first of many), only on building code
        dsm_layer = arcpy.management.MakeLasDatasetLayer(in_las_dataset=las_dataset, 
                                                        out_layer = surface_layer, 
                                                        class_code = building_code,
                                                        return_values = surface_return_values)

        #convert to raster, of resolution sampling_value (defined at top of script)
        arcpy.conversion.LasDatasetToRaster(in_las_dataset=dsm_layer, 
                                            out_raster=out_dsm_raster, 
                                            value_field='ELEVATION',
                                            interpolation_type = 'BINNING MAXIMUM NONE',
                                            sampling_type='CELLSIZE', 
                                            sampling_value=sampling_value)
        
      

        

        ## NORMALIZED DIGITAL SURFACE MODEL (NDSM) FROM DSM AND DTM ##

        print('ndsm layer creation')
        # nDSM is the DSM - DTM, so run raster calculator to do so
        # Execute RasterCalculator(Minus) function
        ndsm_raster = RasterCalculator(rasters= [in_raster1, in_raster2], 
                                            input_names = ["x", "y"],
                                            expression="x-y")
        
        ndsm_raster.save(out_ndsm_raster)

        #Delete dsm and dtm 
        arcpy.Delete_management(out_dsm_raster)
        arcpy.Delete_management(out_dtm_raster)

        return out_ndsm_raster

    
def create_slope_raster (town_name, ndsm_raster):
    '''
    Uses an ndsm raster to define the slope of each pixel that covers each roof in the municipality.

    Inputs:
    - town_name (str): Town Name (not case sensitive)
    - ndsm_raster: ndsm raster created in create_ndsm_raster()

    Output:
    - covering each building in the municipality, a raster whose pixels represent the slope over that part of the building

    '''
    env.workspace = cool_roofs_gdb
    #env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    
    out_slope_raster = os.path.join(cool_roofs_gdb, (town_name + '_slope_buildings'))

    if arcpy.Exists(out_slope_raster):
        return out_slope_raster

    else:
        
        #run ArcPy slope function
        slope = Slope(in_raster=ndsm_raster, 
                        output_measurement='PERCENT_RISE',
                        analysis_target_device='GPU_THEN_CPU')

        slope.save(out_slope_raster)
        
        #arcpy.Delete_management(ndsm_raster)

        return out_slope_raster

def create_aspect_raster (town_name, ndsm_raster):
    '''
    Uses an ndsm raster to define the aspect of each pixel that covers each roof in the municipality.

    Inputs:
    - town_name (str): Town Name (not case sensitive)
    - ndsm_raster: ndsm raster created in create_ndsm_raster()

    Output:
    - covering each building in the municipality, a raster whose pixels represent the aspect over that part of the building
    '''
    
    env.workspace = cool_roofs_gdb
    #env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    
    out_aspect_raster = os.path.join(cool_roofs_gdb, (town_name + '_aspect_buildings'))

    if arcpy.Exists(out_aspect_raster):
        return out_aspect_raster

    else:
        #run ArcPy aspect function
        aspect = Aspect(in_raster=ndsm_raster)

        aspect.save(out_aspect_raster)

        return out_aspect_raster


def create_intensity_raster(town_name, las_dataset):
    '''
    Defines the intensity of each pixel that covers each roof in the municipality.

    Inputs:
    - town_name (str): Town Name (not case sensitive)
    - las_dataset: las dataset created in create_las_dataset()

    Output:
    - covering each building in the municipality, a raster whose pixels represent the intensity over that part of the building
    '''
    env.workspace = cool_roofs_gdb
    #env.overwriteOutput = True
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 StatePlane Massachusetts FIPS 2001 (Meters)")
    

    #intensity inputs
    out_intensity_raster = os.path.join(cool_roofs_gdb, (town_name + '_intensity'))
    surface_layer = town_name + '_surface_layer'
    building_code = [6]
    surface_return_values = [1, 'FIRST_OF_MANY']
    

    if arcpy.Exists(out_intensity_raster):
        return out_intensity_raster 

    else:

        # make a las dataset for surface return values over buildings (for future, consider pairing this with DSM?)
        intensity_layer = arcpy.management.MakeLasDatasetLayer(in_las_dataset=las_dataset, 
                                                        out_layer = surface_layer, 
                                                        class_code = building_code,
                                                        return_values = surface_return_values)


        # convert to raster using lidar intensity as the value
        arcpy.conversion.LasDatasetToRaster(in_las_dataset=intensity_layer, 
                                            interpolation_type = 'BINNING AVERAGE NONE',
                                            out_raster=out_intensity_raster, 
                                            value_field='INTENSITY',
                                            sampling_type='CELLSIZE', 
                                            sampling_value=sampling_value)
    
        return intensity_layer