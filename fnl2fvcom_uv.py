#!/bin/env python
import os,sys
from datetime import datetime, timedelta
import numpy as np
from scipy import interpolate
from scipy.io import netcdf
import pygrib


def read_grib(fnl_path, ndays, u10, v10):
	lon_lat = np.genfromtxt('/public/home/njxdqx/model/fvcom-exec/input/nele_lon_lat.txt',dtype='f')

	file_list = [ fnl_path + "gfs.pgrb2.0p25.f"+ "{0:03d}".format(i) +".grib2" for i in range(0, ndays*24+6, 6 ) ]
	for i in range(len(file_list)):
		grb = pygrib.open(file_list[i])
		print("read " + file_list[i])
		U10 = grb.select(name='U component of wind')[0]  # (721, 1440)
		V10 = grb.select(name='V component of wind')[0]
		lat, lon = U10.latlons()
		#--------------------grid lat lon ------------point lat lon
		u10 = interpolate.interpn((lat[::-1,0], lon[0]), U10.values[::-1,:], lon_lat[:,::-1], method='linear')
		v10 = interpolate.interpn((lat[::-1,0], lon[0]), U10.values[::-1,:], lon_lat[:,::-1], method='linear')
		if i == 0:
			u10_r = u10
			v10_r = v10
		else:
			u10_r =  np.vstack((u10_r, u10))
			v10_r =  np.vstack((v10_r, v10))
	print(u10_r.shape)
	return u10_r, v10_r

# -- MAIN
if __name__ == '__main__':
	global nele_path,nnele,nnode
	nele_path = "/public/home/njxdqx/model/fvcom-exec/input/nele_lon_lat.txt"
	nnode = 2361
	nnele = 4448
	if len(sys.argv) < 4:
	  print('Usage: fnl2fvcom_uv.py <fnl_path> <ndays> <start_ymdh>')
	  sys.exit(0)
	fnl_path = sys.argv[1]
	ndays = int(sys.argv[2])
	ymdh  = sys.argv[3]
	
	starttime = datetime.strptime(ymdh,"%Y%m%d%H")
	timeref = datetime(1858,11,17)
	
	times = [ starttime + timedelta(hours=i) for i in range(0, ndays*24+6, 6 ) ]
	times = [ (i - timeref  ).total_seconds()/(60*60*24) for i in times ]
	
	time_org  = np.array(times, dtype='f4')
	Itime_org = np.array(times, dtype='i4')
	Itime2_org= np.round(( (time_org%1)*24*3600*1000)/(3600*1000))*(3600*1000)
	print(time_org)
	print(Itime_org)
	print(Itime2_org)
	
	u10_r = np.zeros(time_org.shape[0],dtype='f')
	v10_r = np.zeros(time_org.shape[0],dtype='f')
	u10_r, v10_r = read_grib(fnl_path, ndays, u10_r, v10_r)
	# f_r = netcdf.netcdf_file('../input/uv_ncl.nc','r')
	# u10_r = f_r.variables['U10']
	# v10_r = f_r.variables['V10']
	# f_r.close()
	
	
	f = netcdf.netcdf_file('uv_force.nc', 'w')
	f.source = "fvcom grid (unstructured) surface forcing"
	
	f.createDimension('time', None)
	f.createDimension('node', nnode )
	f.createDimension('nele', nnele )
	
	time = f.createVariable('time', 'f', ('time',))
	time[:] = time_org
	time.long_name = "time"
	time.units = 'days since 1858-11-17 00:00:00'
	time.format = "modified julian day (MJD)"
	time.time_zone = "UTC"
	Itime = f.createVariable('Itime', 'i', ('time',))
	Itime[:] = Itime_org
	Itime.units = 'days since 1858-11-17 00:00:00'
	
	Itime2 = f.createVariable('Itime2', 'i', ('time',))
	Itime2[:] = Itime2_org.astype('i4')
	Itime2.units = 'msec since 00:00:00'
	
	u10    = f.createVariable('U10', 'f', ('time','nele',))
	u10[:] = u10_r[:]
	u10.long_name = "Eastward 10-m Velocity"
	u10.units = "m/s"
	v10    = f.createVariable('V10', 'f', ('time','nele',))
	v10[:] = v10_r[:]
	v10.long_name = "Northward 10-m Velocity"
	v10.units = "m/s"
	
	f.close()
	
