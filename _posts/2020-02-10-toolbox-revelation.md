---
title: "Toolbox Revelation"
---
This week in advanced GIS, I wrapped up my first draft of a working ArcGIS Toolbox for the CGA's Middle Earth class.
The class tutorial relied on a toolbox that was created several years ago using `arcgisscripting`, which had suddenly and unexpectedly stopped working.
I took upon the challenge of upgrading `arcgisscripting` to `arcpy` for ArcGIS Pro as I debugged the code.

The first setback was testing the code, because the workflow for a toolbox is not clearly defined anywhere.
Therefore, I started just as I would any project with a basic script separated into functions, classes, and the `if __name__ is "__main__"` block at the bottom.

While I found a method for hacking into ArcGIS Pro's python environment, on my laptop, I am already hacking into OSGEO4W's (QGIS) python, so I'm a little frustrated with switching back-and-forth between the two for the ease of command-line use (I tried virtual environments, but it doesn't like the PYTHON_PATH environment variable linking to OSGEO4W).

Having tested a good portion of the python script via importing the class on ArcGIS Pro's python command line and running through the methods with the typical debugging, I approached the "all-in" moment to go to the toolbox PYT script (you literally just change the file extension from .py to .pyt), but now as a toolbox, you gain access to drop-down menus and the progress bar (secret messages!).
As I loaded the PYT into Python as a new toolbox, I was having to wait 5--10 minutes before the toolbox became available and I kept getting this RUNTIME ERROR message before I finally realized that that stinking `if __name__ is "__main__"` is actually running when the toolbox is loaded!
So I removed it and now the toolbox loads super quick.
There is still the lingering problem where I create dependencies on folder location in the tool class's init, which also, interestingly, is called when the toolbox is imported and has created errors when sharing a toolbox in a folder that moves from one computer to another as the absolute paths change.

This, to be addressed at another time.

### Jekyll Updates
The navigation bar still haunts me.
I was able to get a CSS style that makes the navigation bar stay at the top of the screen, but I can't seem to make it responsive to screen width.
Sorry to those of you looking at this website on mobile devices.
I also found a way to create an ordered navigation using a sort by navigation_weight variable that I added to each page's YAML header.

This can be considered a positive development.
