# -*- coding: utf-8 -*-
# import cmaps
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import matplotlib.tri as tri
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import xarray as xr



class plot_zeta(object):
    fvcom_output = "/public/home/xdqx/fvcom_cn_real/output/a_0001.nc"
    fig_path     = "/public/home/xdqx/fvcom_cn_real/output/figure/"

    def __init__(self,):
        # 读取文件
        self._read_fvcom()
        times_len = self.ds.time.shape[0]
        for it in range(0, times_len):
            self._plot(it)


    def _read_fvcom(self,):
        drop_var = ["siglay","siglev","Itime","Itime2"]
        self.ds = xr.open_dataset(self.fvcom_output, drop_variables=drop_var)

    def _plot(self, it):
        #colors = np.array( [ [255,255,255], [1,160,246], [0,236,236], [0,216,0], [1,144,0], \
        #    [255,255,0], [231,192,0],[255,144,0],[255,0,0] ,[214,0,0],[192,0,0], [255,0,240], [150,0,180],[173,144,240] ] ,dtype='f4')
        # #levels  = np.arange(5,70,5)  /10    # np.array([5,10,20,30,40,50,60,70,80,90,100,110, 120]) # np.arange(5,70,5)        
        # levels  = np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.8,1,1.2,1.4,1.6,1.8, 2])
        # cmap , norm = mpl.colors.from_levels_and_colors(levels, colors/255, extend='both' )
        levels = np.arange(-80, 90, 10)
        #cmap = mpl.cm.get_cmap(name='terrain_r', lut=None)
        cmap = mpl.cm.get_cmap('PiYG')
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
        
        triang = tri.Triangulation(self.ds.lon, self.ds.lat, self.ds.nv.transpose()-1)

        plt.figure(figsize=(11,11),dpi=130)
        ax = plt.axes(projection=ccrs.PlateCarree())

        land = cfeature.NaturalEarthFeature('physical', 'land', '10m',edgecolor='face',facecolor=cfeature.COLORS['land'])
        ax.add_feature(land,facecolor='0.85')
        ax.coastlines('10m',linewidth=0.3, alpha=0.6)

        ax.triplot(triang, color='k', linewidth = 0.1, alpha=0.1)
        # im = ax.tripcolor(triang, self.ds.hs.isel(time=it),  transform=ccrs.PlateCarree())
        im = ax.tripcolor(triang, self.ds.zeta.isel(time=it) * 100, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
        #im = ax.tricontourf(triang, self.ds.hs.isel(time=it), extend="both",levels=levels, cmap=cmap, transform=ccrs.PlateCarree())
        clb = plt.colorbar(im,  cax=inset_axes(ax, width="4%", height="50%",loc=2,borderpad=1), extend='both',extendfrac='auto',extendrect=False ) 
        clb.ax.tick_params(axis='y', length=0., width=0.3,direction='in',labelsize=10)
        clb.ax.set_title('zeta (cm)', horizontalalignment='left', position=(2.2, 0.5))


        # ax.set_title('h (m)')
        ax.set_xticks( np.arange(100,130,2.5), crs=ccrs.PlateCarree())
        ax.set_yticks( np.arange(10,  50,2.5), crs=ccrs.PlateCarree())
        #lon_formatter = LongitudeFormatter(zero_direction_label=True)
        lon_formatter = LongitudeFormatter()
        lat_formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)

        ax.set_xlim(105.2, 127.5)
        ax.set_ylim( 13.5,    41.5)

        ax.set_xlabel('')
        ax.set_ylabel('')
        print(self.ds.time.isel(time=it).dt.round("H") )
        time_str = np.datetime_as_string( self.ds.time.isel(time=it).dt.round("H"), unit='h')
        ax.set_title( time_str )
        fullpath = os.path.join(self.fig_path, "zeta", "zeta_" + time_str + ".png")
        print(fullpath)
        if not os.path.exists( os.path.dirname(fullpath) ):
            os.makedirs(os.path.dirname(fullpath))
        plt.savefig(fullpath, bbox_inches='tight')
        plt.close("all")
    
    def _plot_zeta(self,):
        pass

if __name__ == "__main__":
    '''
    该程序用来批量可视化FVCOM的输出产品
    '''
    plot_zeta()
