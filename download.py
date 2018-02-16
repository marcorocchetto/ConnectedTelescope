'''

Download frames

The input to the script is a json file with the following format. See input_examples

Example:

python /home/telescope/TelescopeConnect/download.py --json=/home/telescope/TelescopeConnect/input_examples/download_files.json

'''

import argparse
from astropy.io import fits
import sys
import numpy as np
from time import strftime
import os
import zipfile, random, string
import shutil


import library.general
from library.general import *

#loading parameter file parser
parser = argparse.ArgumentParser()
parser.add_argument('--json',
                    dest='json_filename',
                    type=str,
                    default=False,
                    )

options = parser.parse_args()

if not options.json_filename:
    RaiseError('You need an inpunt JSON file')

json_data = json.loads(open(options.json_filename).read())

# read all files from list
# images = []
# for image_fname in json_data['input_fits']:
#     images.append(get_ImageData(image_fname))

# TEMPORARY. THIS DOES NOT DO ANYTHING, JUST COMPRESS ALL FILES INTO SINGLE ZIP
random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

# create directory for files to be compressed
zip_directory = os.path.abspath(os.path.join(json_data['output_folder'], random_string))
if not os.path.exists(zip_directory):
    os.makedirs(zip_directory)

for image_fname in json_data['input_fits']:

    # set filename
    hdulist = fits.open(image_fname)
    header = hdulist[0].header

    # Date and time of observation: keyword DATE-OBS
    dateobs_utc_str, dateobs_utc_datetime = get_DateObs(header['DATE-OBS'])
    filename = dateobs_utc_datetime.strftime('%Y-%m-%dT%H-%M-%S')

    # determine Image type from header IMAGETYP
    imagetype = get_ImageType(header['IMAGETYP'])
    if imagetype == 'LIGHT':
        if 'OBJECT' in header:
            filename += '-' + header['OBJECT']
        filename += header['FILTER']
    if imagetype == 'BIAS':
        filename += '-Bias'
    if imagetype == 'DARK':
        filename += '-Dark'
    if imagetype == 'FLAT':
        filename += '-Flat'
        filename += header['FILTER']
    filename = filename.replace(' ', '_')
    filename_fits = filename + '.fits'

    # copy file to archive directory
    shutil.copy(image_fname, zip_directory)

output_filename = random_string + '.zip'

shutil.make_archive(os.path.join(json_data['output_folder'], random_string), 'zip', zip_directory)

shutil.rmtree(zip_directory)

print(json.dumps({'result': 'SUCCESS',
                  'output_file': os.path.abspath(os.path.join(json_data['output_folder'], output_filename))},
                 separators=(',', ':'), indent=4))
sys.exit()
