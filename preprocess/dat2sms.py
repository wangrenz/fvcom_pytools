#!/bin/env python
import sys

data = []
poly = []

infile = sys.argv[1]
outfile = sys.argv[2]
mask_num = int(sys.argv[3])

fin = open(infile, 'r')
for line in fin:
  line = line.strip()
  if line.startswith('>'):
    if len(poly) > 0:
      data.append(poly)
      poly = []
  else:
    poly.append(line)

if len(poly) > 0:
  data.append(poly)
  poly = []

fin.close()

ntotal = 0
for poly in data:
  if len(poly) > mask_num:
    ntotal += 1

print(ntotal)

fout = open(outfile, 'w')
fout.write('COAST\n')
fout.write('%d 0.0\n' % ntotal)
for poly in data:
  if len(poly) >= mask_num:
    fout.write('%d 0\r\n' % len(poly))
    for line in poly:
      fout.write(line+'\r\n')
  
fout.close()
