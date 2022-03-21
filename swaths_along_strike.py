import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from shapely.geometry import mapping
import rioxarray as rxr
import xarray as xr
import geopandas as gpd
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
from scipy import stats
import pandas as pd
from shapely import geometry
import shapely
import pyosp
import fiona
import numpy.ma as ma
import sys
#sys.path.append( '/alpha/beta' )
#import Transects

# specify paths
data_path = r"C:/Users/Sebastian/Documents/Data/" #r"C:/Users/gnann/Documents/Data/"#r"C:/Users/Sebastian/Documents/Data/" #
results_path = "results/" #r"C:/Users/gnann/Documents/PYTHON/Topography/results/"

shp_path = data_path + "GMBA mountain inventory V1.2(entire world)/GMBA Mountain Inventory_v1.2-World.shp"
dem_path = data_path + "wc2.1_30s_elev/wc2.1_30s_elev.tif"
clim_path = data_path + "wc2.1_30s_bio/wc2.1_30s_bio_12.tif"
clim2_path = data_path + "wc2.1_30s_vapr/wc2.1_30s_vapr_avg.tif"

line_path = r"C:/Users/Sebastian/Documents/Python/Topography/Transects/Himalaya_Line/Himalaya_Arc.shp"

name_list = ["Himalaya"]#["Sierra Nevada", "Alps", "Ecuador Andes", "France", "Himalaya", "NorthernAlps", "Kilimanjaro", "Cascades"]

