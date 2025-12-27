from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.crs as ccrs


plt.rcParams['font.sans-serif'] = ['Lolita']
data_raw = Path(r"D:\Desktop\Desktop\52HZ\src\GIS")
geojson_files = {
    "countries": data_raw / "ne_110m_admin_0_countries.url.geojson",
    "ocean": data_raw / "ne_110m_ocean.url.geojson",
    "ports": data_raw / "UpdatedPub150.url.geojson"
}

countries_gdf = gpd.read_file(geojson_files["countries"])
ocean_gdf = gpd.read_file(geojson_files["ocean"])
ports_gdf = gpd.read_file(geojson_files["ports"])

fig, ax = plt.subplots(figsize=(25, 15), subplot_kw={'projection': ccrs.PlateCarree()})

lon_min, lon_max = -180, 180
lat_min, lat_max = -90, 90

countries_gdf.plot(ax=ax, color='green', edgecolor='black', linewidth=1, transform=ccrs.PlateCarree())
ocean_gdf.plot(ax=ax, color='blue', edgecolor='black', linewidth=1, transform=ccrs.PlateCarree())
ports_gdf.plot(ax=ax, color='yellow', markersize=1.5, transform=ccrs.PlateCarree())

ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', alpha=0.67, linestyle='--')
gl.top_labels = gl.bottom_labels = gl.left_labels = gl.right_labels = True
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 16, 'color': 'black'}
gl.ylabel_style = {'size': 16, 'color': 'black'}

plt.savefig("background_map.png", dpi=480)
plt.show()
