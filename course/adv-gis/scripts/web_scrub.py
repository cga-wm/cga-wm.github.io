#!/usr/bin/env python3
#
# web_scrub.py
#
# VERSION 1.0
# AUTHOR: Tyler W. Davis, CGA, William & Mary
# LAST EDIT: 2020-06-24
#
# This script reads polling station attribute data from a government website
# for the purposes of geospatial analysis.
#
# This script uses third-party packages including the following:
#     bs4 v.4.8.2 (https://www.crummy.com/software/BeautifulSoup/)
# To install these on your machine, either read the docs or try the following:
#     pip install beautifulsoup4
#
##############################################################################
# REQUIRED MODULES
##############################################################################
import os.path
import re
import urllib.request

from bs4 import BeautifulSoup

##############################################################################
# FUNCTIONS
##############################################################################
def find_address(addr_tag):
    """
    Name:     find_address
    Inputs:   bs4.element.Tag, address tag (addr_tag)
    Outputs:  list, street, city, state, zip
    Features: Returns street, city, state, zip from address tag
    TODO:     - need to allow: 117-1A North Public Square
              - need to allow: 102 Richmond Road, Suite 101 OR Room 1
              - need to allow: 20 Main Street, 1st floor
              - need to allow: 30 Hwy 42E
              - need to allow: no street number
              - need to allow: missing zip code
    """
    # Initialize empty list
    my_out = []

    # Remove all inner tags (strong and br):
    for line_br in addr_tag.find_all("br"):
        line_br.extract()
    for line_strong in addr_tag.find_all("strong"):
        line_strong.extract()
    # Use regular expressions to parse street, city, state, zip
    # TODO: write second regex for no zip
    my_regex = re.compile('([\d+ ]?[^<>,]+[, ]?.*)\n ([^,]+), ([A-Z]{2}) (\d{5})')
    m = my_regex.search(
        addr_tag.prettify().lstrip("<address>").rstrip("</address>").strip()
    )
    if m:
        addr_street = m.group(1)
        addr_city = m.group(2)
        addr_state = m.group(3)
        try:
            addr_zip = m.group(4)
        except IndexError:
            addr_zip = "N/A"
        my_out = [addr_street, addr_city, addr_state, addr_zip]
    else:
        my_regex_nozip = re.compile('([\d+ ]?[^<>,]+[, ]?.*)\n ([^,]+), ([A-Z]{2})')
        n = my_regex_nozip.search(
            addr_tag.prettify().lstrip("<address>").rstrip("</address>").strip()
        )
        if n:
            addr_street = n.group(1)
            addr_city = n.group(2)
            addr_state = n.group(3)
            addr_zip = "N/A"
            my_out = [addr_street, addr_city, addr_state, addr_zip]

    return my_out


def writeline(f, d):
    """
    Name:     writeline
    Input:    - str, file name with path (f)
              - str, data to be written to file (d)
    Output:   None
    Features: Appends an existing file with data string
    """
    try:
        with open(f, 'a') as my_file:
            my_file.write(d)
    except:
        raise IOError("Can not write to output file.")


def writeout(f, d):
    """
    Name:     writeout
    Input:    - str, file name with path (f)
              - str, data to be written to file (d)
    Output:   None
    Features: Writes new/overwrites existing file with data string
    """
    try:
        with open(f, 'w') as my_file:
            my_file.write(d)
    except:
        raise IOError("Can not write to output file.")


