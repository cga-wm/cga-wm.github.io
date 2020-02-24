## A Case Study
#### 2020-02-24

This week, we take a look at how far we've gotten towards modeling our landslide susceptibility.
Here's what's been done so far.

1. Decide on a town or city.
    - For this case study, I chose Collbran, Colorado because it was listed as having the largest landslide in Colorado (cite Wikipedia article).
1. Decide on a CRS
    - I have chosen NAD83 UTM 13N because the datum matches the DEM data I found (see next point) and is also recommended by CDOT (missing link)

1. Download digital elevation data (e.g., [The National Map](https://viewer.nationalmap.gov/basic/))
    - I had to download two tiles n40w108 and n40w109 because my town is located near the tile intersection

    ![](images/2020-02-24_dem.png)
1. Project raster(s)
1. Add city to the map by creating a plain text file (e.g., point.txt), creating an XY Point table (such as the one below), and importing to GIS

    ```
    ID,LAT,LON,CITY,STATE
    0,39.240016,-107.963956,Collbran,CO
    ```

    ![](images/2020-02-24_dem_dot.png)
1. Project point
1. Extract DEM by mask (e.g., buffer or poly)
    - Chose to create a 10 km buffer around my town because the town limits was pretty small and a 10 km buffer area is less than 100,000 acres---the maximum area for downloading a web soil survey spatial map
    - Note: I had to use Cell Statistics to knit together two DEM tiles after mask extraction; I chose to knit after extraction because the files are smaller and processing time would be faster.

    ![](images/2020-02-24_dem_buff.png)
1. Calculate slope

    ![](images/2020-02-24_slope.png)
1. Download soil data (e.g., [Soil Web Survey](https://websoilsurvey.sc.egov.usda.gov/App/HomePage.htm))
    - To get my Area of Interest (AOI), I exported the buffer to a shape file and used the shapefile to set my AOI

    ![](images/2020-02-24_soils.png)
1. Figure out what the soil survey is actually saying
    - Data is from the Digital General Soil Map of the United States (STATSGO2) database (see Tables and Columns report found [here](https://www.nrcs.usda.gov/wps/portal/nrcs/detail/soils/survey/geo/?cid=nrcs142p2_053631)) and uses a map unit key (MUKEY) and map unit symbol (MUSYM) to relate the shapefile's attribute table to soil information (presumably in the tabular files)
    - Files of interest:
        - comp.txt (link between mapunit key and component key)
        - chorizon.txt (link between component key and horizon key)
        - chunifie.txt (link between horizon key and horizon unified classification)
        - muagatt.txt (link between map unit symbol and minimum bedrock depth, cm)
    - I need to build a table that matches map unit key --> component key --> horizon key --> unified classification --> angle of friction/cohesion
    - First attempt at adding ASCII table to ArcGIS Pro failed (everything dumped into a single field; so, it doesn't seem to recognize the pipe character "\|" as a delimiter)

**Current Challenges**

* Create a table/link between map units (in the attribute table) to unified soil classification (in chunifie.txt)
* Create a table of unified soil classification and soil cohesion and angle of friction (_which values to choose and why_)
* Create a table/link between map symbols and minimum bedrock depth (cm) found in muagatt.txt
