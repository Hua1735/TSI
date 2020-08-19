from math import sqrt, hypot
from numba import jit,prange
import numpy as np


@jit
def type1(in_arr,par):
	return in_arr[in_arr[:,0] == par]

@jit
def type2(in_arr,par):
	return in_arr[in_arr[:,1] == par]

@jit
def type3(in_arr,par):
	return in_arr[in_arr[:,0] + in_arr[:,1] == par]

@jit
def type4(in_arr,par,xsize):
	return in_arr[in_arr[:,1] - in_arr[:,0] == (xsize - 1 - par)]


@jit
def d_b(xo, yo, x_dim, y_dim, direction): # distance from origin to boundary, which will be used later
	x_dim, y_dim = x_dim - 1, y_dim -1
	k = sqrt(2)
	if direction == 0 : # N
		db = yo
	elif direction == 2 : # E
		db = x_dim- xo
	elif direction == 4 : # S
		db = y_dim - yo
	elif direction == 6 : # W
		db = xo
	elif direction == 1 : # NE
		db = (min(yo, x_dim - xo))*k
	elif direction == 3 : # SE
		db = (min(y_dim-yo, x_dim-xo))*k
	elif direction == 5 : # SW
		db = (min(xo, y_dim-yo))*k
	else: # NW
		db = (min(xo, yo))*k
	
	return db



@jit
def tsi_compute(distances,w):
	
	distances_normalized = np.interp(distances, (distances.min(), distances.max()), (0, 1))
	# compute std
	m, variance, k = 0, 0, 0
	for i in range(8):
		m+=distances_normalized[i]/8
	for i in range(8):
		variance+=(distances_normalized[i]-m)**2
	std = sqrt(variance/8)
	# compute tsi
	for i in range(8):
		k+=w[i]/distances[i]
	if std!=0:
		tsi = k/std
	else:
		tsi = 0
	return tsi







@jit(nopython=True)
def get_tsi(r1,r2,r3,r4,y,x,y_dim,x_dim,cell_width):
	N_weight = 2  # 直接改這裡可以改 NW/N/NE 的權重
	distances = np.full((8,),10e6)
	
	# type1
	for i in range(r1.shape[0]):
		d = hypot(r1[i,0]-y,r1[i,1]-x)

		if r1[i,1] >x: # East
			distances[2] = min(distances[2],d)
		elif r1[i,1] <x: # West
			distances[6] = min(distances[6],d)

	# type2
	for i in range(r2.shape[0]):
		d = hypot(r2[i,0]-y,r2[i,1]-x)
		if r2[i,0] > y: # South
			distances[4] = min(distances[4],d)
		elif r2[i,0] <y: # North
			distances[0] = min(distances[0],d)

	# type3
	for i in range(r3.shape[0]):
		d = hypot(r3[i,0]-y,r3[i,1]-x)
		if r3[i,0] > y: # SW
			distances[5] = min(distances[5],d)
		elif r3[i,0] < y: # NE
			distances[1] = min(distances[1],d)

	# type4
	for i in range(r4.shape[0]):
		d = hypot(r4[i,0]-y,r4[i,1]-x)
		if r4[i,0] > y: # SE
			distances[3] = min(distances[3],d)
		elif r4[i,0] < y: # NW
			distances[7] = min(distances[7],d)		 
	
	
	w = [N_weight, N_weight, 1, 1, 1, 1, 1, N_weight]
	for i in range(8):
		if distances[i] == 10e6:
			distances[i] = d_b(x, y, x_dim, y_dim, i)
			w[i] = 0

	tsi = tsi_compute(distances,w)/cell_width	
	
	return tsi