##############################################################################
# MAIN
##############################################################################
if __name__ == '__main__':
    # Of interest is the Kentucky Elections Polling Locations website:
    web_addr = "https://www.sos.ky.gov/elections/Pages/Polling-Locations.aspx"

    # HTTP is based on requests and responses
    # Let's first request the website's content from their server:
    req = urllib.request.Request(web_addr)

    # Now, let's read the page in the site's response:
    # Note that this is the same as viewing a page's source
    with urllib.request.urlopen(req) as response:
        web_page = response.read()
    soup = BeautifulSoup(web_page, "html.parser")
    print(soup)

    # First thing, we notice that none of the polling results are in the
    # source HTML... :(

    # Why?!

    # Well, it looks like the site uses an ASPX file rather than HTML or PHP
    # and employs AJAX (asynchronous Javascript and XML); so the web content
    # is dynamically created using scripts. The result is an awesome site
    # design, but not great for this purpose.

    # So, what now?

    # Let's go back to the website and use the inspector.
    # https://www.lifewire.com/get-inspect-element-tool-for-browser-756549

    # Once all the Javascript has finished loading, we can see the HTML tree
    # nicely organized in such a way as to simply "scrub" what we want from it;
    # unfortunately, it does not appear accessbile via HTTP requests, so let's
    # just copy-and-paste it.

    # Find the tag called <div id="polling">, right-click it and select
    # Copy --> Inner HTML (Firefox) or Copy element (Chrome) and paste it
    # into a plain text document called "ky_polling_2020.txt"

    # Save the directory location where your file is located and its filename:
    my_dir = r"C:\Workspace\AdvGIS"
    my_doc = "ky_polling_firefox.txt"
    my_path = os.path.join(my_dir, my_doc)

    # Before we begin parsing the web content, let's set up the output file.
    my_out = "ky_polling_parsed.csv"
    out_path = os.path.join(my_dir, my_out)

    # Create a headerline and save to a new file:
    # (see below for attribute definitions)
    header_items = ["County", "Type", "Name", "Street", "City",
                    "State", "Zip", "Time", "Lon", "Lat"]
    my_head = "\t".join(header_items)
    my_head += "\n"
    writeout(out_path, my_head)

    web_data = ''
    if os.path.isfile(my_path):
        with open(my_path) as f:
            web_data = f.read()

    # Remove the trailing newline character and pass the text to bs
    web_data = web_data.strip()
    soup = BeautifulSoup(web_data, "html.parser")

    # Notice that the HTML tags have a div with class attribute "location"
    # for each polling station location.

    # Let's start by finding all locations.
    loc_data = soup.find_all("div", {"class": "location"})
    if len(loc_data) > 0:
        for my_loc in loc_data:
            # Note that there are absentee locations and June 23 locations.
            # First, initialize the variables (attributes) we want to save
            my_county = ""   # County for polling station
            my_type = ""     # Used to distinguish absentee from June 23
            my_name = ""     # Name of polling station
            my_street = ""   # Street address of polling station
            my_city = ""     # City of polling station
            my_state = "KY"  # State of polling station (should always be KY)
            my_zip = ""      # Zip code of polling station
            my_time = ""     # Absentee location hours (N/A for June polling)
            my_lon = "N/A"   # Polling location longitude (georef'ed)
            my_lat = "N/A"   # Polling location latitude (georef'ed)

            # Extract county from tag attribute:
            my_county = my_loc.get("data-county")

            # ~~~~~~~~~~~~~ ABSENTEE LOCATION ~~~~~~~~~~~~~
            # Absentee locations are in the div class "row"
            my_type = "In-person Absentee Location"
            my_absentees = my_loc.find_all("div", {"class": "row"})
            for my_absentee in my_absentees:
                my_name = my_absentee.find("strong").decode_contents()
                my_time = my_absentee.find("p").decode_contents()
                my_abs_addr = my_absentee.find("address")
                my_abs_scsz = find_address(my_abs_addr)
                if len(my_abs_scsz) == 4:
                    my_street = my_abs_scsz[0]
                    my_city = my_abs_scsz[1]
                    my_state = my_abs_scsz[2]
                    my_zip = my_abs_scsz[3]
                else:
                    print("Failed to find address for %s" % (my_name))
                    my_street = "N/A"
                    my_city = "N/A"
                    my_state = "KY"
                    my_zip = "N/A"

                # Write line to file:
                my_parts = [my_county, my_type, my_name, my_street, my_city,
                            my_state, my_zip, my_time, my_lon, my_lat]
                my_line = "\t".join(my_parts)
                my_line += "\n"
                writeline(out_path, my_line)

                # Extract this tag
                my_absentee.extract()

            # ~~~~~~~~~~~~~ 23 JUNE LOCATION ~~~~~~~~~~~~~
            # Note that some locations have multiple polling addresses
            my_type = "June 23 Polling Location(s)"
            my_time = "N/A"  # Absentee location hours; N/A for June polling
            my_addrs = my_loc.find_all("address")
            for my_addr in my_addrs:
                # Extract the name from the strong tag
                my_name = my_addr.find("strong").decode_contents()
                my_scsz = find_address(my_addr)
                if len(my_scsz) == 4:
                    my_street = my_scsz[0]
                    my_city = my_scsz[1]
                    my_state = my_scsz[2]
                    my_zip = my_scsz[3]
                else:
                    print("Failed to find address for %s" % (my_name))
                    my_street = "N/A"
                    my_city = "N/A"
                    my_state = "KY"
                    my_zip = "N/A"

                # Write line to file:
                my_parts = [my_county, my_type, my_name, my_street, my_city,
                            my_state, my_zip, my_time, my_lon, my_lat]
                my_line = "\t".join(my_parts)
                my_line += "\n"
                writeline(out_path, my_line)
    else:
        print("Found no location class div elements!")
