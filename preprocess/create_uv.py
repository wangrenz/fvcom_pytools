#!/public/home/xdqx/app/miniconda3/envs/metenv/bin/python
# -*- coding: utf-8 -*-
import os,sys
import time,glob
import f90nml
from datetime import datetime, timedelta
import numpy as np
import xarray as xr


class wind(object):
    # 经纬度信息文件
    _ll_path = "/public/home/xdqx/fvcom_cn_real/scripts/lat_lon_cn.nc"
    def __init__(self, starttime, ndays):
        _uv_delta  = 1   # delta hours 
        self.times = [ starttime + timedelta(hours=i) for i in range(0, ndays*24 + _uv_delta, _uv_delta ) ]
        self.times_julian = [ (i - datetime(1858,11,17)  ).total_seconds()/(60*60*24) for i in self.times ]
        self.era5_src_path = "/public/home/xdqx/data/ERA5/2018/10muv.grib"
        self.get_era5()
        self.write_uv()

    # 读取ERA5风场数据
    def get_era5(self,):
        # 读取模式node的经纬度
        ds_ll = xr.open_dataset(self._ll_path)
        # 读取ERA5风场数据
        ds_era5 = xr.open_dataset(self.era5_src_path,engine='cfgrib',backend_kwargs={'indexpath':''})
        ds_era5 = ds_era5.sel(time= np.array(self.times, dtype='datetime64') )
        ds_era5 = ds_era5.drop(["number","step","surface","valid_time"])
        print(ds_era5)
        print(ds_ll)
        self.u10 = ds_era5.u10.interp(latitude=ds_ll.latc,longitude=ds_ll.lonc,method='linear')  # nearest
        self.v10 = ds_era5.v10.interp(latitude=ds_ll.latc,longitude=ds_ll.lonc,method='linear')
        self.u10_node = ds_era5.u10.interp(latitude=ds_ll.lat,longitude=ds_ll.lon,method='linear')  # nearest
        self.v10_node = ds_era5.v10.interp(latitude=ds_ll.lat,longitude=ds_ll.lon,method='linear')
        print("print u10:")
        print(self.u10)

    def write_uv(self,):
        time_org      = np.array(self.times_julian, dtype='f4')
        Itime_org     = np.array(self.times_julian, dtype='i4')
        Itime2_org    = np.round(( (time_org%1)*24*3600*1000)/(3600*1000))*(3600*1000)
        self.ds =  xr.Dataset({'time':(['time'], time_org), 'Itime':(['time'], Itime_org), 'Itime2':(['time'], Itime2_org), \
            'U10':(['time','nele'], self.u10), 'V10':(['time','nele'], self.v10), \
            'U10_node':(['time','node'], self.u10_node), 'V10_node':(['time','node'], self.v10_node) } )
        self.ds.attrs['source']             = "fvcom grid (unstructured) surface forcing"
        self.ds['time'].encoding            = {'dtype': 'f4','_FillValue': None}
        self.ds['time'].attrs['long_name']  = 'time'
        self.ds['time'].attrs['units']      = 'days since 1858-11-17 00:00:00'
        self.ds['time'].attrs['format']     = "modified julian day (MJD)"
        self.ds['time'].attrs['time_zone']  = 'UTC'

        self.ds['Itime'].encoding           = {'dtype': 'i4','_FillValue': None}
        self.ds['Itime'].attrs['units']     = 'days since 1858-11-17 00:00:00'

        self.ds['Itime2'].encoding          = {'dtype': 'i4','_FillValue': None}
        self.ds['Itime2'].attrs['units']    = 'msec since 00:00:00'

        self.ds['U10'].encoding             = {'dtype': 'f4','_FillValue': None}
        self.ds['U10'].attrs['units']       = 'm/s'

        self.ds['V10'].encoding             = {'dtype': 'f4','_FillValue': None}
        self.ds['V10'].attrs['units']       = 'm/s'

        self.ds['U10_node'].encoding             = {'dtype': 'f4','_FillValue': None}
        self.ds['U10_node'].attrs['units']       = 'm/s'

        self.ds['V10_node'].encoding             = {'dtype': 'f4','_FillValue': None}
        self.ds['V10_node'].attrs['units']       = 'm/s'
        print("output ds details: ")
        print(self.ds)
        self.ds.to_netcdf('era5_uv.nc', unlimited_dims=['time'],engine="scipy")



if __name__ == '__main__':
   
    os.environ['NCARG_ROOT'] = "/public/home/xdqx/app/ncl"
    os.environ['PATH'] += ":/public/home/xdqx/app/ncl/bin" 
    starttime = datetime(2018,1,1,0)
    # 制作风场驱动
    wind(starttime, 30)

        
