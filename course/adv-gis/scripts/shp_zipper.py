#!/usr/bin/env python3
#
# shp_zipper.py
#
# VERSION 0.1
#
# AUTHOR: Tyler W. Davis, CGA, W&M
#
# LAST UPDATED: 2020-03-18
#
# Use this script to create zipped shapefiles (e.g., to upload to AGOL).
#
###############################################################################
# REQUIRED MODULES
###############################################################################
import argparse
import os
import os.path
import zipfile


###############################################################################
# FUNCTIONS
###############################################################################
def find_files():
    """
    Name:     find_files
    Inputs:   None.
    Outputs:  dictionary, file prefixes with associated file extensions
    Features: Searches base directory for shape files
    """
    # Initialize empty list and dictionary of files
    files_dict = {}

    # Shapefile file extensions
    # http://webhelp.esri.com/arcgiSDEsktop/9.2/index.cfm?TopicName=Shapefile_file_extensions
    shp_exts = [
        ".shp", # required
        ".shx", # required
        ".dbf", # required
        ".sbn", ".sbx", ".fbn", ".fbx", ".ain", ".aih",
        ".atx", ".ixs", ".mxs", ".prj", ".xml", ".cpg"
    ]

    # Read all files in current directory, filter by extension,
    # and save all file extensions associated for each file prefix;
    # we'll use this later to filter valid shapefiles from random XMLs
    # NOTE: assumes compound file extensions of max length = 2
    #       and will fail for the strange occurrence of .shp.aux.xml
    for f in os.listdir("."):
        if os.path.isfile(f):
            f_name, f_ext = os.path.splitext(f)
            if f_ext in shp_exts:
                # Check for compound file extensions (e.g., .shp.xml)
                # !!! could be made recursive until splitext[1] = ''
                cf_name, cf_ext = os.path.splitext(f_name)
                cf_ext = "".join([cf_ext, f_ext])

                if cf_name in files_dict.keys():
                    files_dict[cf_name].append(cf_ext)
                else:
                    files_dict[cf_name] = [cf_ext,]

    # Filter invalid shapefiles:
    for fname, fexts in files_dict.items():
        # This effectively checks that all three required file extensions
        # are associated with a given file:
        if not all([h in fexts for h in ['.shp', '.shx', '.dbf']]):
            files_dict[fname] = None

    return(files_dict)


def zip_shapes(to_clean=False):
    """
    Name:     zip_shapes
    Inputs:   (optional) bool, delete original files after zip (to_clean)
    Outputs:  None
    Features: Compresses shapefiles found in the local directory into .zip
    Depends:  find_files
    """
    # Find all valid shapefiles in local directory;
    # NOTE: dict vals of type None should be skipped
    shape_dict = find_files()

    for k,v in shape_dict.items():
        if v is not None and isinstance(v, list):
            # Open a zipfile for writing
            zip_name = "".join([k, ".zip"])
            my_zip = zipfile.ZipFile(zip_name, 'w')

            print("> zipping %s" % zip_name)
            # Go through file dictionary and re-create file names
            # add files to zip and clean up, if requested
            for val in v:
                f_name = "".join([k, val])
                if os.path.isfile(f_name):
                    my_zip.write(f_name)
                    if to_clean:
                        os.remove(f_name)
            my_zip.close()
    print("Done!")


###############################################################################
# MAIN
###############################################################################
if __name__ == '__main__':
    # Create an ArgumentParser class object for dealing with commandline args
    my_descr = (
        "Compresses shapefiles found in the local directory into .zip format."
        " Pass -c to delete orginal files after they are added to zip.")
    p = argparse.ArgumentParser(description=my_descr)
    p.add_argument("-c", "--clean", action="store_true",
                   help="delete original files after zipping")

    # Read any command line arguements sent to the program
    # NOTE: if -h or --help, the program stops here
    args = p.parse_args()
    zip_shapes(to_clean=args.clean)
