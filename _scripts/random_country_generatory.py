#!/usr/bin/env python3

# random_country_generator.py
# AUTHOR: Tyler W. Davis
# LAST EDITED: 2020-02-03

###############################################################################
# REQUIRED MODULES
###############################################################################
import os.path
import random
import urllib.request


###############################################################################
# FUNCTIONS
###############################################################################
def get_countries():
    '''
    Name:     get_countries
    Inputs:   None.
    Outputs:  list, English names of the countries of the world
    Features: Opens, reads, and returns a list of countries of the world from
              the web.
    '''
    # Open and read URL:
    iso_url = "https://www.iban.com/country-codes"
    fp = urllib.request.urlopen(iso_url)
    my_bytes = fp.read()
    fp.close()

    # Break URL into lines
    my_str = my_bytes.decode("utf8")
    my_lines = my_str.split("\n")

    # Disregard everything before the id="myTable"
    # such that we only have table data elements of our countries
    collecting = False
    my_table_lines = []
    for my_line in my_lines:
        if collecting:
            if "</table>" in my_line:
                collecting = False
            elif my_line.startswith("<td>"):
                my_table_lines.append(
                    my_line.replace("<td>", "").replace("</td>", "")
                )
        elif "myTable" in my_line:
            collecting = True

    # Each row has four columns, remove the other three
    my_countries = []
    for i in range(len(my_table_lines)):
        if i % 4 == 0:
            my_countries.append(my_table_lines[i])

    return(my_countries)


def read_list(ifile):
    '''
    Name:     read_list
    Inputs:   str, input file name (ifile)
    Outputs:  list, country names
    Features: Reads a list of names from text file.
    '''
    if os.path.isfile(ifile):
        my_list = []
        with open(ifile, 'r') as f:
            for line in f:
                line = line.rstrip("\n")
                if line != "":
                    my_list.append(line)
        return(my_list)
    else:
        print("Could not find file %s!" % ifile)
        return []


def write_countries(olist, ofile):
    '''
    Name:     write_countries
    Inputs:   - list, output list (olist)
              - str, output file name (ofile)
    Outputs:  None.
    Features: Writes a list of country names to file.
    '''
    # Create a single string with newlines between each country name:
    my_str = ""
    for my_item in olist:
        my_str = "\n".join([my_str, my_item])

    try:
        with open(ofile, 'w') as f:
            f.write(my_str)
    except:
        raise IOError("Can not write to output file.")

###############################################################################
# MAIN
###############################################################################
# Get countries of the world:
my_country_file = "countries.txt"
if not os.path.isfile(my_country_file):
    countries = get_countries()
    write_countries(countries, my_country_file)
    print("Read %d countries from the web." % len(countries))
else:
    countries = read_list(my_country_file)
    print("Read %d countries from file." % len(countries))

# Get student file:
my_student_file = "students.txt"
students = read_list(my_student_file)

# Find USA and remove it from options:
i_usa = None
for country in countries:
    if "United States of America" in country:
        i_usa = countries.index(country)
if i_usa is not None:
    countries.pop(i_usa)

# Give every student/team k random countries and the USA
st_dict = {}
randc = None
kcountries = 3
for my_st in students:
    randc = random.sample(countries, k=kcountries)
    st_dict[my_st] = list()
    for c in randc:
        st_dict[my_st].append(c)
    st_dict[my_st].append("United States of America")
    # Remove selected countries from options:
    for country in randc:
        i_country = countries.index(country)
        countries.pop(i_country)

# Print the results
for key, value in st_dict.items():
    # Initial output string with group name
    my_str = "%s:\n" % (key)
    i = 1
    for myval in value:
        # Enumerates each country in the list
        my_str = "".join([my_str, "\t", str(i), ". ", myval, "\n"])
        i += 1
    print(my_str)
