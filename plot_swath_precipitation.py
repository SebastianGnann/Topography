import matplotlib.pyplot as plt
import numpy as np
import rioxarray as rxr
import pyosp
from functions.get_geometries import get_swath_geometries
from functions.create_shapefiles import create_line_shp
from functions.create_shapefiles import create_polygon_shp
import os
from functions.get_swath_data import get_swath_data

# Plots a transect of precipitation (or other variables) along swaths in different mountain regions.

# specify paths
#data_path = r"C:/Users/Sebastian/Documents/Data/"
data_path = r"D:/Data/"
results_path = "results/"

shp_path = data_path + "GMBA mountain inventory V1.2(entire world)/GMBA Mountain Inventory_v1.2-World.shp"
#dem_path = data_path + "WorldClim/wc2.1_30s_elev/wc2.1_30s_elev.tif"
#pr_path = data_path + "WorldClim/wc2.1_30s_bio/wc2.1_30s_bio_12.tif"
#pet_path = data_path + "WorldClim/7504448/global-et0_annual.tif/et0_yr/et0_yr.tif"
#t_path = data_path + "WorldClim/wc2.1_30s_bio/wc2.1_30s_bio_1.tif"
dem_path = data_path + "DEMs/MERIT_250m/Elevation_MERIT_30s.tif"
pr_path = data_path + "CHELSA/CHELSA_bio12_1981-2010_V.2.1.tif"
pet_path = data_path + "CHELSA/CHELSA_pet_penman_mean_1981-2010_V.2.1.tif"
t_path = data_path + "CHELSA/CHELSA_bio1_1981-2010_V.2.1.tif"

name_list = ["Southern Andes"]

# load dem shapefile
dem = rxr.open_rasterio(dem_path, masked=True).squeeze() #todo: remove masked ...

# loop over mountain ranges
for name in name_list:

    # check if folder exists
    path = results_path + name + '/shapefiles/'
    if not os.path.isdir(path):
        os.makedirs(path)

    path = results_path + name + "/swaths_precipitation/"
    if not os.path.isdir(path):
        os.makedirs(path)

    # load coordinates for lines
    xy_line, xy_box = get_swath_geometries(name)

    # create line
    baseline = results_path + name + '/shapefiles/line.shp'
    create_line_shp(xy_line, baseline)
    line_shape = pyosp.read_shape(baseline)
    lx, ly = line_shape.xy

    # generate swath objects
    w = 1.6 # 2 degrees + 2*cs
    ls = w/250
    cs = w/100
    orig_dem = pyosp.Orig_curv(baseline, dem_path, width=w, line_stepsize=ls, cross_stepsize=cs)
    orig_pr = pyosp.Orig_curv(baseline, pr_path, width=w, line_stepsize=ls, cross_stepsize=cs)
    orig_pet = pyosp.Orig_curv(baseline, pet_path, width=w, line_stepsize=ls, cross_stepsize=cs)
    orig_t = pyosp.Orig_curv(baseline, t_path, width=w, line_stepsize=ls, cross_stepsize=cs)

    ### PLOT 1 ###
    fig = plt.figure(figsize=(4, 2), constrained_layout=True)
    ax = plt.axes()

    # plot swath lines and polygons
    swath_polylines = orig_dem.out_polylines()
    swath_polygon = orig_dem.out_polygon()
    px, py = swath_polygon.exterior.xy
    ax.plot(px, py, c='tab:orange')

    # save polygon as shapefile
    create_polygon_shp(swath_polygon, results_path + name + '/shapefiles/polygon.shp')

    sp0 = dem.plot.imshow(ax=ax, cmap='gray')
    ax.set(title=None)
    ax.axis('equal')
    ax.set_xlim([xy_box[0], xy_box[1]])
    ax.set_ylim([xy_box[2], xy_box[3]])
    ax.set_xlabel('Lon [deg]')
    ax.set_ylabel('Lat [deg]')
    sp0.colorbar.set_label('Elevation [m]')
    sp0.set_clim([0, 3000])

    #plt.show()
    plt.savefig(results_path + name + "/swaths_precipitation/swath_" + name + ".png", dpi=600, bbox_inches='tight')
    plt.close()

    # plot swath profile
    dist, dem_swath, pr_swath, pet_swath, t_swath = \
        get_swath_data(orig_dem, orig_pr, orig_pet, orig_t, line_shape)

    # account for offset and scale (only for CHELSA)
    pr_swath = pr_swath * 0.1
    pet_swath = pet_swath * 0.01 * 12
    t_swath = t_swath * 0.1 - 273.15

    ### PLOT 2 ###
    # plot swath transect
    fig = plt.figure(figsize=(8, 2), constrained_layout=True)
    ax = plt.axes()

    axa = ax.twinx()
    axa.fill_between(dist, np.zeros(len(dist)), dem_swath.mean(axis=1),
                       facecolor='tab:gray', alpha=0.5, label='Elevation')

    axb = ax.twinx()
    axb.plot(dist, pr_swath.mean(axis=1),
               c='tab:blue', label='Precipitation') #np.array(orig_dem.dat)[:,i]
    axb.fill_between(dist, pr_swath.mean(axis=1)-pr_swath.std(axis=1), pr_swath.mean(axis=1)+pr_swath.std(axis=1),
                        facecolor='tab:blue', alpha=0.25)

    lines, labels = ax.get_legend_handles_labels()
    lim = 6000
    axa.set_ylim(0,lim)
    axb.set_ylim(0,lim)
    axa.set_xlim([line_shape.xy[0][0], line_shape.xy[0][1]]) # works only for east-west swaths
    axb.set_xlim([line_shape.xy[0][0], line_shape.xy[0][1]]) # works only for east-west swaths
    #ax.set_xlabel('Lon [deg]')

    ax.spines.right.set_visible(False)
    ax.spines.left.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.spines.bottom.set_visible(False)
    ax.set_xticklabels([])
    ax.set_xticks([])
    ax.set_yticklabels([])
    ax.set_yticks([])

    axa.spines['right'].set_position(('outward', 50))
    axa.spines.left.set_visible(False)
    axa.spines.top.set_visible(False)
    axa.spines['bottom'].set_position(('outward', 10))

    axb.spines['right'].set_position(('outward', 10))
    axb.yaxis.label.set_color('black')
    axb.tick_params(axis='y', colors='black')
    axb.spines['right'].set_color('black')
    axb.spines.left.set_visible(False)
    axb.spines.top.set_visible(False)
    axb.spines.bottom.set_visible(False)
    plt.yticks(fontsize=12)

    #plt.show()
    plt.savefig(results_path + name + "/swaths_precipitation/transect_" + name + ".png", dpi=600, bbox_inches='tight')
    plt.close()
