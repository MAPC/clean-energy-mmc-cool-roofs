
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