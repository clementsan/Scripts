#! /usr/bin/env python
import os
import fnmatch
import sys
from string import Template
from optparse import OptionParser

usage = "usage: %prog [options] arg"
parser = OptionParser(usage)

parser.add_option("-b", "--b0",dest="b0_list", help="b0 lists")
parser.add_option("-a", "--dwi_dim",dest="dwi_dim", help="dimension of the dwis")

#whether or not to do dicom convert

(options, args) = parser.parse_args()
if(len(args) == 0):
    print 'Purpose: Combine DWI Nrrd Files with the option to combine extra b0 files\nUsage: CombineDWI.py [outputfile] [input dwi files] -b[--b0] [input b0 files] -a[--dwi_dim] [the dimension of the graident direction, usually is 0 or 3]\n ****files should be separated with \',\'***'
    

output_prefix = args[0]
#work around that option doesn't store a varied-length string
############files needed to be separated with','###############
input_dwi_file = args[1].split(',')
if (options.b0_list):
    input_b0_file = (options.b0_list).split(',')


output_prefix = output_prefix.replace('.nhdr','').replace('.nrrd','')

# write the header files
hdrContent = ''
SlicerLoc = '/tools/Slicer3/Slicer3-3.6.3-2011-03-04-linux-x86_64'
Gen_rawdata_cmd = Template(os.path.join(SlicerLoc,'bin/unu join -i $infile -a ') + options.dwi_dim+' | '+(os.path.join(SlicerLoc,'bin/unu save -f nrrd -e gzip -o $outfile')))

foutnhdr = output_prefix + '.nhdr'
foutraw = output_prefix + '.raw'
# output file name
if (options.b0_list):
    Gen_rawdata_cmd = Gen_rawdata_cmd.substitute(infile=' '.join(input_b0_file)+' '+' '.join(input_dwi_file),outfile=foutnhdr)
else:
    Gen_rawdata_cmd = Gen_rawdata_cmd.substitute(infile=' '.join(input_dwi_file),outfile=foutnhdr)
print Gen_rawdata_cmd
# Generate the raw data file using unu join
os.system(Gen_rawdata_cmd)

#read in the header
hdrContent = ''.join(open(foutnhdr,'r').readlines())
hdrContent = hdrContent.replace('NRRD0004','NRRD0005')
hdrContent = hdrContent.replace('NRRD0003','NRRD0005')
hdrContent = hdrContent.replace('kinds: domain domain domain ???\n','')
#print hdrContent

gradinfo = ''
gradnum = 0

if options.b0_list:
    for b0_counter,file in enumerate(input_b0_file):
        addline = 'DWMRI_gradient_'+"%04d"%gradnum + ':=0   0   0\n'
        gradinfo = gradinfo + addline
        gradnum +=1

for dwi_counter,file in enumerate(input_dwi_file):
    # convert DWI
    fin = open(file,'r')
    # the first file
    if dwi_counter == 0:
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
	       if (fnmatch.fnmatch(line,'content: exists*') == True):
		       hdrContent = hdrContent + line
               if (fnmatch.fnmatch(line,'kinds*') == True):
		       hdrContent = hdrContent + line
               if (fnmatch.fnmatch(line,'centerings*') == True):
		       hdrContent = hdrContent + line
               if (fnmatch.fnmatch(line,'thickness*') == True):
		       hdrContent = hdrContent + line
               if (fnmatch.fnmatch(line,'space directions:*') == True):
		       hdrContent = hdrContent + line
	       #getting gradient info
	       if (fnmatch.fnmatch(line,'DWMRI_gradient_*') == True):
		       addline = 'DWMRI_gradient_'+"%04d"%gradnum + ':=' + line[21:]
		       gradinfo = gradinfo + addline
		       gradnum +=1
    else:
       for line in fin:
           if (fnmatch.fnmatch(line,'DWMRI_gradient_*') == True):
	       addline = 'DWMRI_gradient_'+"%04d"%gradnum + ':=' + line[21:]
	       gradinfo = gradinfo + addline
	       gradnum +=1
    
hdrContent = hdrContent.replace('content: exists(*,0)','content: exists(' + foutraw + ',0)')
hdrContent = hdrContent.replace('kinds: space space space ???','kinds: space space space list')
#add gradient info
hdrContent = hdrContent + gradinfo

fout = open(foutnhdr,'w')
fout.write(hdrContent)
fout.close()

print 'Done combining ' + str(dwi_counter+1) + ' DWI files ' + str(b0_counter+1)+' b0 files'

