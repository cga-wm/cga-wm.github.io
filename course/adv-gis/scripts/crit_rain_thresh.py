#!/usr/bin/env python3
#
# crit_rain_thresh.py
#
# Tyler W. Davis, CGA, William & Mary
#
# LAST UPDATED: 2020-03-05
#
# This script contains the "sandbox" of methods for creating the
# critical rainfall threshold model, which is to become a Python toolbox.

##############################################################################
# REQUIRED MODULES
##############################################################################
import os.path

import arcpy

##############################################################################
# SANDBOX
##############################################################################
# Setting up my folders
aprx = arcpy.mp.ArcGISProject("CURRENT")
base_dir = os.path.dirname(aprx.filePath)
out_dir = os.path.join(base_dir, "Output")

# Define constants
k_pi = 3.14159
gamma_r_nm3 = 20000.0  # unit weight of soil, N/m3
gamma_w_nm3 = 10000.0  # unit weight of water, N/m3

# Define input rasters
lands_h = "soilmu_a_aoi_utm_h"       # depth of regolith, m
lands_phi = "soilmu_a_aoi_utm_psi"   # internal friction angle, deg
lands_c = "soilmu_a_aoi_utm_c"       # soil cohesion, Pa
lands_theta = "collbran_slope"       # hillslope angle, deg

# Define input water depth, m
water_h = .2

# Create radian version of slope
theta_rad = arcpy.sa.Times(lands_theta, k_pi/180.0)
phi_rad = arcpy.sa.Times(lands_psi, k_pi/180.0)

# The Critical Rainfall Threshold Model
#
#      tan φ                 C                     ψt * γw * (tan φ)
# Fs = -----  +  -------------------------- - ----------------------------
#      tan θ     γr * H * (sin θ) * (cos θ)    γr * H * (sin θ) * (cos θ)
#
# Fs = Ff     +              Fc             -          Fw
#

# STEP - Calculate Ff
ff = arcpy.sa.Divide(arcpy.sa.Tan(phi_rad), arcpy.sa.Tan(theta_rad))

# STEP - Calculate Fc
sin_cos = arcpy.sa.Times(arcpy.sa.Sin(theta_rad), arcpy.sa.Cos(theta_rad))
# Soil depth vertical (influenced by gravity)
big_z = arcpy.sa.Divide(lands_h, arcpy.sa.Cos(theta_rad))
h_sin_cos = arcpy.sa.Times(big_z, sin_cos)
c_gr = arcpy.sa.Divide(lands_c, gamma_r_nm3)
fc = arcpy.sa.Divide(c_gr, h_sin_cos)

# Step - Calculate Fw
# Pressure head parallel to hillslope
ls_psit = arcpy.sa.Times(water_h, arcpy.sa.Cos(theta_rad))
g_wr = gamma_w_nm3/gamma_r_nm3
pgwr = arcpy.sa.Times(ls_psit, g_wr)
pgwrt = arcpy.sa.Times(pgwr, arcpy.sa.Tan(phi_rad))
fw = arcpy.sa.Divide(pgwrt, h_sin_cos)

# Step - calculate Fs
# REMINDER: where fs < 1, UNSAFE
fs = ff + fc - fw
