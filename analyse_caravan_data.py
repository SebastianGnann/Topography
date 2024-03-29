import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from scipy import stats
import seaborn as sns
from functions import plotting_fcts
import rasterio as rio
from pingouin import partial_corr

# Plots Caravan signatures against catchment attributes, e.g. BFI against slope and calculates the fraction of observations in each landform.

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

caravan_path = "data/complete_table.csv"

# check if folder exists
results_path = "results/Caravan/"
if not os.path.isdir(results_path):
    os.makedirs(results_path)

# load and process data
df = pd.read_csv(caravan_path, sep=',')

coord_list = [(x, y) for x, y in zip(df['gauge_lon'], df['gauge_lat'])]

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

df["aridity_30s"] = df["pet_30s"]/df["pr_30s"]

df["dummy"] = ""

#df = df.dropna()

# BFI per landform
print("BFI per landform")
print("Plains " + ": " + str(round(df.loc[df["landform"]==4, "BFI"].mean(), 2)))
print("Tablelands " + ": " + str(round(df.loc[df["landform"]==3, "BFI"].mean(), 2)))
print("Hills " + ": " + str(round(df.loc[df["landform"]==2, "BFI"].mean(), 2)))
print("Mountains " + ": " + str(round(df.loc[df["landform"]==1, "BFI"].mean(), 2)))
#print("Uplands " + ": " + str(round(df.loc[np.logical_or(df["landform"]==1, df["landform"]==2, df["landform"]==3), "BFI"].mean(), 2)))
print("Uplands " + ": " + str(round(df.loc[df["landform"]<4, "BFI"].mean(), 2)))

# landform distribution
print("Distribution landforms")
print("Plains " + ": " + str(
    round(len(df[df["landform"]==4]) / len(df), 2)))
print("Tablelands " + ": " + str(
    round(len(df[df["landform"]==3]) / len(df), 2)))
print("Hills " + ": " + str(
    round(len(df[df["landform"]==2]) / len(df), 2)))
print("Mountains " + ": " + str(
    round(len(df[df["landform"]==1]) / len(df), 2)))

# stream order distribution
print("Distribution landforms")
print("Plains " + ": " + str(
    round(len(df[df["landform"]==4]) / len(df), 2)))
print("Tablelands " + ": " + str(
    round(len(df[df["landform"]==3]) / len(df), 2)))
print("Hills " + ": " + str(
    round(len(df[df["landform"]==2]) / len(df), 2)))
print("Mountains " + ": " + str(
    round(len(df[df["landform"]==1]) / len(df), 2)))

# reclassify landforms
df.loc[df["landform"]==1, "landform"] = 5 # mountains
df.loc[df["landform"]==2, "landform"] = 5 # hills
df.loc[df["landform"]==3, "landform"] = 5 # plateaus
df.loc[df["landform"]==4, "landform"] = 6 # plains

df["slope"] = df["slp_dg_sav"] * 0.1#np.tan(np.deg2rad(df['slp_dg_sav'] * 0.1)) #
df["aridity_class"] = "energy-limited"
df.loc[100/df["ari_ix_sav"] > 1, "aridity_class"] = "water-limited"

# BFI vs slope
x_name = "slope"
y_name = "BFI"
sns.set(rc={'figure.figsize': (4, 4)})
sns.set_style("ticks")
g = sns.FacetGrid(df, col="dummy", col_wrap=4)
g.map_dataframe(plt.scatter, x_name, y_name, color="silver", marker='o', lw=0, alpha=0.5, s=5, label=None)
g.set(xlim=[0.1, 45], ylim=[0, 1])
g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:blue", group_type="dummy", group="")
#g.add_legend(loc=(.2, .75), handletextpad=0.0)
# results_df = plotting_fcts.binned_stats_table(df, x_name, y_name, sources)
g.set(xlabel = "Slope [deg]" , ylabel = "Baseflow Index [-]")
g.set_titles(col_template='{col_name}')
g.set(xscale='log', yscale='linear')
plt.savefig(results_path + x_name + '_' + y_name + ".png", dpi=600, bbox_inches='tight')
plt.close()

