import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import seaborn as sns
from functions import plotting_fcts
import rasterio as rio

# Plots Moeck et al. (2021) recharge against slope and calculates the fraction of observations in each landform.

# prepare data
data_path = "D:/Data/"

pr_path = data_path + "resampling/" + "P_CHELSA_30s.tif"
pet_path = data_path + "resampling/" + "PET_CHELSA_30s.tif"
slope_path = data_path + "resampling/" + "Slope_MERIT_30s.tif"
elevation_path = data_path + "resampling/" + "Elevation_MERIT_30s.tif"
landform_path = data_path + "resampling/" + "WorldLandform_30sec.tif"

slope = rio.open(slope_path, masked=True)
elevation = rio.open(elevation_path, masked=True)
pr = rio.open(pr_path, masked=True)
pet = rio.open(pet_path, masked=True)
landform = rio.open(landform_path, masked=True)

# check if folder exists
results_path = "./results/Moeck/"
if not os.path.isdir(results_path):
    os.makedirs(results_path)

# load and process data
df = pd.read_csv("data/global_groundwater_recharge_moeck-et-al.csv", sep=',')

df.rename(columns={'Groundwater recharge [mm/y]': 'Recharge',
                   'Longitude': 'lon', 'Latitude': 'lat'}, inplace=True)

coord_list = [(x, y) for x, y in zip(df['lon'], df['lat'])]

df['slope_30s'] = [x for x in slope.sample(coord_list)]
df['slope_30s'] = np.concatenate(df['slope_30s'].to_numpy())
df.loc[df["slope_30s"] < 0, "slope_30s"] = np.nan
df['slope_30s'] = np.tan(np.deg2rad(df['slope_30s'] * 0.01))

df['elevation_30s'] = [x for x in elevation.sample(coord_list)]
df['elevation_30s'] = np.concatenate(df['elevation_30s'].to_numpy())
df.loc[df["elevation_30s"] < -1000, "elevation_30s"] = np.nan

df['pr_30s'] = [x for x in pr.sample(coord_list)]
df['pr_30s'] = np.concatenate(df['pr_30s'].to_numpy())
df.loc[df["pr_30s"] > 50000, "pr_30s"] = np.nan
df['pr_30s'] = df['pr_30s'] * 0.1

df['pet_30s'] = [x for x in pet.sample(coord_list)]
df['pet_30s'] = np.concatenate(df['pet_30s'].to_numpy())
df.loc[df["pet_30s"] > 50000, "pet_30s"] = np.nan
df['pet_30s'] = df['pet_30s'] * 0.01 * 12

df['landform'] = [x for x in landform.sample(coord_list)]
df['landform'] = np.concatenate(df['landform'].to_numpy())
df.loc[df["landform"] < 1, "landform"] = np.nan
df.loc[df["landform"] > 4, "landform"] = np.nan

df["Recharge Ratio"] = df["Recharge"]/df["pr_30s"]
df["aridity_30s"] = df["pet_30s"]/df["pr_30s"]

df["dummy"] = ""

#df = df.dropna()

df.loc[df["landform"]==1, "landform"] = 5 # mountains
df.loc[df["landform"]==2, "landform"] = 5 # hills
df.loc[df["landform"]==3, "landform"] = 5 # plateaus
df.loc[df["landform"]==4, "landform"] = 6 # plains

# recharge vs slope
x_name = "slope_30s"
y_name = "Recharge"
x_unit = " [mm/y]"
y_unit = " [m]"
sns.set(rc={'figure.figsize': (4, 4)})
sns.set_style("ticks")
g = sns.FacetGrid(df, col="dummy", col_wrap=4)
g.map_dataframe(plt.scatter, x_name, y_name, color="silver", marker='o', lw=0, alpha=0.5, s=5, label=None)
g.set(xlim=[0.0001, 1], ylim=[0, 1000])
g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:blue", group_type="dummy", group="")
g.set(xlabel = "Slope" + x_unit, ylabel = y_name + y_unit)
g.set_titles(col_template='{col_name}')
g.set(xscale='log', yscale='linear')
#plt.legend(loc='upper right')
plt.savefig(results_path + x_name + '_' + y_name + "_distribution.png", dpi=600, bbox_inches='tight')
plt.close()

# landform distribution
df_tmp = df["landform"]
print("Distribution landforms")
print("Humid and plains " + ": " + str(
    round(len(df_tmp[np.logical_and(df["landform"]==6, df["aridity_30s"]<1)]) / len(df_tmp), 2)))
print("Arid and plains " + ": " + str(
    round(len(df_tmp[np.logical_and(df["landform"]==6, df["aridity_30s"]>1)]) / len(df_tmp), 2)))
print("Humid and mountains " + ": " + str(
    round(len(df_tmp[np.logical_and(df["landform"]==5, df["aridity_30s"]<1)]) / len(df_tmp), 2)))
print("Arid and mountains " + ": " + str(
    round(len(df_tmp[np.logical_and(df["landform"]==5, df["aridity_30s"]>1)]) / len(df_tmp), 2)))
