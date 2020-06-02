import arcpy
# Python GUI CreateTIN
inRedline = "C:\\Users\\shiyu\\Documents\\ArcGIS\\bygc\\byredline.shp"
inBefore = "C:\\Users\\shiyu\\Documents\\ArcGIS\\bygc\\bybefore.shp"
inBeforePRJ = "C:\\Users\\shiyu\\Documents\\ArcGIS\\bygc\\bybefore.prj"
inAfter = "C:\\Users\\shiyu\\Documents\\ArcGIS\\bygc\\byafter.shp"
inAfterPRJ = "C:\\Users\\shiyu\\Documents\\ArcGIS\\bygc\\byafter.prj"
arcpy.CheckOutExtension('3D')
arcpy.env.workspace = 'C:\\Users\\shiyu\\py_demo\\tufangliang'
arcpy.CreateTin_3d("before_t", inBeforePRJ, [[inBefore, 'Elevation', 'Mass_Points'], inRedline], "constrained_delaunay")
arcpy.CreateTin_3d("after_t", inAfterPRJ, [[inAfter, 'Elevation', 'Mass_Points'], inRedline], "constrained_delaunay")

# TIN to Raster
arcpy.TinRaster_3d("after_t", "after_sg", data_type="FLOAT", method="LINEAR", sample_distance="OBSERVATIONS 250", z_factor=1)
arcpy.TinRaster_3d("before_t", "before_sg", data_type="FLOAT", method="LINEAR", sample_distance="OBSERVATIONS 250", z_factor=1)

# Cut Fill
outCutFill = arcpy.sa.CutFill("before_sg", "after_sg", 1)
outCutFill.save("outFillValue")