print(x_name + " and " + y_name)
r, p = stats.spearmanr(df[x_name], df[y_name])
print(str(np.round(r,2)))
r_partial_mat = partial_corr(data=df, x=x_name, y=y_name, covar="frac_snow", method='spearman')
print(str(np.round(r_partial_mat.r.values[0],2)))
r_partial_mat = partial_corr(data=df, x=x_name, y=y_name, covar="ari_ix_sav", method='spearman')
print(str(np.round(r_partial_mat.r.values[0],2)))

# baseflow magnitude vs slope
x_name = "slope"
y_name = "BaseflowMagnitude"
sns.set(rc={'figure.figsize': (4, 4)})
sns.set_style("ticks")
g = sns.FacetGrid(df, col="dummy", col_wrap=4)
g.map_dataframe(plt.scatter, x_name, y_name, color="silver", marker='o', lw=0, alpha=1, s=5, label=None)
g.set(xlim=[0.1, 45], ylim=[0, 5])
g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:blue", group_type="dummy", group="")
#g.add_legend(loc=(.2, .75), handletextpad=0.0)
# results_df = plotting_fcts.binned_stats_table(df, x_name, y_name, sources)
g.set(xlabel = "Slope [deg]" , ylabel = "Baseflow Variability [mm/d]")
g.set_titles(col_template='{col_name}')
g.set(xscale='log', yscale='linear')
plt.savefig(results_path + x_name + '_' + y_name + ".png", dpi=600, bbox_inches='tight')
plt.close()

print(x_name + " and " + y_name)
r, p = stats.spearmanr(df[x_name], df[y_name], nan_policy='omit')
print(str(np.round(r,2)))
r_partial_mat = partial_corr(data=df, x=x_name, y=y_name, covar="frac_snow", method='spearman')
print(str(np.round(r_partial_mat.r.values[0],2)))
r_partial_mat = partial_corr(data=df, x=x_name, y=y_name, covar="ari_ix_sav", method='spearman')
print(str(np.round(r_partial_mat.r.values[0],2)))

# normalised baseflow magnitude vs slope
df["NormalizedBaseflowMagnitude"] = df["BaseflowMagnitude"]/df["Qmean"]
x_name = "slope"
y_name = "NormalizedBaseflowMagnitude"
sns.set(rc={'figure.figsize': (4, 4)})
sns.set_style("ticks")
g = sns.FacetGrid(df, col="dummy", col_wrap=4)
g.map_dataframe(plt.scatter, x_name, y_name, color="silver", marker='o', lw=0, alpha=1, s=5, label=None)
g.set(xlim=[0.1, 45], ylim=[0, 2])
g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:blue", group_type="dummy", group="")
#g.add_legend(loc=(.2, .75), handletextpad=0.0)
# results_df = plotting_fcts.binned_stats_table(df, x_name, y_name, sources)
g.set(xlabel = "Slope [deg]" , ylabel = "Norm. Baseflow Variability [-]")
g.set_titles(col_template='{col_name}')
g.set(xscale='log', yscale='linear')
plt.savefig(results_path + x_name + '_' + y_name + ".png", dpi=600, bbox_inches='tight')
plt.close()

print(x_name + " and " + y_name)
r, p = stats.spearmanr(df[x_name], df[y_name], nan_policy='omit')
print(str(np.round(r,2)))
r_partial_mat = partial_corr(data=df, x=x_name, y=y_name, covar="frac_snow", method='spearman')
print(str(np.round(r_partial_mat.r.values[0],2)))
r_partial_mat = partial_corr(data=df, x=x_name, y=y_name, covar="ari_ix_sav", method='spearman')
print(str(np.round(r_partial_mat.r.values[0],2)))

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

