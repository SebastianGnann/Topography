import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from scipy import stats
import seaborn as sns
#from functions import plotting_fcts
#from functions import get_nearest_neighbour
import geopandas as gpd
from shapely.geometry import Point
import xarray as xr
from datetime import datetime as dt
import rioxarray as rxr

data_path = "/home/hydrosys/data/" #r"D:/Data/" #

dem_path = data_path + "WorldClim/wc2.1_30s_elev/wc2.1_30s_elev.tif" # code currently only works with that DEM
pr2_path = data_path + "WorldClim/wc2.1_30s_bio/wc2.1_30s_bio_12.tif"
#dem_path = data_path + "DEMs/MERIT_250m/Elevation_MERIT_30s.tif"
pr_path = data_path + "CHELSA/CHELSA_bio12_1981-2010_V.2.1.tif"

var_list = ["pr_WorldClim", "DEM"]
path_list = [pr2_path,
             dem_path]

df = pd.DataFrame(columns=["y", "x"])
for var, path in zip(var_list, path_list):
    rds = rxr.open_rasterio(path)
    rds = rds.squeeze().drop("spatial_ref").drop("band")
    rds.name = var
    df_tmp = rds.to_dataframe().reset_index()
    # df_tmp["y"] = np.round(df_tmp["y"],4) # because of small coordinate differences...
    # df_tmp["x"] = np.round(df_tmp["x"],4)
    df = pd.merge(df, df_tmp, on=['y', 'x'], how='outer')

df.rename(columns={'x': 'lon', 'y': 'lat'}, inplace=True)

df.loc[df["pr_WorldClim"] < 0, "pr_WorldClim"] = np.nan
#df.loc[df["pr_CHELSA"] > 50000, "pr_CHELSA"] = np.nan
df.loc[df["DEM"] > 50000, "DEM"] = np.nan

#df['pr_CHELSA'] = df['pr_CHELSA'] * 0.1

df = df.dropna()

print("mean above 1000m: ", str(df.loc[df["DEM"] > 1000, "pr_WorldClim"].mean()))
print("mean below 1000m: ", str(df.loc[df["DEM"] < 1000, "pr_WorldClim"].mean()))


df_new = []
# loop over lat,lon
for x, y in zip(df["lon"], df["lat"]):
    # https://gis.stackexchange.com/questions/421231/how-can-i-calculate-the-area-of-a-5-arcminute-grid-cell-in-square-kilometers-gi
    # 1 degree of latitude = 111.567km. This varies very slightly by latitude, but we'll ignore that
    # 5 arcminutes of latitude is 1/12 of that, so 9.297km
    # 5 arcminutes of longitude is similar, but multiplied by cos(latitude) if latitude is in radians, or cos(latitude/360 * 2 * 3.14159) if in degrees
    # we have half a degree here
    y_len = 111.567/(2*60)
    x_len = y_len * np.cos(y/360 * 2 * np.pi)
    df_new.append([x_len, y_len])
df_new = pd.DataFrame(df_new)
df_new["area"] = df_new[0]*df_new[1]
df["area"] = df_new["area"]

print("WorldClim")
print((df["pr_WorldClim"]*df["area"]).sum()/df["area"].sum())
for i in [1, 2, 3, 4]:
    df_tmp = df.loc[df["Landform"]==i]
    print((df_tmp["pr_WorldClim"]*df_tmp["area"]).sum()/df_tmp["area"].sum())

print("CHELSA")
print((df["pr_CHELSA"]*df["area"]).sum()/df["area"].sum())
for i in [1, 2, 3, 4]:
    df_tmp = df.loc[df["Landform"]==i]
    print((df_tmp["pr_CHELSA"]*df_tmp["area"]).sum()/df_tmp["area"].sum())

