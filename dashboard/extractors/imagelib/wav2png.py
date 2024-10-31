#!/usr/bin/env python

#
# Freesound is (c) MUSIC TECHNOLOGY GROUP, UNIVERSITAT POMPEU FABRA
#
# Freesound is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Freesound is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     See AUTHORS file.
#
# 03/10/2013: Modified from original code 

from .processing import create_wave_images, AudioProcessingException
import sys

def progress_callback(percentage):
    sys.stdout.write(str(percentage) + "% ")
    sys.stdout.flush()
   
    # process all files so the user can use wildcards like *.wav
    
def genimages(input_file,output_file_w, output_file_s, options):
    args = (input_file, output_file_w, output_file_s, options.image_width, options.image_height, options.fft_size, progress_callback)
    print("processing file %s:\n\t" % input_file)
    try:
        create_wave_images(*args)
    except AudioProcessingException as e:
        print("Error running wav2png: ", e)
        