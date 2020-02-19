#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# myspi.pyt
#
# Tyler W. Davis, CGA, William & Mary, Williamsburg, VA
#
# VERSION:   2.0
# LAST EDIT: 2020-02-11
#
# This script is based on "summedPointInfluence" by Fisher & Didier (2013)
# to calculate an index of influence intensity (e.g., hunting) from multiple
# features (e.g., villages) using a cost surface (e.g., travel time), which
# is based loosely on original AML by Gosia Bryja (gbrya@wcs.org) and Karl
# Didier # (kdidier@wcs.org).
#
# -----
# SETUP
# -----
# 1. Create an ArcGIS Pro project (e.g., C:\Workspace\SPI\Spi.aprx)
# 2. Create a Data directory (e.g., C:\Workspace\SPI\Data) in which you should
#    have a feature class ("Populated_places.shp") and a cost raster
#    ("cost_distance.tiff").
# 3. Create a Scripts directory (e.g., C:\Workspace\SPI\Scripts) in which you
#    should copy this script.
# 4. Right-click on Toolboxes in the Catalog and select "Add New Toolbox"
# 5. Open CGA SPI Tool, make IO selections, run, and enjoy
#
# -----
# TODO
# -----
# 1. implement the max distance threshold
# 1. deal with update parameters function and handling
#
##############################################################################
# REQUIRED MODULES
##############################################################################
import os
import re

import arcpy


##############################################################################
# CLASSES
##############################################################################
class Toolbox(object):
    """
    This class is needed for importing as an ArcGIS toolbox.
    """
    def __init__(self):
        self.label = "SPI toolbox"
        self.alias = "SPI"
        self.tools = [MYARCPYSPI]


