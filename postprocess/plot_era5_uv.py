# -*- coding: utf-8 -*-
# import cmaps
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import xarray as xr
# from multiprocessing import Pool
# from multiprocessing.dummy import Pool  #  as ThreadPool 

    
class plot_era5(object):
    era5_path    = "/public/home/xdqx/data/ERA5/2018/10muv.grib"
    fig_path     = "/public/home/xdqx/fvcom_cn_real/output/figure/era5/"

    def __init__(self,):
        # 读取文件
        self._read_era5()
        times_len = self.ds.time.shape[0]
        
        for it in range(200, 745):
            self._plot_uv(it)


    def _read_era5(self,):
        self.ds = xr.open_dataset(self.era5_path, engine='cfgrib' )

    def _plot_uv(self, it):
        colors = np.array( [ [255,255,255],[142,106,219],[0,18,153], [2,66,227], [0,170,255], [0,233,255], \
            [57,153,31], [149,255,127], [246,255,0], [255,190,0], [255,84,0], [191,0,0], [255,0,128]] ,dtype='f4')
        cmap = mpl.colors.ListedColormap(colors/255., name='rain_cmap')
        levels =np.array([1.6,3.4,5.5,8,10.8,13.9,17.2,20.8,24.5,32.7,41.5,51],dtype='f4')
        lon = self.ds.longitude.values
        lat = self.ds.latitude.values
        u = self.ds.u10.isel(time=it)
        v = self.ds.v10.isel(time=it)
        magnitude = (u ** 2 + v ** 2) ** 0.5

        plt.figure(figsize=(11,11),dpi=130)
        ax = plt.axes(projection=ccrs.PlateCarree())

        land = cfeature.NaturalEarthFeature('physical', 'land', '10m',edgecolor='face',facecolor=cfeature.COLORS['land'])
        ax.add_feature(land,facecolor='0.85')
        ax.coastlines('10m',linewidth=0.3, alpha=0.6)

        space = 5
        im = magnitude.plot.contourf(ax=ax,xlim=(105.2, 127.5), ylim=( 15,  41.5),extend='both',levels=levels, cmap=cmap,cbar_kwargs={'cax':inset_axes(ax, width="2.7%", height="55%", loc=2),'label': '','ticks': levels,'extendfrac': 'auto' }, transform=ccrs.PlateCarree())
        ax.barbs(lon[::space], lat[::space], u[::space,::space]*2.5, v[::space,::space]*2.5, sizes=dict(emptybarb=0), length=5, linewidth=0.3,pivot='middle', transform= ccrs.PlateCarree())



        # ax.set_title('h (m)')
        ax.set_xticks( np.arange(100,130,2.5), crs=ccrs.PlateCarree())
        ax.set_yticks( np.arange(10,  50,2.5), crs=ccrs.PlateCarree())
        #lon_formatter = LongitudeFormatter(zero_direction_label=True)
        lon_formatter = LongitudeFormatter()
        lat_formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)

        ax.set_xlim(105.2, 127.5)
        ax.set_ylim( 15,    41.5)

        ax.set_xlabel('')
        ax.set_ylabel('')
        print(self.ds.time.isel(time=it).dt.round("H") )
        time_str = np.datetime_as_string( self.ds.time.isel(time=it).dt.round("H"), unit='h')
        ax.set_title( time_str )
        fullpath = os.path.join(self.fig_path, "era5", "uv_" + time_str + ".png")
        print(fullpath)
        if not os.path.exists( os.path.dirname(fullpath) ):
            os.makedirs(os.path.dirname(fullpath))
        plt.savefig(fullpath, bbox_inches='tight')
        plt.close("all")

if __name__ == "__main__":
    '''
    该程序用来批量可视化ERA5的输出产品
    '''
    plot_era5()
