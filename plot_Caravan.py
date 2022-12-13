import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from scipy import stats
import seaborn as sns
from functions import plotting_fcts
from functions import get_nearest_neighbour
import geopandas as gpd
from shapely.geometry import Point
import rasterio as rio
from pingouin import partial_corr

# This script ...

# prepare data
data_path = "data/complete_table.csv" #"D:/Data/Caravan/complete_table.csv" #
#data_path = "data/attributes/camels/attributes_hydroatlas_camels.csv"
#data_path = "data/attributes/hysets/attributes_hydroatlas_hysets.csv"

# check if folder exists
results_path = "results/Caravan/"
if not os.path.isdir(results_path):
    os.makedirs(results_path)

# load and process data
df = pd.read_csv(data_path, sep=',')

df["dummy"] = ""

# slope
x_name = "slope"
y_name = "BFI"
x_unit = " [deg]"
y_unit = " [-]"
df["aridity_class"] = "energy-limited"
df.loc[100/df["ari_ix_sav"] > 1, "aridity_class"] = "water-limited"
df["slope"] = df["slp_dg_sav"] * 0.1#np.tan(np.deg2rad(df['slp_dg_sav'] * 0.1)) #
sns.set(rc={'figure.figsize': (4, 4)})
sns.set_style("ticks")
g = sns.FacetGrid(df, col="dummy", col_wrap=4)
g.map_dataframe(plt.scatter, x_name, y_name, color="silver", marker='o', lw=0, alpha=1, s=5, label=None)
g.set(xlim=[0.1, 100], ylim=[0, 1])
#g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:blue", group_type="aridity_class", group="energy-limited")
#g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:orange", group_type="aridity_class", group="water-limited")
g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:red", group_type="dummy", group="")
g.add_legend(loc=(.2, .75), handletextpad=0.0)
# results_df = plotting_fcts.binned_stats_table(df, x_name, y_name, sources)
g.set(xlabel = x_name + x_unit, ylabel = y_name + y_unit)
g.set_titles(col_template='{col_name}')
g.set(xscale='log', yscale='linear')
plt.savefig(results_path + x_name + '_' + y_name + "_aridity.png", dpi=600, bbox_inches='tight')
plt.close()

r, p = stats.spearmanr(df[x_name], df[y_name])
print(str(np.round(r,2)), str(np.round(p,2)))
r_partial_mat = partial_corr(data=df, x=x_name, y=y_name, covar="frac_snow", method='spearman')
print(str(np.round(r_partial_mat,2)))


# slope
x_name = "slope"
y_name = "BFI"
z_name = "frac_snow"
x_unit = " [deg]"
y_unit = " [-]"
df["aridity_class"] = "energy-limited"
df.loc[100/df["ari_ix_sav"] > 1, "aridity_class"] = "water-limited"
df["slope"] = np.tan(np.deg2rad(df['slp_dg_sav'] * 0.1)) #df["slp_dg_sav"] * 0.1#
sns.set(rc={'figure.figsize': (4, 4)})
sns.set_style("ticks")
df["hue"] = np.round(df[z_name],2) # to have fewer unique values
g = sns.FacetGrid(df, col="dummy", hue="hue", palette="viridis", col_wrap=4)
g.map_dataframe(sns.scatterplot, x_name, y_name, marker='o', lw=0, alpha=1, s=5, label=None)
#plt.scatter(df[x_name], df[y_name], marker='o', lw=0, alpha=1, s=5, label=None)
g.set(xlim=[0.001, 1], ylim=[0, 1])
#g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:blue", group_type="aridity_class", group="energy-limited")
#g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:orange", group_type="aridity_class", group="water-limited")
#g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:red", group_type="dummy", group="")
#g.add_legend(loc=(.2, .75), handletextpad=0.0)
# results_df = plotting_fcts.binned_stats_table(df, x_name, y_name, sources)
g.set(xlabel = x_name + x_unit, ylabel = y_name + y_unit)
g.set_titles(col_template='{col_name}')
g.set(xscale='log', yscale='linear')
plt.savefig(results_path + x_name + '_' + y_name + "_frac_snow.png", dpi=600, bbox_inches='tight')
plt.close()

r, p = stats.spearmanr(df[x_name], df[y_name])
print(str(np.round(r,2)), str(np.round(p,2)))
r_partial_mat = partial_corr(data=df, x=x_name, y=y_name, covar="frac_snow", method='spearman')
print(str(np.round(r_partial_mat,2)))

# stream gradient
x_name = "sgr_dk_sav"
y_name = "BFI"
x_unit = " [deg]"
y_unit = " [-]"
df["aridity_class"] = "energy-limited"
df.loc[100/df["ari_ix_sav"] > 1, "aridity_class"] = "water-limited"
sns.set(rc={'figure.figsize': (4, 4)})
sns.set_style("ticks")
g = sns.FacetGrid(df, col="dummy", col_wrap=4)
g.map_dataframe(plt.scatter, x_name, y_name, color="silver", marker='o', lw=0, alpha=1, s=5, label=None)
#g.set(xlim=[1/1000, 1000/1000], ylim=[0, 1])
#g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:blue", group_type="aridity_class", group="energy-limited")
#g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:orange", group_type="aridity_class", group="water-limited")
g.map_dataframe(plotting_fcts.plot_bins_group, x_name, y_name, color="tab:red", group_type="dummy", group="")
g.add_legend(loc=(.2, .75), handletextpad=0.0)
# results_df = plotting_fcts.binned_stats_table(df, x_name, y_name, sources)
g.set(xlabel = x_name + x_unit, ylabel = y_name + y_unit)
g.set_titles(col_template='{col_name}')
g.set(xscale='log', yscale='linear')
plt.savefig(results_path + x_name + '_' + y_name + "_aridity.png", dpi=600, bbox_inches='tight')
plt.close()


# test for partial correlation
fig = plt.figure(figsize=(3, 2))
ax = plt.axes()
plt.grid(color='grey', linestyle='--', linewidth=0.25)
count, bins_count = np.histogram(df["slope"], bins=1000)
pdf = count / sum(count)
cdf = np.cumsum(pdf)
plt.plot(bins_count[1:], cdf, color="grey", label="Global distribution")
ax.set_xlabel("Slope [m/m]")
ax.set_ylabel("Cumulative probability [-]")
ax.set_xlim([0, 0.5])
plt.savefig(results_path + "slope_histogram.png", dpi=600, bbox_inches='tight')
plt.close()
