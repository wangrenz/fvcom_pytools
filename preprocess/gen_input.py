#!/usr/bin/env python
import os
import sys
import numpy as np

if len(sys.argv) < 3:
  print('Usage: gen_input.py <sms_grd_file> <nobc>')
  sys.exit(0)

sms_grd_file = sys.argv[1]
nobc = int(sys.argv[2])

# read grid and depth from sms .grd file 
fl = open(sms_grd_file, 'r')
# read head info
fl.readline()
header = fl.readline()
tlist = header.split()
nele = int(tlist[0])
nvert = int(tlist[1])
print('No. of triangulars:', nele)
print('No. of trangular vertexs:', nvert)

x = np.zeros(nvert)
y = np.zeros(nvert)
h = np.zeros(nvert)
# read triangular vertexs
for i in range(nvert):
  line = fl.readline()
  tlist = line.split()
  #print 'vert:', tlist[0]
  if tlist[0] != str(i+1):
    print("read vertex error!")
    sys.exit(1)
  x[i] = np.fromstring(tlist[1], sep=' ')
  y[i] = np.fromstring(tlist[2], sep=' ')
  h[i] = np.fromstring(tlist[3], sep=' ')

# read triangular faces
nv = np.zeros([nele, 3])
for i in range(nele):
  line = fl.readline()
  tlist = line.split()
  #print 'face:', tlist[0]
  if tlist[0] != str(i+1):
    print("read face error!")
    sys.exit(2)
  nv[i,0] = np.fromstring(tlist[2], sep=' ')
  nv[i,1] = np.fromstring(tlist[3], sep=' ')
  nv[i,2] = np.fromstring(tlist[4], sep=' ')

fl.close()
print('min depth: %f' % h.min())
print('max depth: %f' % h.max())

# write fvcom grd file 
print('writing fvcom grd file ...')
fl_grd = open('grd.dat', 'w')
fl_grd.write('Node Number = %d\n' % nvert)
fl_grd.write('Cell Number = %d\n' % nele)
for i in range(nele):
  fl_grd.write('%6d %6d %6d %6d    1\n' % (i+1, nv[i,0], nv[i,1], nv[i,2]))

for i in range(nvert):
  fl_grd.write('%6d  %f  %f  %f\n' % (i+1, x[i], y[i], 0.0))
fl_grd.close()

# write fvcom depth file
print('writing fvcom depth file ...')
fl_dep = open('dep.dat', 'w')
fl_dep.write('Node Number = %d\n' % nvert)
for i in range(nvert):
  fl_dep.write('%f  %f  %f\n' % (x[i], y[i], np.abs(h[i])))
fl_dep.close()

# write fvcom coriolis file
print('writing fvcom coriolis file ...')
fl_cor = open('cor.dat', 'w')
fl_cor.write('Node Number = %d\n' % nvert)
for i in range(nvert):
  corio = 2*7.292E-5 * np.sin(y[i]*np.pi/180.0)
  fl_cor.write('%f  %f  %e\n' % (x[i], y[i], corio))
fl_cor.close()

# write fvcom obc file
print('writing fvcom obc file ...')
fl_obc = open('obc.dat', 'w')
fl_obc.write('OBC Node Number = %d\n' % nobc)
for i in range(nobc):
  fl_obc.write('%d  %d  %d\n' % (i+1, i+1, 1))
fl_obc.close()

