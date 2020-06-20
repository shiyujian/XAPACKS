
import arcpy
import os
import sys
import shutil
stdin = sys.argv[1]
static_URL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processFile_URL = os.path.join(static_URL, 'processFile')
resultGIS_URL = os.path.join(processFile_URL, stdin)
beforeShp = os.path.join(processFile_URL, stdin, 'before'+'.shp')
afterShp = os.path.join(processFile_URL, stdin, 'after'+'.shp')
redlineShp = os.path.join(processFile_URL, stdin, 'redline'+'.shp')
beforeProjectionShp = os.path.join(processFile_URL, stdin, 'beforeProjection'+'.shp')
afterProjectionShp = os.path.join(processFile_URL, stdin, 'afterProjection'+'.shp')
redlineProjectionShp = os.path.join(processFile_URL, stdin, 'redlineProjection'+'.shp')
resultGDB_URL = os.path.join(static_URL, 'result.gdb')
resultFile_URL = os.path.join(static_URL, 'resultFile', stdin)

arcpy.env.workspace = resultGIS_URL
arcpy.CheckOutExtension('3D')

coordinate_projection = arcpy.SpatialReference('CGCS2000 3 Degree GK CM 117E')
arcpy.Project_management(beforeShp, beforeProjectionShp, coordinate_projection)
arcpy.Project_management(afterShp, afterProjectionShp, coordinate_projection)
arcpy.Project_management(redlineShp, redlineProjectionShp, coordinate_projection)
arcpy.ddd.CreateTin("before_t", None, [[beforeProjectionShp, 'Elevation', 'Mass_Points'], redlineProjectionShp], "constrained_delaunay")
arcpy.ddd.CreateTin("after_t", None, [[afterProjectionShp, 'Elevation', 'Mass_Points'], redlineProjectionShp], "constrained_delaunay")

# TIN to Raster
arcpy.ddd.TinRaster("before_t", "before_sg", data_type="FLOAT", method="LINEAR", sample_distance="OBSERVATIONS 250", z_factor=1)
arcpy.ddd.TinRaster("after_t", "after_sg", data_type="FLOAT", method="LINEAR", sample_distance="OBSERVATIONS 250", z_factor=1)

# Cut Fill out_raster raster dataset
outCutFill = arcpy.sa.CutFill("before_sg", "after_sg", 1)

if not os.path.exists(resultFile_URL):
    os.makedirs(resultFile_URL)
arcpy.env.workspace = resultFile_URL
outCutFill.save("outFill")
arcpy.RasterToPolygon_conversion(outCutFill, 'outFillProjection.shp', 'NO_SIMPLIFY', 'VALUE')
coordinate_WGS84 = arcpy.SpatialReference('WGS 1984')
arcpy.Project_management('outFillProjection.shp', 'outFillShp.shp', coordinate_WGS84, None, in_coor_system=coordinate_projection)

arcpy.TableToTable_conversion(outCutFill, resultGDB_URL, stdin)
arcpy.TableToExcel_conversion(resultGDB_URL + '\\' + stdin, 'outFill.xls')
# delete table
arcpy.env.workspace = resultGDB_URL
arcpy.Delete_management(stdin)



