# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.tri as mtri
from scipy import interpolate
from scipy.io import netcdf
from datetime import datetime, timedelta
import xarray as xr


class write_hycom_ts(object):

    def __init__(self, starttime, ndays):
        _ts_delta  = 24
        lat_lon    = np.genfromtxt('/public/home/njxdqx/FVCOM_js_real/scripts/node_lon_lat.txt',dtype='f')
        self.lat   = lat_lon[:,1]
        self.lon   = lat_lon[:,0]
        self.nnode = self.lat.shape[0]
        latc_lonc  = np.genfromtxt('/public/home/njxdqx/FVCOM_js_real/scripts/nele_lon_lat.txt',dtype='f')
        self.latc  = latc_lonc[:,1]
        self.lonc  = latc_lonc[:,0]
        self.times = [ starttime + timedelta(hours=i) for i in range(0, ndays*24 + _ts_delta, _ts_delta ) ]
        self.times_julian = [ (i - datetime(1858,11,17)  ).total_seconds()/(60*60*24) for i in self.times ]
        self.hycom_src_path = '/public/home/njxdqx/data/Hycom/2018/'

        self.get_hycom()
        self.write_ts()


    def get_hycom(self, ):
        lat = xr.DataArray(self.lat, dims='node', coords={'node': np.linspace(1, self.nnode, self.nnode)})
        lon = xr.DataArray(self.lon, dims='node', coords={'node': np.linspace(1, self.nnode, self.nnode)})
        for it in range(len(self.times)):
            print(it)
            ds  = xr.open_dataset(os.path.join(self.hycom_src_path,'hycom_glbv_930_%s_t000_ts3z.nc' % self.times[it].strftime('%Y%m%d%H')),decode_times=False)
            if it == 0:
                self.zsl = ds.depth.values
                self.tsl   = ds.water_temp.interp(lat=lat,lon=lon,method='nearest')
                self.ssl   = ds.salinity.interp(lat=lat,lon=lon,method='nearest')
                # self.tsl = interpolate.interpn((ds.depth.values, ds.lat.values, ds.lon.values), ds.water_temp.values[0,:,:,:], (self.zsl,self.lat,self.lon), method='nearest')
                # self.ssl = interpolate.interpn((ds.depth.values, ds.lat.values, ds.lon.values), ds.salinity.values[0,:,:,:],   (self.zsl,self.lat,self.lon), method='nearest')
            else:
                self.tsl   = self.tsl.combine_first(ds.water_temp.interp(lat=lat,lon=lon,method='nearest'))
                self.ssl   = self.ssl.combine_first(ds.salinity.interp(lat=lat,lon=lon,method='nearest'))
                # self.tsl   = np.vstack((self.tsl, ds.water_temp.interp(lat=lat,lon=lon,method='nearest').values))
                # self.ssl   = np.vstack((self.ssl, ds.salinity.interp(lat=lat,lon=lon,method='nearest').values))
                # self.tsl = np.vstack((self.tsl, interpolate.interpn((ds.lat.values, ds.lon.values), ds.water_temp.values[0,:,:,:], np.vstack([self.zsl,self.lat,self.lon]).T, method='nearest')))
                # self.ssl = np.vstack((self.ssl, interpolate.interpn((ds.lat.values, ds.lon.values), ds.salinity.values[0,:,:,:], np.vstack([self.zsl,self.lat,self.lon]).T, method='nearest')))				
    def write_ts(self, ):
        time_org      = np.array(self.times_julian, dtype='f4')
        Itime_org     = np.array(self.times_julian, dtype='i4')
        Itime2_org    = np.round(( (time_org%1)*24*3600*1000)/(3600*1000))*(3600*1000)
        print(type(Itime2_org))

        self.ds = xr.Dataset({'time':(['time'], time_org), 'Itime':(['time'], Itime_org), 'Itime2':(['time'], Itime2_org), \
            'zsl':(['ksl'], self.zsl), 'tsl':(['time','ksl','node'], self.tsl.values), 'ssl':(['time','ksl','node'], self.ssl.values)  } )
        
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

        self.ds['zsl'].encoding             = {'dtype': 'f4','_FillValue': None}
        self.ds['zsl'].attrs['long_name']   = "standard z levels positive up"
        self.ds['zsl'].attrs['units']       = 'meters'

        self.ds['tsl'].encoding             = {'dtype': 'f4','_FillValue': 10}
        self.ds['tsl'].attrs['long_name']   = "observed_temperature_profile"
        self.ds['tsl'].attrs['units']       = 'C'

        self.ds['ssl'].encoding             = {'dtype': 'f4','_FillValue': 0}
        self.ds['ssl'].attrs['long_name']   = "observed_salinity_profile"
        self.ds['ssl'].attrs['units']       = 'PSU'
        self.ds.to_netcdf('ts_hycom.nc', unlimited_dims=['time'])

        # self.f = netcdf.netcdf_file('ts_hycom.nc', 'w')
        # self.f.source = "fvcom grid (unstructured) surface forcing"
        
        # self.f.createDimension('time', None)
        # self.f.createDimension('ksl',  self.zsl.shape[0])
        # self.f.createDimension('node', self.nnode)	
        
        # time          = self.f.createVariable('time', 'f', ('time',))
        # time[:]       = time_org
        # time.long_name= "time"
        # time.units    = 'days since 1858-11-17 00:00:00'
        # time.format   = "modified julian day (MJD)"
        # time.time_zone= "UTC"
        
        # Itime         = self.f.createVariable('Itime', 'i', ('time',))
        # Itime[:]      = Itime_org
        # Itime.units   = 'days since 1858-11-17 00:00:00'	
        
        # Itime2        = self.f.createVariable('Itime2', 'i', ('time',))
        # Itime2[:]     = Itime2_org.astype('i4')
        # Itime2.units  = 'msec since 00:00:00'

        # zsl           = self.f.createVariable('zsl', 'f', ('ksl',))
        # zsl[:]        = self.zsl
        # zsl.long_name = "standard z levels positive up"
        # zsl.units     = "meters"

        # tsl           = self.f.createVariable('tsl', 'f', ('time','ksl','node'))
        # tsl[:]        = self.tsl
        # tsl.long_name = "observed_temperature_profile"
        # tsl.units     = "C"
        # ssl           = self.f.createVariable('ssl', 'f', ('time','ksl','node'))
        # ssl[:]        = self.ssl
        # ssl.long_name = "observed_salinity_profile"
        # ssl.units     = "PSU"	
        # self.f.close()

if __name__ == '__main__':

    write_hycom_ts(datetime.strptime('2018010112','%Y%m%d%H'), 4)