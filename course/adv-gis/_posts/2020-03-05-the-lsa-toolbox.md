## The Landslide Analysis Toolbox
#### 2020-03-05

The first approach to creating the toolbox is to get all the data, layers, and processes together and in the right order.
To approach this, I started on the Python interpreter in ArcGIS.

In my ArcGIS Pro project folder, I created a `\Scripts` directory and made a blank plain text file (`crit_rain_thresh.py`) where I copy over working code.

A nice thing about ArcGIS is that it creates a file (`.pyHistory`) in the project folder that contains all the executed commands you type on the Python interpreter.
While testing, I can just copy-and-paste the good stuff from here to my script file.

Here's the [Python script (.py)](scripts/crit_rain_thresh.py) I ended up with after testing.

The next step is converting the procedure from script to Toolbox, which means creating classes---one for the toolbox and one for each tool inside the toolbox.

Esri has published [The Python toolbox template](https://pro.arcgis.com/en/pro-app/arcpy/geoprocessing_and_python/a-template-for-python-toolboxes.htm), which sets up the framework for the toolbox and geoprocessing tool.
In this example, I only need one tool (Critical Rainfall Threshold Model) in my Toolbox (Landslide Analysis) with six parameters:

1. Hillslope raster (deg)
1. Soil internal friction angle raster (deg)
1. Soil cohesion raster (Pa)
1. Depth of regolith raster (m)
1. Depth of soil moisture value (m)
1. Output factor of safety (Fs) raster

I did not give the user the ability to change &gamma;<sub>r</sub> or &gamma;<sub>w</sub>, but it could be added later.

Here's the [Python Toolbox (.pyt)](scripts/lsa.pyt) I ended up with.

To get the toolbox in ArcGIS Pro, open your project file and, in the Catalog pane, right-click on Toolboxes and click "Add Toolbox" (note: __not__ New Python Toolbox; the toolbox is already created!).
The tool ran in something like five seconds, which was a little disappointing because I took time to write progress labels (the progress bar you see after you click "Run") that are quickly passed over.
On the upside, the tool runs in five seconds!

The output Fs raster is not filtered for values.
For landslide susceptibility, we are interested in values between 0 and 1.
Arguably, values of 1.25 and 1.5 could also be of interest.

There are some NODATA values that crop up in the output raster, which seem to be related to pixels where Fw > Fc + Ff.
My guess is that I don't take into consideration water depth greater than regolith depth and it may be an artifact of bad coding.

Regardless, it was four and a half hours well spent.