for name in name_list:

    # create geometries
    """
    import get_region
    xy_line, xy_box = get_region.get_region(name)

    line = geometry.LineString([geometry.Point(xy_line[0], xy_line[2]),
                                geometry.Point(xy_line[1], xy_line[3])])

    schema = {'geometry': 'LineString', 'properties': {'id': 'int'}}
    # write a new shapefile
    with fiona.open(results_path + 'tmp/tmp_' + name + '_line.shp', 'w', 'ESRI Shapefile', schema) as c:
        c.write({'geometry': mapping(line), 'properties': {'id': 123}})

    baseline = results_path + 'tmp/tmp_' + name + '_line.shp'
    line_shape = pyosp.read_shape(baseline)
    lx, ly = line_shape.xy

    polygon = [{'type': 'Polygon',
                'coordinates': [[[xy_box[0], xy_box[2]],
                                 [xy_box[0], xy_box[3]],
                                 [xy_box[1], xy_box[3]],
                                 [xy_box[1], xy_box[2]],
                                 [xy_box[0], xy_box[2]]]]}]
    """

    line = pyosp.read_shape(line_path)
    #mountain_shp = gpd.read_file(shp_path)
    #mountain_range = mountain_shp.loc[mountain_shp.Name==name]

    # preprocess shapefiles
    dem = rxr.open_rasterio(dem_path, masked=True).squeeze()
    #dem_clipped = dem.rio.clip(mountain_range.geometry.apply(mapping), dem.rio.crs)
    #dem_clipped.__array__()[np.isnan(dem_clipped.__array__())] = -999
    #dem_clipped.rio.to_raster(results_path + 'tmp/tmp_' + name + '_dem.tif')
    #raster_dem = results_path + 'tmp/tmp_' + name + '_dem.tif'
    #dem_clipped = rxr.open_rasterio(raster_dem).squeeze()

    clim = rxr.open_rasterio(clim_path, masked=True).squeeze()
    #clim_clipped = clim.rio.clip(mountain_range.geometry.apply(mapping), clim.rio.crs)
    #clim_clipped.__array__()[np.isnan(clim_clipped.__array__())] = -999
    #clim_clipped.rio.to_raster(results_path + 'tmp/tmp_' + name + '_clim.tif')
    #raster_clim = results_path + 'tmp/tmp_' + name + '_clim.tif'
    #clim_clipped = rxr.open_rasterio(raster_clim).squeeze()

    clim2 = rxr.open_rasterio(clim2_path, masked=True).squeeze()
    #clim2_clipped = clim2.rio.clip(mountain_range.geometry.apply(mapping), clim2.rio.crs)
    #clim2_clipped.__array__()[np.isnan(clim2_clipped.__array__())] = -999
    #clim2_clipped.rio.to_raster(results_path + 'tmp/tmp_' + name + '_clim2.tif')
    #raster_clim2 = results_path + 'tmp/tmp_' + name + '_clim2.tif'
    #clim2_clipped = rxr.open_rasterio(raster_clim2).squeeze()


    """
    mp = shapely.geometry.MultiPoint()
    len = line.length
    for i in np.arange(0, len, len/9):
        s = shapely.ops.substring(line, i, i + len/9)
        s = shapely.wkt.loads(shapely.wkt.dumps(s, rounding_precision=3))
        mp = mp.union(s.boundary)
    #mp = shapely.wkt.loads(shapely.wkt.dumps(mp, rounding_precision=3))
    #mp = shapely.wkt.loads(mp).simplify(0)
    """

    w = 2
    distances = np.arange(0, line.length, w)[:-1]
    # or alternatively without NumPy:
    # points_count = int(line.length // distance_delta) + 1
    # distances = (distance_delta * i for i in range(points_count))
    points = [line.interpolate(distance) for distance in distances] + [line.boundary[1]]
    mp = shapely.ops.unary_union(points)  # or new_line = LineString(points)

    """
    n = 10
    # or to get the distances closest to the desired one:
    # n = round(line.length / desired_distance_delta)
    distances = np.linspace(0, line.length, n)
    # or alternatively without NumPy:
    # distances = (line.length * i / (n - 1) for i in range(n))
    points = [line.interpolate(distance) for distance in distances]
    mp = shapely.ops.unary_union(points)  # or new_line = LineString(points)
    """

    xs = [point.x for point in mp]
    ys = [point.y for point in mp]
    x, y = line.xy
    xx = (np.array(xs[1:])+np.array(xs[0:-1]))/2
    yy = (np.array(ys[1:])+np.array(ys[0:-1]))/2
    d = 2

    import perp_pts
    m = (ys[1] - ys[0]) / (xs[1] - xs[0])
    x1, y1, x2, y2 = perp_pts.perp_pts(xx[0], yy[0], m, d*2, [xs[0], ys[0], xs[1], ys[1]])

    #plt.scatter(xs, ys)
    #plt.plot(x, y)
    #plt.scatter(xx, yy)
    #plt.scatter(x1,y1)
    #plt.scatter(x2,y2)
    #plt.show()
    #plt.axis('equal')

    # write line
    line = geometry.LineString([geometry.Point(x1, y1),
                                geometry.Point(xx[0], yy[0])])

    schema = {'geometry': 'LineString', 'properties': {'id': 'int'}}
    # write a new shapefile
    with fiona.open(results_path + 'tmp/tmp_' + name + '_line.shp', 'w', 'ESRI Shapefile', schema) as c:
        c.write({'geometry': mapping(line), 'properties': {'id': 123}})

    baseline = results_path + 'tmp/tmp_' + name + '_line.shp'
    line_shape = pyosp.read_shape(baseline)
    lx, ly = line_shape.xy

    # generate swath objects
    line_stepsize = 0.05
    cross_stepsize = 0.05
    orig_dem = pyosp.Orig_curv(baseline, dem_path, width=w, line_stepsize=line_stepsize, cross_stepsize=line_stepsize)
    orig_clim = pyosp.Orig_curv(baseline, clim_path, width=w, line_stepsize=line_stepsize, cross_stepsize=line_stepsize)
    orig_clim2 = pyosp.Orig_curv(baseline, clim2_path, width=w, line_stepsize=line_stepsize, cross_stepsize=line_stepsize)

    # plot the swath profile lines
    fig = plt.figure(figsize=(12, 3), constrained_layout=True)
    gs = plt.GridSpec(1, 3, figure=fig)
    axes0 = fig.add_subplot(gs[0, 0])
    axes1 = fig.add_subplot(gs[0, 1])
    axes2 = fig.add_subplot(gs[0, 2])

    swath_polylines = orig_dem.out_polylines()
    #for line in swath_polylines:
    #    x, y = line.xy
    #    axes0.plot(x, y, color='C2')

    swath_polygon = orig_dem.out_polygon()
    px, py = swath_polygon.exterior.xy
    axes0.plot(px, py, c='tab:orange')

    #axes0.plot(lx, ly, color='C3', label="Baseline")
    axes0.set_aspect('equal', adjustable='box')
    #axes0.set_title("Swath profile lines")
    #axes0.legend()

    sp0 = dem.plot.imshow(ax=axes0, cmap='terrain')
    axes0.set(title=None) #"DEM [m]"
    #axes1.set_axis_off()
    #axes0.axis('equal')
    #axes0.set_xlim([xy_box[0], xy_box[1]])
    #axes0.set_ylim([xy_box[2], xy_box[3]])
    axes0.set_xlim([60, 110])
    axes0.set_ylim([20, 40])
    axes0.set_xlabel('Lon [deg]')
    axes0.set_ylabel('Lat [deg]')
    sp0.colorbar.set_label('DEM [m]')
    #sp0.set_clim([0, np.round(np.array(orig_dem.dat).max(), 100)])
    sp0.set_clim([0, 8000]) #100*round(np.max(dem.values/100))

    axes0.plot(x, y, color='tab:red')

    # plot swath
    #orig_dem.profile_plot(ax=axes1, color='grey', label='Elevation')
    #orig_clim.profile_plot(ax=axes1, color='navy', label='Precipitation')
    #for i in range(len(orig_dem.dat[0])):
    dist = orig_dem.distance
    dem_swath = np.array(orig_dem.dat)
    dem_swath[dem_swath==-999] = np.nan
    if len(dist) > len(dem_swath):
        dist = orig_dem.distance[0:-1]
    #ma.masked_invalid(dem_swath)
    clim_swath = np.array(orig_clim.dat)
    clim_swath[clim_swath==-999] = np.nan
    #ma.masked_invalid(clim_swath)
    clim2_swath = np.array(orig_clim2.dat)
    clim2_swath[clim2_swath==-999] = np.nan
    clim2_swath = clim2_swath*1000 # transform to Pa
    #ma.masked_invalid(clim_swath)

    axes1.fill_between(dist, np.zeros(len(dist)), dem_swath.mean(axis=1),
                       facecolor='tab:gray', alpha=0.25, label='Elevation')
    axes1.fill_between(dist, np.zeros(len(dist)), dem_swath.mean(axis=1)-dem_swath.std(axis=1),
                       facecolor='tab:gray', alpha=0.25)
    axes1.fill_between(dist, np.zeros(len(dist)), dem_swath.mean(axis=1)+dem_swath.std(axis=1),
                       facecolor='tab:gray', alpha=0.25)
    #axes1.plot(dist, dem_swath.mean(axis=1), c='tab:grey', label='Elevation') #np.array(orig_dem.dat)[:,i]

    axes1b = axes1.twinx()
    axes1b.plot(dist, clim_swath.mean(axis=1),
               c='tab:blue', label='Precipitation') #np.array(orig_dem.dat)[:,i]
    axes1b.fill_between(dist, clim_swath.mean(axis=1)-clim_swath.std(axis=1), clim_swath.mean(axis=1)+clim_swath.std(axis=1),
                        facecolor='tab:blue', alpha=0.25)

    axes1b.plot(dist, clim2_swath.mean(axis=1),
                c='tab:green', label='Vapor pressure')  # np.array(orig_dem.dat)[:,i]
    axes1b.fill_between(dist, clim2_swath.mean(axis=1) - clim2_swath.std(axis=1),
                        clim2_swath.mean(axis=1) + clim2_swath.std(axis=1),
                        facecolor='tab:green', alpha=0.25)


    lines, labels = axes1.get_legend_handles_labels()
    lines2, labels2 = axes1b.get_legend_handles_labels()
    axes1b.legend(lines + lines2, labels + labels2)
    #axes1.legend().set_visible(False)
    #axes1.legend(loc='upper left')
    axes1.set_xlabel('Distance [deg]')
    axes1.set_ylabel('Elevation [m]')
    axes1b.set_ylabel('Precipitation [mm/y] / Vapor pressure [Pa]')
    #axes1.set_ylim(0,5000)
    #axes1b.set_ylim(0,5000)

    axes2.plot(clim_swath.mean(axis=1), dem_swath.mean(axis=1), c='grey', alpha=0.5)
    sp2 = axes2.scatter(clim_swath.mean(axis=1), dem_swath.mean(axis=1),
                 marker='o', c=dist)
    axes2.set_xlabel('Precipitation [mm/y]')
    axes2.set_ylabel('Elevation [m]')
    #axes2.set_xlim([0,5000])
    #axes2.set_ylim([0,5000])
    #axes2.set(title="Distance [deg]")
    cbar2 = plt.colorbar(sp2, ax=axes2)
    cbar2.ax.set_ylabel('Distance [deg]')

    #fig.tight_layout()

    #plt.show()
    plt.savefig(results_path + "swath_along_strike_" + name + ".png", dpi=600, bbox_inches='tight')
    #plt.clear()

