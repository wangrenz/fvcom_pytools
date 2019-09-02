#!/bin/env python
import sys
import numpy as np
from scipy.io import netcdf_file

def write_file(file_out, tide_name, nodes_obc, amp, phase):
  ntide = len(tide_name)
  nobc = len(nodes_obc)
  period = {'m2':44712, 's2':43200, 'k2':43082, 'n2':45570, 'k1':86164, 'o1':92950, 'p1':86637, 'q1':96726}

  nc = netcdf_file(file_out, 'w')
  nc.createDimension('nobc', nobc)
  nc.createDimension('tidal_components', ntide)
  nc.createDimension('DateStrLen', 26)

  obc_nodes = nc.createVariable('obc_nodes', 'i', ('nobc',))
  obc_nodes.long_name = "Open Boundary Node Number"
  obc_nodes.grid = "obc_grid"

  tide_period = nc.createVariable('tide_period', 'f', ('tidal_components',))
  tide_period.long_name = "tide angular period"
  tide_period.units = "seconds"

  tide_Eref = nc.createVariable('tide_Eref', 'f', ('nobc',))
  tide_Eref.long_name = "tidal elevation reference level"
  tide_Eref.units = "meters"

  tide_Ephase = nc.createVariable('tide_Ephase', 'f', ('tidal_components', 'nobc'))
  tide_Ephase.long_name = "tidal elevation phase angle"
  tide_Ephase.units = "degrees, time of maximum elevation with respect to chosen time origin"

  tide_Eamp = nc.createVariable('tide_Eamp', 'f', ('tidal_components', 'nobc'))
  tide_Eamp.long_name = "tidal elevation amplitude"
  tide_Eamp.units = "meters"

  equilibrium_tide_Eamp = nc.createVariable('equilibrium_tide_Eamp', 'f', ('tidal_components',))
  equilibrium_tide_Eamp.long_name = "equilibrium tidal elevation amplitude"
  equilibrium_tide_Eamp.units = "meters"

  equilibrium_beta_love = nc.createVariable('equilibrium_beta_love', 'f', ('tidal_components',))
  equilibrium_beta_love.long_name = "formula"
  equilibrium_beta_love.formula = "beta=1+klove-hlove"

  equilibrium_tide_type = nc.createVariable('equilibrium_tide_type', 'c', ('tidal_components', 'DateStrLen'))
  #equilibrium_tide_type:units = "beta=1+klove-hlove" ;

  time_origin = nc.createVariable('time_origin', 'f', ())
  time_origin.long_name = "time"
  time_origin.units = "days since 0.0"
  time_origin.time_zone = "none"

  nc.type = "FVCOM SPECTRAL ELEVATION FORCING FILE"
  nc.components = ",".join(tide_name)
  nc.history = "FILE CREATED: 2019-08-25T08:29:00Z: CST"

  obc_nodes[:] = nodes_obc
  tide_period[:] = [period[name] for name in tide_name]
  tide_Eref[:] = 0.0
  tide_Ephase[:,:] = phase
  tide_Eamp[:,:] = amp
  equilibrium_tide_Eamp[:] = 0.0
  equilibrium_beta_love[:] = 0.0
  equilibrium_tide_type[:,:] = 'SEMIDIURNAL               '
  time_origin = 0
  nc.close()


# ---------- MAIN ----------
if len(sys.argv) < 3:
  print('Usage: gen_obc_eta.py <tide_hc_file> <ntide>')
  sys.exit(0)
tide_hc_file = sys.argv[1]
ntide = int(sys.argv[2])

# read harmonic constants
fl_hc = open(tide_hc_file, 'r')
for i in range(2):
  line = fl_hc.readline()

header = fl_hc.readline()
h_fields = header.split()
tide_name = []
print(h_fields)
for i in range(2,2*ntide+2,2):
  tname = h_fields[i][:2]
  tide_name.append(tname)
print(tide_name)

lines = fl_hc.readlines()
fl_hc.close()

nobc = len(lines)
lat = np.zeros(nobc)
lon = np.zeros(nobc)
amp = np.zeros([ntide, nobc])
phase = np.zeros([ntide, nobc])

for i in range(nobc):
  tfields = lines[i].split()
  lat[i] = np.fromstring(tfields[0], sep=' ')
  lon[i] = np.fromstring(tfields[1], sep=' ')
  for n in range(ntide):
    amp[n,i] = np.fromstring(tfields[2+2*n], sep=' ')
    phase[n,i] = np.fromstring(tfields[3+2*n], sep=' ')

nodes_obc = np.arange(1,nobc+1)

file_out = 'tidal_force.nc'
write_file(file_out, tide_name, nodes_obc, amp, phase)

