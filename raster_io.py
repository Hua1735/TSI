import gdal
import osr
import numpy as np
from timeit import default_timer as timer

if __name__ == "__main__":
    pass


def read_raster_dataset(raster_file: str, print_info=True):
    '''
    Read raster datset through gdal.Open()
    Disable info output with print_info=False
    '''

    in_raster = gdal.Open(raster_file)

    if (print_info):
        # Show raster resolution
        print("Raster size ( X , Y ) = {} , {}".format(
            in_raster.RasterXSize, in_raster.RasterYSize))

        in_GeoTransform = in_raster.GetGeoTransform()
        print(
            "Cell size: {} , {} ( w-e , n-s )".format(in_GeoTransform[1], in_GeoTransform[5]))
        # 0 : top left x
        # 1 : w-e pixel resolution
        # 2 : rotation
        # - 0 = N as up
        # 3 : top left y
        # 4 : rotation  0 = N up
        # 5 : n-s pixel resolution ( meters )

        # Print raster projection
        print("Projection : {}".format(in_raster.GetProjection()))
        print("Successfully loaded raster : {}".format(raster_file))
    return in_raster


def raster_band_to_array(
        in_raster,
        band=1,
        x_offset=0,
        y_offset=0,
        x_dim=0,
        y_dim=0):
    in_band = in_raster.GetRasterBand(band)
    print("Loading raster band {} ...".format(band))

    # Show Input raster Min & Max
    in_min, in_max = in_band.ComputeRasterMinMax()
    in_no_data = in_band.GetNoDataValue()
    print("Band min value : {}\nBand max value : {}" .format(in_min, in_max))
    print("Band No data value : {}".format(in_no_data))

    if (x_dim == 0 and y_dim == 0):
        x_dim = in_raster.RasterXSize
        y_dim = in_raster.RasterYSize

    in_arr = in_band.ReadAsArray(0, 0, x_dim, y_dim)
    # x-offset :L TR , y-offset : TB , x-size , y-size (Unit : pixel)

    return in_arr


def write_array_to_raster(
        in_array,
        ref_raster,
        out_raster_path,
        format="GTiff"):
    # ( in_array , ref_raster , pixel_width , pixel_height , out_raster_path , format="GTiff" )

    # From input array
    cols, rows = in_array.shape[1], in_array.shape[0]  # y= [0] . x=[1]

    # From reference raster
    geotransform = ref_raster.GetGeoTransform()
    origin_x = geotransform[0]
    origin_y = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]
    ref_SRS = ref_raster.GetProjectionRef()

    # Output raster
    driver = gdal.GetDriverByName(format)
    out_raster = driver.Create(
        out_raster_path,
        xsize=cols,
        ysize=rows,
        bands=1,
        eType=gdal.GDT_Float32)
    out_raster.SetGeoTransform(
        (origin_x, pixel_width, 0, origin_y, 0, pixel_height))
    out_band = out_raster.GetRasterBand(1)

    # Write array to raster
    out_band.WriteArray(in_array)

    # Set output raster SRS
    out_raster_SRS = osr.SpatialReference()
    out_raster_SRS.ImportFromWkt(ref_SRS)
    out_raster.FlushCache


'''
def rescale_ndarry ( ndarray_ , ranges_ ) :
    in_min = ndarray_.min()
    in_max = ndarray_.max()
'''
