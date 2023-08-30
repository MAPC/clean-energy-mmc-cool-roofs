# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
#from dotenv import find_dotenv, load_dotenv
import geopandas as gpd




ms4_parcels_folder = r'K:\DataServices\Projects\Current_Projects\Environment\MS4\Data\Spatial\Output\Parcels'

mmc_munis = ['Arlington', 'Boston', 'Braintree', 'Brookline', 'Cambridge', 'Chelsea', 
             'Everett', 'Malden', 'Medford', 'Melrose', 'Newton', 'Quincy', 
             'Revere', 'Somerville', 'Watertown', 'Winthrop']

#building structures
building_structures_gdb = 'K:\\DataServices\\Datasets\\MassGIS\\Facilities_Structures\\Building_Structures\\Output\\structures.gdb'
building_structures_layer = 'STRUCTURES_POLY'

'''
@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
'''