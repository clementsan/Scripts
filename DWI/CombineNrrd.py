#! /usr/bin/env python
import os
import fnmatch
import sys
from string import Template
from optparse import OptionParser

print 'Purpose: Combine DWI Nrrd Files\nUsage: CombineNrrd.py [outputfile] [input files]'

output_prefix = sys.argv[1]
input_dwi_file = sys.argv[2:]

output_prefix = output_prefix.replace('.nhdr','').replace('.nrrd','')

# write the header files
hdrContent = ''
Gen_rawdata_cmd = Template('/tools/Slicer3/Slicer3-3.6-2010-06-10-linux-x86_64/bin/unu join -i $infile -a 0 | /tools/Slicer3/Slicer3-3.6-2010-06-10-linux-x86_64/bin/unu save -f nrrd -e gzip -o $outfile')

foutnhdr = output_prefix + '.nhdr'
foutraw = output_prefix + '.raw'
# output file name
Gen_rawdata_cmd = Gen_rawdata_cmd.substitute(infile=' '.join(input_dwi_file),outfile=foutnhdr)
print Gen_rawdata_cmd
# Generate the raw data file using unu join
os.system(Gen_rawdata_cmd)

#read in the header
hdrContent = ''.join(open(foutnhdr,'r').readlines())
hdrContent = hdrContent.replace('NRRD0004','NRRD0005').replace('NRRD0003','NRRD0005')
#print hdrContent

gradinfo = ''
dwi_counter = 0
gradnum = 0

for file in input_dwi_file:
    Gen_rawdata_cmd = Gen_rawdata_cmd + ' ' + file 
    # convert DWI
    fin = open(file,'r')
    # the first file
    if dwi_counter == 0:
       lnum = 1
       dwi_counter += 1
       for line in fin:
	       #adding info that's missing after unu join
	       if (fnmatch.fnmatch(line,'space:*') == True):
		       hdrContent = hdrContent + line
	       if (fnmatch.fnmatch(line,'space units:*') == True):
		       hdrContent = hdrContent + line
	       if (fnmatch.fnmatch(line,'space origin:*') == True):
		       hdrContent = hdrContent + line
	       if (fnmatch.fnmatch(line,'measurement frame:*') == True):
		       hdrContent = hdrContent + line
	       if (fnmatch.fnmatch(line,'modality:*') == True):
		       hdrContent = hdrContent + line
	       if (fnmatch.fnmatch(line,'DWMRI_b-value:=*') == True):
		       hdrContent = hdrContent + line
	       if (fnmatch.fnmatch(line,'content:*') == True):
		       hdrContent = hdrContent + line
               if (fnmatch.fnmatch(line,'space directions:*') == True):
		       hdrContent = hdrContent + line
               print line
	       #getting gradient info
	       if (fnmatch.fnmatch(line,'DWMRI_gradient_*') == True):
		       addline = 'DWMRI_gradient_'+"%04d"%gradnum + ':=' + line[21:]
		       gradinfo = gradinfo + addline
		       gradnum +=1
    else:
       dwi_counter += 1
       for line in fin:
           if (fnmatch.fnmatch(line,'DWMRI_gradient_*') == True):
	       addline = 'DWMRI_gradient_'+"%04d"%gradnum + ':=' + line[21:]
	       gradinfo = gradinfo + addline
	       gradnum +=1
	
hdrContent = hdrContent.replace('kinds: ??? space space space','kinds: list space space space')
hdrContent = hdrContent.replace('kinds: space space space ???','kinds: space space space list')
#add gradient info
hdrContent = hdrContent + gradinfo

fout = open(foutnhdr,'w')
fout.write(hdrContent)
fout.close()

print 'Done combining ' + str(dwi_counter) + ' DWI files' 

