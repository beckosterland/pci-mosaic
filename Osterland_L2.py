## Course:     REMS 6023 Lab 2
## Author:     Beck Osterland
## Date:       January 27, 2022

## Purpose:    Python script to automate Landsat image corrections and mosaicking in PCI.
## AOI:        The Landsat 8 data attached with this script covers a section of the Himalayas
##             3 Landsat scenes cover the entire country of Bhutan.

## Disclaimer: This assignment and script is for educational purposes only.

print("Starting PCI Mosaic Python Script")

# import necessary Python modules
import pci
import os
import fnmatch
import shutil
import calendar, time

from pci.hazerem import *
from pci.exceptions import *
from pci.atcor import *
from pci.pcimod import pcimod
from pci.reproj import *
from pci.mosprep import mosprep
from pci.mosdef import mosdef
from pci.mosrun import mosrun
from pci.fexport import fexport

# Begin runtime clock using calendar module
start_time = calendar.timegm(time.gmtime())


# specify the Working directory
# switch to C-drive
working_dir = r"C:\Osterland_L2"
print("Working directory is: " + working_dir)

# specify output directory
output_dir = os.path.join(working_dir, 'outputs')

# test if output directory is already exists
# if true, delete it and make fresh one to allow reproduceability
# uses mkdir module from os to make new folder (directory)

if os.path.exists(output_dir):
# remove directory    
    shutil.rmtree(output_dir)
    print("Previous directory removed")	

# make new empty directory
os.mkdir(output_dir)
print("New output directory created")


# create sub folders in output directory
folder_names = ["haze","atcor","mosaic"]

#for loop to make new subfolders for each output step
for folder in folder_names:
    
    sub_folder = os.path.join(output_dir, folder)
    if os.path.exists(sub_folder):
# remove directory    
        shutil.rmtree(sub_folder)
        print("Previous sub-folder removed")	

# make new empty sub-folder
    os.mkdir(sub_folder)
    print("New " + folder + " subfolder created")

# Define output folders for future placement    
haze_folder = os.path.join(output_dir, "haze")
atcor_folder = os.path.join(output_dir, "atcor")
mosaic_folder = os.path.join(output_dir, "mosaic")


# create empty list to store MTL files
input_files = []

# for loop that collects all files with the MTL.txt extension 
# within LandsatImagery folder using fnmatch module
for r, d, f in os.walk(working_dir):
	for inFile in fnmatch.filter(f,'*_MTL.txt'):
		input_files.append(os.path.join(r, inFile))

#Print list count and names to make sure all files were gathered
print(str(len(input_files)) + " Landsat scenes collected")
print(input_files)





# Specify channels to delete throughout for loop
# In this case we want to keep Landsat 8 OLI bands 2(blue),3(green),5(NIR)
channels = [1,4,6,7,8]



# Iterate through list of files performing PCI modules

for image in input_files:

# Perform Haze removal using hazerem module from PCI
# Specify input as the iteration of the loop that calls file path
# Use join by '-' to add MS extension to the file name    
    try:
        hazerem(fili='-'.join([image, 'MS']),
        filo=os.path.join(haze_folder, '_HAZE.'.join([os.path.basename(image).split('_MTL')[0], 'pix'])))
        print("Haze removal complete for " + image)
    
    except:
        print("Error: Haze removal failed")


#Assign path for hazerem file for next step
    hazerem_file = os.path.join(haze_folder, '_HAZE.'.join([os.path.basename(image).split('_MTL')[0], 'pix']))

    try:
        atcor(fili=hazerem_file,
            filo=os.path.join(atcor_folder, '_ATMOSC.'.join([os.path.basename(image).split('_MTL')[0], 'pix'])))
        print("Atmospheric correction complete for " + image)
    except:
        print("Error: atmospheric correction failed")


# Assign path for atcor file for next step
    atcor_file = os.path.join(atcor_folder, '_ATMOSC.'.join([os.path.basename(image).split('_MTL')[0], 'pix']))

# Delete unwanted channels (bands) using pcimod module
# To change band to keep, modify "channels" list to include bands to delete
    try:
        pcimod(file=atcor_file, pciop="DEL", pcival=channels)
        print("5 bands removed from " + image)

    except:
        print("Error: band trimming")


# End of for loop
print("Haze removal and Atmospheric correction Complete...")

# After corrections for each scene (tile), time to perform mosaic

# Specify mosprep project file output
mosprep_proj = os.path.join(mosaic_folder, "mosaic_prj.mos")

# Run mosprep module, files located in atcor folder       
mosprep(mfile=atcor_folder, silfile = mosprep_proj)

# Specify mosdef XML file output
mosdef_file = os.path.join(mosaic_folder, "mosdef.xml")

# Run mosdef module
mosdef(silfile = mosprep_proj, mdfile = mosdef_file, dbic=[3,2,1])

#Speficy location of mosaic file
final_mosaic = os.path.join(mosaic_folder, "mosaic_output")
os.mkdir(final_mosaic)

#Run mosrun
mosrun(silfile = mosprep_proj, mdfile = mosdef_file, outdir = final_mosaic)


# Export cutlines vector layer to ESRI Shapefile
try:
    fexport(fili=os.path.join(mosaic_folder, "mosaic_prj\misc\mosaic_prj_cutline_topology.pix"),
     filo=os.path.join(final_mosaic, "cutlines.shp"), dbvs=[2], ftype="shp")
    print("Cutlines successfully exported as Shapefile")
except:
    print("Cutlines export failed")


# Stop runtime clock
end_time=calendar.timegm(time.gmtime())

# Calculate runtime
process_time = end_time - start_time

print("Total Processing Time: " + str(process_time) + " seconds.")
print("End of Script")
