#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# lsa.pyt
#
# Tyler W. Davis, CGA, William & Mary
#
# VERSION: 1.0
# LAST UPDATED: 2020-03-05
#
# This is a Python toolbox for calculating landslide susceptibility.
# This is a part of GIS 420 class.

##############################################################################
# IMPORT MODULES
##############################################################################
import os.path

import arcpy


##############################################################################
# CLASSES
##############################################################################
class Toolbox(object):
    """
    The class needed for importing as an ArcGIS toolbox.
    """
    def __init__(self):
        """Toolbox class initialization"""
        self.label = "Landslide Analysis"
        self.alias = "Landslides"
        self.tools = [CritRainThresh]


class CritRainThresh(object):
    """
    Name:     CritRainThresh
    Features: Creates a factor of safety raster based on the Critical Rainfall
              Threshold Model (Iverson, 2000)
    History:  VERSION 1.0
              - initial attempt at an ArcGIS Toolbox
    Ref:      https://doi.org/10.1029/2000WR900090
    """
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Initialization
    # ////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
        Name:     CritRainThresh.__init__
        Inputs:   None
        Outputs:  None
        Features: Initialize the tool
        """
        # ArcGIS Tool descriptors
        self.label = "Critical Rainfall Threshold Model"
        self.description = (
            "Creates a factor of safety raster based on the Critical Rainfall "
            "Threshold Model (Iverson, 2000)"
        )
        self.canRunInBackground = False

        # Check that spatial analyst tools extension is enabled
        arcpy.gp.checkOutExtension("spatial")

        # Define constants and default values used in model
        self.k_pi = 3.14159
        self.deg2rad = self.k_pi / 180.0
        self.gamma_r_nm3 = 20000.0  # unit weight of soil, N/m3
        self.gamma_w_nm3 = 10000.0  # unit weight of water, N/m3


    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Methods
    # ////////////////////////////////////////////////////////////////////////
    def execute(self, parameters, messages):
        """
        Name:     CritRainThresh.execute
        Inputs:   - list, list of ArcGIS Parameter objects (parameters)
                  - list?
        Outputs:  None.
        Features: The ArcGIS toolbox tool execute function (i.e., Run)
        """
        # Get pointers to the current project and map:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        map = aprx.activeMap

        # Get user-defined parameters by list order:
        self.lands_theta = parameters[0].valueAsText
        self.lands_phi = parameters[1].valueAsText
        self.lands_c = parameters[2].valueAsText
        self.lands_h = parameters[3].valueAsText
        self.water_h = parameters[4].value
        self.outFs = parameters[5].valueAsText

        # Create and initialize a step progressor to update the user
        out_steps = 6
        arcpy.SetProgressor(
            "step", "Converting slope to radians...", 0, out_steps, 1
        )

        # Create radian version of slope
        theta_rad = arcpy.sa.Times(self.lands_theta, self.deg2rad)
        phi_rad = arcpy.sa.Times(self.lands_phi, self.deg2rad)

        # THE MODEL: Fs = Ff + Fc - Fw (Iverson, 2000)

        # Create Ff
        arcpy.SetProgressorLabel("Calculating Ff...")
        arcpy.SetProgressorPosition()
        ff = arcpy.sa.Divide(arcpy.sa.Tan(phi_rad), arcpy.sa.Tan(theta_rad))

        # Create Fc
        arcpy.SetProgressorLabel("Calculating Fc...")
        arcpy.SetProgressorPosition()
        sin_cos = arcpy.sa.Times(
            arcpy.sa.Sin(theta_rad), arcpy.sa.Cos(theta_rad))
        # Get vertical component of soil depth (influenced by gravity)
        big_z = arcpy.sa.Divide(self.lands_h, arcpy.sa.Cos(theta_rad))
        h_sin_cos = arcpy.sa.Times(big_z, sin_cos)
        c_gr = arcpy.sa.Divide(self.lands_c, self.gamma_r_nm3)
        fc = arcpy.sa.Divide(c_gr, h_sin_cos)

        # Create Fw
        # Get pressure head parallel to hillslope
        # NOTE: does not consider water depth greater than soil depth
        arcpy.SetProgressorLabel("Calculating Fw...")
        arcpy.SetProgressorPosition()
        ls_psit = arcpy.sa.Times(self.water_h, arcpy.sa.Cos(theta_rad))
        g_wr = self.gamma_w_nm3/self.gamma_r_nm3
        pgwr = arcpy.sa.Times(ls_psit, g_wr)
        pgwrt = arcpy.sa.Times(pgwr, arcpy.sa.Tan(phi_rad))
        fw = arcpy.sa.Divide(pgwrt, h_sin_cos)

        # Calculate Fs
        arcpy.SetProgressorLabel("Calculating Fs...")
        arcpy.SetProgressorPosition()
        fs = ff + fc - fw

        # Save output raster
        arcpy.SetProgressorLabel("Writing Fs to disk...")
        arcpy.SetProgressorPosition()
        fs.save(self.outFs)

        arcpy.SetProgressorLabel("Complete!")
        arcpy.ResetProgressor()

        # Add raster to current map
        map.addDataFromPath(self.outFs)


    def getParameterInfo(self):
        """
        Name:     CritRainThresh.getParameterInfo
        Input:    None
        Outputs:  list, list of ArcGIS Parameter objects
        Features: Defines the parameter definitions
        Ref:      https://pro.arcgis.com/en/pro-app/arcpy/
                  geoprocessing_and_python/defining-parameter-data-types-in-a-
                  python-toolbox.htm
        """
        param0 = arcpy.Parameter(
            displayName = "Hillslope raster (deg)",
            name = "lands_theta",
            datatype = "GPLayer",
            parameterType = "Required",
            direction = "Input"
        )
        param1 = arcpy.Parameter(
            displayName = "Soil internal friction angle raster (deg)",
            name = "lands_phi",
            datatype = "GPLayer",
            parameterType = "Required",
            direction = "Input"
        )
        param2 = arcpy.Parameter(
            displayName = "Soil cohesion raster (Pa)",
            name = "lands_c",
            datatype = "GPLayer",
            parameterType = "Required",
            direction = "Input"
        )
        param3 = arcpy.Parameter(
            displayName = "Depth of regolith raster (m)",
            name = "lands_h",
            datatype = "GPLayer",
            parameterType = "Required",
            direction = "Input"
        )
        param4 = arcpy.Parameter(
            displayName = "Depth of soil moisture (m)",
            name = "water_h",
            datatype = "GPDouble",
            parameterType = "Required",
            direction = "Input"
        )
        # Set default soil moisture value (m)
        param4.value = 0.2
        param5 = arcpy.Parameter(
            displayName = "Output factor of safety raster",
            name = "outFs",
            datatype = "DEFile",
            parameterType = "Required",
            direction = "Output"
        )

        # Send ArcGIS your parameters :)
        params = [param0, param1, param2, param3, param4, param5]
        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True


    def updateParameters(self, parameters):
        """This is called whenever a parameter value is changed."""
        return


    def updateMessages(self, parameters):
        """Modify messages from internal validation for each parameter."""
        return
