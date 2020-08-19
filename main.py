import gdal
import numpy as np
from timeit import default_timer as timer
from argparse import ArgumentParser
from raster_io import *
from toolkit import *
import time
def parse_arg_():
	parser = ArgumentParser(
		prog="python-TSI",
		description="A simple program to calculate TSI value"
		"and rescale(Optional) to 0-8.")
	
	parser.add_argument(
		"--input",
		"-i",
		type=str,
		required=True,
		help="Input ridge raster , pixel value must be 255 (ridge) or 0 (otherwise).")

	parser.add_argument(
		"--multiprocess",
		"-mp",
		required=False,
		type=int,
		help="Not implemented")

	parser.add_argument(
		"--output",
		"-o",
		type=str,
		required=True,
		help="Output raster path.")

	#parser.add_argument( "--output-format" ,"-of" , type= str , required = True /False , help="Output format")

	'''
	parser.add_argument(
		"--rescale",
		"-r",
		nargs=1,
		type=int,
		required=False,
		help="Rescale TSI value to specific range.")
		# help="Rescale into spcified range , if omittied , output raw TSI")
	'''

	args = parser.parse_args()
	return args

args = parse_arg_()
in_file_path = args.input
out_file_path = args.output
in_raster = read_raster_dataset(in_file_path)
in_projectionRef = in_raster.GetProjectionRef()
in_GeoTransform = in_raster.GetGeoTransform()  # 1:we , 5:ns
in_raster_width = in_raster.RasterXSize
in_raster_height = in_raster.RasterYSize

print("Processing slice 1_1....")
slice_size_x = in_raster.RasterXSize
slice_size_y = in_raster.RasterYSize

print("x : {} to {} , y : {} to {}".format(
	0, slice_size_x - 1, 0, slice_size_y - 1))

in_arr = raster_band_to_array(in_raster, band=1, x_offset=0, y_offset=0)
print('Searching all ridges.....')
r = np.argwhere(in_arr == 255)
nr = r.shape[0]
print(f"number of ridges = {nr}")
# Loop through thw whole array , compute TSI.
from numba import njit,prange
@njit(parallel = True)
def speed_tsi(group1,group2,group3,group4):
	tsi_arr = np.zeros((slice_size_y, slice_size_x), dtype = np.float32) # initialize	
	for y in range(1,slice_size_y-1):
		
		for x in prange(1,slice_size_x-1):
			r1 = group1[y]
			r2 = group2[x]
			r3 = group3[x+y]
			r4 = group4[slice_size_x-x-1+y]
			tsi_arr[y,x] = get_tsi(r1,r2,r3,r4,y,x,y_dim,x_dim,cell_width)
			# print(x)
			
			

	return tsi_arr





del in_arr
ti = timer()
from numba.typed import List

group1 = List()
# print('group1=',group1)
group2 = List()
group3 = List()
group4 = List()

# compure four types
print('Processing type1.......')
for i in range(slice_size_y):
	group1.append(type1(r,i))
# group1 = [type1(r,i) for i in range(slice_size_y)]
print('Processing type2.......')
# group2 = [type2(r,i) for i in range(slice_size_x)]
for i in range(slice_size_x):
	group2.append(type2(r,i))
print('Processing type3.......')
# group3 = [type3(r,i) for i in range(slice_size_x+slice_size_y-1)]
for i in range(slice_size_x+slice_size_y-1):
	group3.append(type3(r,i))
print('Processing type4.......')
# group4 = [type4(r,i,slice_size_x) for i in range(slice_size_x+slice_size_y-1)]
for i in range(slice_size_x+slice_size_y-1):
	group4.append(type4(r,i,slice_size_x))
# print(type(group3))
print('all takes',timer()-ti)
x_dim = slice_size_x
y_dim = slice_size_y
cell_width = in_GeoTransform[1]
n_all = (x_dim-2)*(y_dim-2)

# from itertools import product

# tsi_arr = np.zeros([slice_size_y, slice_size_x], dtype = np.float16) # initialize

ti = timer() # record initial time before looping




final = speed_tsi(group1,group2,group3,group4)
final[r[:,0],r[:,1]] = 0 # make tsi of ridges >> 0
write_array_to_raster(final, in_raster, out_file_path)

tf = timer() # record final time
print('Time cost : {} sec(before looping)'.format(tf-ti))

