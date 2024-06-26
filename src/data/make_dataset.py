# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
#from dotenv import find_dotenv, load_dotenv
import geopandas as gpd
import pandas as pd
import os


datasets_dir = r'K:\DataServices\datasets'
projects_dir = 'K:\\DataServices\\projects\\Current_Projects' 
input_dir = r"C:\Users\rbowers\Desktop\Data_Cool_Roofs\0_Input"
intermediate_path = r"C:\Users\rbowers\Desktop\Data_Cool_Roofs\1_Intermediate"
output_dir = r"C:\Users\rbowers\Desktop\Data_Cool_Roofs\2_Output"

las_folder = r'I:\Imagery\MassGIS_LAS_files'

mass_mainland_crs = "EPSG:26986"

cool_roofs_project_dir = r'K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP'
#cool_roofs_gdb = os.path.join(cool_roofs_project_dir, 'ArcGIS\CoolRoofs_Analysis.gdb')
cool_roofs_gdb = r'C:\Users\rbowers\Desktop\cool_roof_analysis_offnetwork.gdb'

mmc_munis = ['Arlington', 'Boston', 'Braintree', 'Brookline', 'Cambridge', 'Chelsea', 
             'Everett', 'Malden', 'Medford', 'Melrose', 'Newton', 'Quincy', 
             'Revere', 'Somerville', 'Watertown', 'Winthrop']

#building structures
#building_structures_gdb = os.path.join(datasets_dir, 'MassGIS\Facilities_Structures\Building_Structures\Output\structures.gdb')
building_structures_fp = os.path.join(input_dir, 'structures.gdb\STRUCTURES_POLY')
building_structures_layer = 'STRUCTURES_POLY'

#massgis_footprints = r'K:\DataServices\Datasets\MassGIS\Facilities_Structures\Building_Structures\Output\structures.gdb\STRUCTURES_POLY'

#lookup tables
#land_use_lookup_fp = r"K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP\Data\lookup_tables\land_use_lookup.csv"
#real_estate_lookup_fp = r"K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP\Data\lookup_tables\real_estate_type_lookup.csv"
#real_estate_lookup_codes_fp = r"K:\DataServices\Projects\Current_Projects\Climate_Change\MVP_MMC_CoolRoofs_MVP\Data\lookup_tables\real_estate_lookup.csv"

land_use_lookup_fp = os.path.join(input_dir, 'land_use_lookup.csv')
real_estate_lookup_fp = os.path.join(input_dir, 'real_estate_type_lookup.csv')
real_estate_lookup_codes_fp = os.path.join(input_dir, 'real_estate_lookup.csv')

land_use_lookup = pd.read_csv(land_use_lookup_fp)
real_estate_lookup = pd.read_csv(real_estate_lookup_fp)
real_estate_lookup_code = pd.read_csv(real_estate_lookup_codes_fp)

#where to export charts
chart_fp = "K:\\DataServices\\Projects\\Current_Projects\\Climate_Change\\MVP_MMC_CoolRoofs_MVP\Charts"

#mapc blocks
#mapc_blocks_fp = 'K:\\DataServices\\Projects\\Current_Projects\\Environment\\MS4\\Project\\MS4_Model.gdb'
#mapc_blocks = gpd.read_file(mapc_blocks_fp, layer='mapc_2020_blocks')
mapc_blocks_fp = os.path.join(input_dir, 'mapc_2020_blocks.shp')
mapc_blocks = gpd.read_file(mapc_blocks_fp)


#municipalities
#munis_fp = os.path.join(datasets_dir, "Boundaries\Spatial\mapc_towns_poly.shp")
munis_fp = os.path.join(input_dir, 'TOWNSSURVEY_POLY.shp')
munis=gpd.read_file(munis_fp)
muni_field = 'TOWN'

#environmental justice (2020 boundaries, updated in 2023)
ej_2020_gdb = os.path.join(input_dir, 'ej2020.gdb')
ej_2020 = gpd.read_file(ej_2020_gdb, layer='EJ_POLY')
ej_field = 'EJ_CRIT_DESC'

#heat
heat_fp = os.path.join(input_dir, 'LSTindex.tif')

mapc_lpd_folder = os.path.join(input_dir, 'parcels_by_muni')


#mmc_heat_export_path = os.path.join(intermediate_path, 'mmc_blocks_heat.shp')
mmc_heat_export_path = os.path.join(intermediate_path, 'mmc_blocks_heat.shp')
mmc_heat_blocks = gpd.read_file(mmc_heat_export_path)

#all town parcels are read in from MassGIS, except Boston. Do a manual download and replace here:
boston_parcels_fp = os.path.join(input_dir, 'Parcels_(2024)\Parcels_(2024).shp')
boston_parcels = gpd.read_file(boston_parcels_fp)

