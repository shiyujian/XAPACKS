 
# Python bash
import arcpy
import os
import sys
import shutil
stdin = sys.argv[1]
static_URL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processFile_URL = os.path.join(static_URL, 'processFile')
redlineShp = os.path.join(processFile_URL, stdin, 'redline'+'.shp')
beforeShp = os.path.join(processFile_URL, stdin, 'before'+'.shp')
arterShp = os.path.join(processFile_URL, stdin, 'after'+'.shp')
resultGIS_URL = os.path.join(processFile_URL, stdin)
resultGDB_URL = os.path.join(static_URL, 'resultGDB.gdb')
resultFile_URL = os.path.join(static_URL, 'resultFile', stdin)

arcpy.env.workspace = resultGIS_URL
arcpy.CheckOutExtension('3D')
arcpy.ddd.CreateTin("before_t", None, [[beforeShp, 'Elevation', 'Mass_Points'], redlineShp], "constrained_delaunay")
arcpy.ddd.CreateTin("after_t", None, [[arterShp, 'Elevation', 'Mass_Points'], redlineShp], "constrained_delaunay")

# TIN to Raster
arcpy.ddd.TinRaster("before_t", "before_sg", data_type="FLOAT", method="LINEAR", sample_distance="OBSERVATIONS 250", z_factor=1)
arcpy.ddd.TinRaster("after_t", "after_sg", data_type="FLOAT", method="LINEAR", sample_distance="OBSERVATIONS 250", z_factor=1)

# Cut Fill out_raster raster dataset
outCutFill = arcpy.sa.CutFill("before_sg", "after_sg", 1)

if not os.path.exists(resultFile_URL):
    os.makedirs(resultFile_URL)
arcpy.env.workspace = resultFile_URL
outCutFill.save("outFill")
# use TabletoTable
arcpy.TableToTable_conversion('outFill', resultGDB_URL, stdin)
# use TabletoExcel
arcpy.TableToExcel_conversion(resultGDB_URL + '\\' + stdin, 'outFill.xls')
# delete table
arcpy.env.workspace = resultGDB_URL
arcpy.Delete_management(stdin)