class MYARCPYSPI(object):
    """
    Name:     MYARCPYSPI
    Features: Class for handling the SPI work for Rob's Middlearth class
    History:  Version 2.0
              - abandon command line; going all in on toolbox [20.02.11]
              - add SPI raster to current map
              !!! NOTE: 'if name is main' will run tool during import to ArcPro
              Version 1.1
              - add progress messages [20.02.11]
              - add parameter maker functions [20.02.11]
              - fix issues with project and map references [20.02.11]
              Version 1.0
              - update for arcgis toolbox [20.02.10]
              Version 0.1
              - converting arcgisscripting to arcpy [20.02.06]
    """
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Initialization
    # ////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
        Name:     MYARCPYSPI.__init__
        Features: Class initialization function for arcpy
        """
        # Setup ArcGIS Toolbox requirements
        # https://pro.arcgis.com/en/pro-app/arcpy/geoprocessing_and_python/a-template-for-python-toolboxes.htm
        self.label = "CGA SPI Tool"
        self.description = "SPI analysis based on Fisher & Didier (2013)."
        self.canRunInBackground = False

        # Check that necessary extensions are available:
        arcpy.gp.CheckOutExtension("spatial")

        # Set geoprocessor preferences
        arcpy.gp.pyramid = "PYRAMIDS 0"
        arcpy.gp.rasterStatistics = "NONE"

        # Define directories
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        base_dir = os.path.dirname(aprx.filePath)
        data_dir = os.path.join(base_dir, "Data")
        work_dir = os.path.join(data_dir, "SPI_Working")
        if not os.path.isdir(data_dir):
            error_msg = "The Data directory you are looking for does not exist"
            raise FileNotFoundError(error_msg)

        # Define class variables
        self.convertToInteger = True
        self.baseDir = base_dir
        self.workDir = work_dir
        self.totalRows = 0
        self.featsDesc = None

        # Set workspace environment
        arcpy.env.workspace = self.workDir
        arcpy.env.scratchWorkspace = self.workDir

        # Set up workspace directory
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)

        # Intermediate layer names
        # THESE LAYERS ARE DELETED
        self.feats = "featslyr"
        # name of intermediate cost surface (path = dirWorking)
        self.cost = "cost"
        # name of cost-dist grid for each loop
        self.costDist = "cd"
        # name of influence grid for each feat
        self.influence = "infl"

    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Function Definitions
    # ////////////////////////////////////////////////////////////////////////
    def makeCostParam(self, cost_surface):
        """
        Name:    MYARCPYSPI.makeCostParam
        Inputs:  str, path to cost surface raster file (cost_surface)
        Outputs: Parameter
        Feature: Creates parameter for input cost surface raster.
        """
        param0 = arcpy.Parameter(
            displayName="Cost Surface Raster",
            name="costInput",
            datatype="GPLayer",
            parameterType="Required",
            direction="Input")

        param0.value = cost_surface
        return param0

    def makeInputParam(self, input_feat):
        """
        Name:    MYARCPYSPI.makeInputParam
        Inputs:  str, path to input feature file (input_feat)
        Outputs: Parameter
        Feature: Creates parameter for input feature layer.
        """
        param1 = arcpy.Parameter(
            displayName="Feature Layer",
            name="featsInput",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param1.value = input_feat
        return param1

    def makeWeightParam(self, weight_col):
        """
        Name:    MYARCPYSPI.makeWeightParam
        Inputs:  str, input feature layer field name (weight_col)
        Outputs: Parameter
        Feature: Creates parameter for input feature layer weight column.
        """
        param2 = arcpy.Parameter(
            displayName="Feature Weight Column",
            name="weightColumn",
            datatype="Field",
            parameterType="Optional",
            direction="Input")

        param2.value = weight_col
        return param2

    def makeOutputParam(self, out_rast):
        """
        Name:    MYARCPYSPI.makeOutputParam
        Inputs:  str, path to output SPI raster layer (out_rast)
        Outputs: Parameter
        Feature: Creates parameter for output SPI raster layer.
        """
        param3 = arcpy.Parameter(
            displayName="Output SPI Raster",
            name="outGrid",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")

        param3.value = out_rast
        return param3

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Parameter data types:
        # https://pro.arcgis.com/en/pro-app/arcpy/geoprocessing_and_python/
        # defining-parameter-data-types-in-a-python-toolbox.htm
        param0 = arcpy.Parameter(
            displayName="Cost Surface Raster",
            name="costInput",
            datatype="GPLayer",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="Feature Layer",
            name="featsInput",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        param2 = arcpy.Parameter(
            displayName="Feature Weight Column",
            name="weightColumn",
            datatype="Field",
            parameterType="Optional",
            direction="Input")
        param2.filter.list = ['Long', 'Short', 'Float', 'Double']
        param2.parameterDependencies = [param1.name]
        param3 = arcpy.Parameter(
            displayName="Output SPI Raster",
            name="outGrid",
            datatype="DEFile",
            parameterType="Required",
            direction="Output")

        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # TODO: validate table has field
        # TODO: check to see if cost distance requires point featues
        # TODO: read fields from featsInput -> weightedColumn options
        # TODO: set working directory?

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """
        Name:     MYARCPYSPI.execute
        Features: The ArcGIS toolbox tool execute function
        Inputs:   - list, list of Parameters required
                    1. Parameter, cost surface raster
                    2. Parameter, input feature layer
                    3. Parameter, input feature field name
                    4. Parameter, output raster file
                  - Message
        """
        # Set user options:
        self.costInput = parameters[0].valueAsText
        self.featsInput = parameters[1].valueAsText
        self.weightColumn = parameters[2].valueAsText
        self.outGrid = parameters[3].valueAsText

        # Default to equal weights if no weight column is defined
        self.equalWeight = True
        if self.weightColumn is not None and self.weightColumn != "":
            self.equalWeight = False

        # Copy feats to intermediate location to avoid messing with the
        # The copy features can't have the ".shp" extension, but is necessary
        # for Describe to work...
        feats_copy = os.path.join(self.workDir, self.feats)
        feats_copy_shp = feats_copy + ".shp"
        self.featsShape = feats_copy_shp
        arcpy.CopyFeatures_management(self.featsInput, feats_copy)

        feats_desc = arcpy.Describe(feats_copy_shp)
        self.featsDesc = feats_desc

        # See how many features we are working with
        total_rows = int(arcpy.GetCount_management(feats_copy_shp).getOutput(0))
        self.totalRows = total_rows

        # Create the weight column
        # e.g., this could be village population because more people
        # need more resources
        if self.equalWeight == True:
            self.weightColumn = "spiweight"
            arcpy.AddField_management(
                feats_copy_shp, self.weightColumn, "SHORT")
            arcpy.CalculateField_management(
                feats_copy_shp, self.weightColumn, "1")

        # Set environment variables
        my_cell_size_x = arcpy.GetRasterProperties_management(
            self.costInput, 'CELLSIZEX').getOutput(0)
        my_cell_size_x = float(my_cell_size_x)
        arcpy.env.cellSize = my_cell_size_x
        arcpy.env.extent = self.costInput
        arcpy.env.snapRaster = self.costInput

        # Run the program...
        self.calcCost()
        self.calcInfluence()
        self.cleanup()

    def calcCost(self):
        """
        Name:     MYARCPYSPI.calcCost
        Features: Iterates through features in the input feature class
                  and calculates their cost distances
        """
        # Track highest cost distance maximum for use as "anchor"
        self.maxCostDist = 0

        # Create a floating point version of the cost raster
        cost_rast = os.path.join(self.workDir, self.cost)
        cell_size = float(arcpy.env.cellSize)
        cost_f = arcpy.sa.FloatDivide(self.costInput, cell_size)
        cost_f.save(cost_rast)

        # Prepare the progressor:
        arcpy.SetProgressor(
            "step", "Calculating cost distances...", 0, self.totalRows, 1)

        # Begin a search cursor that allows us to iterate through features
        cursor = arcpy.SearchCursor(self.featsShape)
        row = cursor.next()
        while row:
            featID = str(row.getValue(self.featsDesc.OIDFieldName))

            # Select a single feature for doing the cost distance
            my_query = '"%s" = %s' % (self.featsDesc.OIDFieldName, featID)
            arcpy.SelectLayerByAttribute_management(
                self.featsShape, "NEW_SELECTION", my_query)

            # Cost distance for a single feature
            cd_out_name = "%s%s" % (self.costDist, featID)
            cd_out = os.path.join(self.workDir, cd_out_name)
            cd = arcpy.sa.CostDistance(self.featsShape, cost_rast)
            cd.save(cd_out)

            # Get maximum distance of cost distance raster
            cdm = arcpy.GetRasterProperties_management(
                cd, 'MAXIMUM').getOutput(0)
            cdm = float(cdm)

            # Apply max distance threshold
            # TODO: apply the con tool to set pixel values greater than
            # maximum to maximum

            if cdm > self.maxCostDist:
                self.maxCostDist = cdm

            out_str = "Calculating cost ...(%s/%s)" % (
                int(featID)+1, self.totalRows)
            arcpy.SetProgressorLabel(out_str)
            arcpy.SetProgressorPosition()

            row = cursor.next()

        arcpy.SelectLayerByAttribute_management(
            self.featsShape, "CLEAR_SELECTION")
        arcpy.SetProgressorLabel("Cost distance complete.")
        arcpy.ResetProgressor()

    def calcInfluence(self):
        """
        Name:     MYARCPYSPI.calcInfluence
        Inputs:   None.
        Outputs:  None.
        Features: Normalizes each cost distance over maximum of cost distances
                  calculates influence, and multiplies by weight
        """
        # Prepare the progressor:
        arcpy.SetProgressor(
            "step", "Calculating influence...", 0, self.totalRows, 1)

        # Prep weighted sum table
        my_table_list = []

        # Begin a search cursor that allows us to iterate through features
        cursor = arcpy.SearchCursor(self.featsShape)
        row = cursor.next()
        while row:
            featID = str(row.getValue(self.featsDesc.OIDFieldName))

            # Cost distance raster
            cd_out_name = "%s%s" % (self.costDist, featID)
            cd_out = os.path.join(self.workDir, cd_out_name)

            # Normalize cost distance over maximum of cost distance
            # maximums. Linear normalization function as before:
            # (x - min) / (max - min) but here we rely on min = 0
            # (smallest cost distance is always 0).
            # This means 0-1 for feature with largest range; 0-.xxx for all
            # others (so normalization scale is the same everywhere).
            # Have to do this before inverting to "influence" to preserve
            # max influence = 1 at feature cell (i.e., where cost
            # distance = 0).
            cn_out_name = "%s%s_norm" % (self.costDist, featID)
            cn_out = os.path.join(self.workDir, cn_out_name)
            cn = arcpy.sa.Divide(cd_out, self.maxCostDist)
            cn.save(cn_out)

            # Invert cost distance to influence and multiply by weight to
            # get units in weight (e.g., people)
            weightVal = row.getValue(self.weightColumn)
            irast_out_name = "%s%s" % (self.influence, featID)
            irast_out = os.path.join(self.workDir, irast_out_name)
            irast = (1.0 - cn) * weightVal
            irast.save(irast_out)

            out_str = "Calculating influence feature %s" % (featID)
            arcpy.SetProgressorLabel(out_str)
            arcpy.SetProgressorPosition()

            my_table_list.append([irast_out_name, "VALUE", 1])

            row = cursor.next()

        # Weighted sum
        my_table = arcpy.sa.WSTable(my_table_list)
        wtsum = arcpy.sa.WeightedSum(my_table)
        wtsum.save(self.outGrid)

        # Add spi raster to the map
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        my_map = aprx.listMaps()[0]
        my_map.addDataFromPath(self.outGrid)

        arcpy.SetProgressorLabel("Weighted influence complete.")
        arcpy.ResetProgressor()

    def cleanup(self):
        """
        Name:     MYARCPYSPI.cleanup
        Inputs:   None.
        Outputs:  None.
        Features: Deletes intermediate raster files
        """
        # Prepare the progressor:
        arcpy.SetProgressor(
            "step", "Cleaning up...", 0, self.totalRows, 1)

        # Begin a search cursor that allows us to iterate through features
        cursor = arcpy.SearchCursor(self.featsShape)
        row = cursor.next()
        while row:
            featID = str(row.getValue(self.featsDesc.OIDFieldName))

            # Cost distance raster
            cd_out_name = "%s%s" % (self.costDist, featID)
            cd_out = os.path.join(self.workDir, cd_out_name)
            if os.path.exists(cd_out):
                arcpy.Delete_management(cd_out)
                out_str = "Deleting %s" % (cd_out_name)
                arcpy.SetProgressorLabel(out_str)

            cn_out_name = "%s%s_norm" % (self.costDist, featID)
            cn_out = os.path.join(self.workDir, cn_out_name)
            if os.path.exists(cn_out):
                arcpy.Delete_management(cn_out)
                out_str = "Deleting %s" % (cn_out_name)
                arcpy.SetProgressorLabel(out_str)

            irast_out_name = "%s%s" % (self.influence, featID)
            irast_out = os.path.join(self.workDir, irast_out_name)
            if os.path.exists(irast_out):
                arcpy.Delete_management(irast_out)
                out_str = "Deleting %s" % (irast_out_name)
                arcpy.SetProgressorLabel(out_str)

            arcpy.SetProgressorPosition()

            row = cursor.next()

        arcpy.SetProgressorLabel("Garbage dealt with.")
        arcpy.ResetProgressor()
