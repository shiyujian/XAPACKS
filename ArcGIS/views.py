from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ElevationPoint, ElevationPointFile
from osgeo import ogr
from osgeo import osr
from osgeo import gdal
from gdalconst import *
import json
import os
import uuid
import zipfile
import subprocess
import time
import shutil
import xlrd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_URL = os.path.join(BASE_DIR, 'static')
'''
上传shapefile文件
http://localhost:8000/arcgis/home/
'''
def home (request):
    return render(request, 'home.html')

'''
# 存储shapefile文件
http://localhost:8000/arcgis/uploadelevationPointfile/
'''
@csrf_exempt
def uploadelevationPointfile(request):
    if request.method == 'POST':
        file_type = request.POST.get('file_type')
        file_name = request.POST.get('file_name')
        section = request.POST.get('section')
        file_obj = request.FILES.get('file', None)
        z = zipfile.ZipFile(file_obj, "r")
        shpfile = ElevationPointFile()
        shpfile.file_name = file_name
        shpfile.shp_file = file_obj
        shpfile.file_type = file_type
        shpfile.section = section
        shpfile.save()
        return HttpResponse('文件上传成功')

'''
存储shapefile文件解析得到的高程点数据
http://localhost:8000/arcgis/elevationPoint/?filename=byredline&filetype=Polygon
http://localhost:8000/arcgis/elevationPoint/?filename=bybefore&filetype=Point
http://localhost:8000/arcgis/elevationPoint/?filename=byafter&filetype=Point
http://localhost:8000/arcgis/elevationPoint/?filename=redline&filetype=Polygon
'''
@csrf_exempt
def elevationPoint (request):
    if request.method == 'GET':
        file_name = request.GET.get('filename')
        file_type = request.GET.get('filetype')
        shapefile_URL = os.path.join(static_URL, 'upload', 'shapefile')
        shpfile = ElevationPointFile.objects.filter(file_name=file_name).filter(file_type=file_type)
        print(shpfile)
        try:
            # uncompress
            zip_file = zipfile.ZipFile(shpfile[0].shp_file, "r")
            zip_file.extractall(path=shapefile_URL)
        finally:
            zip_file.close
        # read shpfile
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shp_file = os.path.join(shapefile_URL, file_name, file_name+'.shp')
        dataSource = driver.Open(shp_file, 0)
        if dataSource is None:
            print('Could not open %s' % (shp_file))
        else:
            layer = dataSource.GetLayer(0)
            # read element
            for i in range(layer.GetFeatureCount()):
                feature = layer.GetFeature(i)
                feadict = json.loads(feature.ExportToJson())
                geometry = feadict['geometry']
                properties = feadict['properties']
                if geometry['type'] == 'Polygon':
                    updateshpfile = ElevationPointFile.objects.get(id=shpfile[0].id)
                    updateshpfile.coordinates = geometry['coordinates']
                    updateshpfile.save()
                elif geometry['type'] == 'Point':
                    elevationPoint = ElevationPoint()
                    elevationPoint.Y_touyin = geometry['coordinates'][0]
                    elevationPoint.X_touyin = geometry['coordinates'][1]
                    elevationPoint.Z_touyin = properties['Elevation']
                    elevationPoint.coordinates = geometry['coordinates']
                    elevationPoint.point_type = geometry['type']
                    elevationPoint.point_name = file_name
                    elevationPoint.save()
        return HttpResponse('文件解析成功')

'''
通过高程点生成shapefile文件
http://localhost:8000/arcgis/elevationPointfile/?filename=byredline&filetype=Polygon
http://localhost:8000/arcgis/elevationPointfile/?filename=bybefore&filetype=Point
http://localhost:8000/arcgis/elevationPointfile/?filename=byafter&filetype=Point
'''
@csrf_exempt
def elevationPointfile(request):
    file_name = request.GET.get('filename')
    file_type = request.GET.get('filetype')
    result_file = os.path.join(static_URL, 'resultShp', file_name+'.shp')
    # create dataSource
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.access(result_file, os.F_OK):
        driver.DeleteDataSource(result_file)
    newds = driver.CreateDataSource(result_file)
    # 创建WGS84空间参考
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    if file_type == 'Point':
        # 创建图层
        layernew = newds.CreateLayer('point', srs, ogr.wkbPoint)

        # 添加属性定义
        fieldf_elevation = ogr.FieldDefn('Elevation', ogr.OFTReal)
        layernew.CreateField(fieldf_elevation)
        # 创建点状要素
        elevationPoint_list = ElevationPoint.objects.filter(point_name=file_name)
        print('wkt6')

        for point in elevationPoint_list:
            print('wkt7')
            wkt = 'POINT(%f %f %f)' % (point.Y_touyin, point.X_touyin, point.Z_touyin)
            print('wkt2')
            print(wkt)
            geom = ogr.CreateGeometryFromWkt(wkt)
            feat = ogr.Feature(layernew.GetLayerDefn())
            feat.SetField('Elevation', point.Z_touyin)
            feat.SetGeometry(geom)
            layernew.CreateFeature(feat)
    elif file_type == 'Polygon':
        # create layer
        layernew = newds.CreateLayer('polygon', srs, ogr.wkbPolygon)
        # 添加属性定义
        # 创建多边形要素
        shp_file = ElevationPointFile.objects.get(file_name=file_name)
        coordinates = shp_file.coordinates
        coordinates_arr = coordinates[3:-3].split('], [')
        wkt = 'POLYGON(('
        for c in coordinates_arr:
            newc = c.replace(', ', ' ')
            wkt += newc + ','
        finally_wkt = wkt[0: -1] + '))'
        geom = ogr.CreateGeometryFromWkt(finally_wkt)
        feat = ogr.Feature(layernew.GetLayerDefn())
        feat.SetGeometry(geom)
        layernew.CreateFeature(feat)
    return HttpResponse('通过高程点生成shapefile文件')
'''
使用进程，算出土方量
http://localhost:8000/arcgis/useOSCommand/?filename=arcGISBash
http://localhost:8000/arcgis/useOSCommand/?filename=arcGISfutu
'''
def useOSCommand(request):
    file_name = request.GET.get('filename')
    if file_name == 'arcGISBash':
        bashpy_file = os.path.join(static_URL, 'python', 'arcGISBash.py')
        popen = subprocess.Popen(['C:\Python27\ArcGIS10.1\python.exe', bashpy_file],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        shell=True)
        out, err = popen.communicate('1234')
        print('stdout ' + out)
        print('stderr ' + err)
    elif file_name == 'arcGISfutu':
        bashpy_file = os.path.join(static_URL, 'python', 'arcGISfutu.py')
        popen = subprocess.Popen(['C:\Python27\ArcGIS10.1\python.exe', bashpy_file],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        shell=True)
        out, err = popen.communicate('4321')
        print('stdout ' + out)
        print('stderr ' + err)
    return HttpResponse('使用进程,算出土方量')
'''
导入覆土/塘渣数据
http://localhost:8000/arcgis/uploadData/?filename=before&filetype=Point
http://localhost:8000/arcgis/uploadData/?filename=after&filetype=Point
'''
def uploadData(request):
    file_name = request.GET.get('filename')
    file_type = request.GET.get('filetype')
    file_URL = os.path.join(static_URL, 'sourceShp', file_name + '.dat')
    with open(file_URL, 'r') as datfile:
        list = datfile.readlines()
        print(len(list))
        for i in range(len(list)):
            print(list[i])
            listArr = list[i].split(',,')
            dataArr = listArr[1].split(',')
            print(listArr[1])
            print(dataArr[0])
            point = ElevationPoint()
            point.Y_touyin = dataArr[0]
            point.X_touyin = dataArr[1]
            point.Z_touyin = dataArr[2]
            point.point_type = file_type
            point.point_name = file_name
            point.section = 'P191-01-01'
            point.save()
    return HttpResponse('导入覆土/塘渣数据成功')

'''
根据覆土/塘渣数据生成shapefile
http://localhost:8000/arcgis/pointShapefile/?filename=futu&filetype=Point
http://localhost:8000/arcgis/pointShapefile/?filename=tangzha&filetype=Point
'''
def pointShapefile(request):
    file_name = request.GET.get('filename')
    file_type = request.GET.get('filetype')
    result_file = os.path.join(static_URL, 'resultShp', file_name+'.shp')
    # create dataSource
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.access(result_file, os.F_OK):
        driver.DeleteDataSource(result_file)
    newds = driver.CreateDataSource(result_file)
    if file_type == 'Point':
        # 创建图层
        layernew = newds.CreateLayer('point', None, ogr.wkbPoint)
        # 添加属性定义
        fieldf_elevation = ogr.FieldDefn('Elevation', ogr.OFTReal)
        layernew.CreateField(fieldf_elevation)
         # 创建点状要素
        elevationPoint_list = ElevationPoint.objects.filter(point_name=file_name)

        for point in elevationPoint_list:
            wkt = 'POINT(%f %f %f)' % (point.Y_touyin, point.X_touyin, point.Z_touyin)
            print('wkt2')
            print(wkt)
            geom = ogr.CreateGeometryFromWkt(wkt)
            feat = ogr.Feature(layernew.GetLayerDefn())
            feat.SetField('Elevation', point.Z_touyin)
            feat.SetGeometry(geom)
            layernew.CreateFeature(feat)
    return HttpResponse('根据覆土/塘渣数据生成shapefile')

'''
根据标段数据查找高程点
根据标段数据查找红线数据
计算土方量值和TIF文件地址
http://localhost:8000/arcgis/earthVolume/?section=P193-01-01
'''
def earthVolume(request):
    uuidValue = str(uuid.uuid1())[0 : -13]
    section = request.GET.get('section')
    stdinValue = section + '_' + str(uuidValue)
    newStdinValue = stdinValue.replace('-', '')
    print(newStdinValue)

    processFile_URL = os.path.join(static_URL, 'processFile', newStdinValue)
    if os.path.exists(processFile_URL):
        shutil.rmtree(processFile_URL)
    if not os.path.exists(processFile_URL):
        os.makedirs(processFile_URL)
    before_file = os.path.join(processFile_URL,  'before.shp')
    after_file = os.path.join(processFile_URL, 'after.shp')
    redline_file = os.path.join(processFile_URL, 'redline.shp')

    driver = ogr.GetDriverByName('ESRI Shapefile')
    beforeds = driver.CreateDataSource(before_file)
    afterds = driver.CreateDataSource(after_file)
    redlineds = driver.CreateDataSource(redline_file)

    layerbefore = beforeds.CreateLayer('point', None, ogr.wkbPoint)
    layerafter = afterds.CreateLayer('point', None, ogr.wkbPoint)
    layerredline = redlineds.CreateLayer('polygon', None, ogr.wkbPolygon)

    fieldf_elevation = ogr.FieldDefn('Elevation', ogr.OFTReal)
    layerbefore.CreateField(fieldf_elevation)
    layerafter.CreateField(fieldf_elevation)

    point_list_before = ElevationPoint.objects.filter(point_name='before', section=section)
    point_list_after = ElevationPoint.objects.filter(point_name='after', section=section)
    polygon_redline = ElevationPointFile.objects.filter(file_name='redline', section=section)

    for point in point_list_before:
        wkt = 'POINT(%f %f)' % (point.Y_touyin, point.X_touyin)
        geom = ogr.CreateGeometryFromWkt(wkt)
        feat = ogr.Feature(layerbefore.GetLayerDefn())
        feat.SetField('Elevation', point.Z_touyin)
        feat.SetGeometry(geom)
        layerbefore.CreateFeature(feat)
    for point in point_list_after:
        wkt = 'POINT(%f %f)' % (point.Y_touyin, point.X_touyin)
        geom = ogr.CreateGeometryFromWkt(wkt)
        feat = ogr.Feature(layerbefore.GetLayerDefn())
        feat.SetField('Elevation', point.Z_touyin)
        feat.SetGeometry(geom)
        layerafter.CreateFeature(feat)
    coordinates = polygon_redline[0].coordinates
    coordinates_arr = coordinates[3:-3].split('], [')
    wkt = 'POLYGON(('
    for c in coordinates_arr:
        newc = c.replace(', ', ' ')
        wkt += newc + ','
    finally_wkt = wkt[0: -1] + '))'
    geom = ogr.CreateGeometryFromWkt(finally_wkt)
    feat = ogr.Feature(layerredline.GetLayerDefn())
    feat.SetGeometry(geom)
    layerredline.CreateFeature(feat)
    beforeds.Destroy()
    afterds.Destroy()
    redlineds.Destroy()

    arcGIS_file = os.path.join(static_URL, 'python', 'arcGIS.py')
    popen = subprocess.Popen(['C:\Python27\ArcGIS10.6\python.exe', arcGIS_file, newStdinValue],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    shell=True)
    code = popen.wait()

    if os.path.exists(processFile_URL):
        shutil.rmtree(processFile_URL)

    attrTalbe_url = os.path.join(static_URL, 'resultFile', newStdinValue, 'outFill.xls')
    outfill_URL = os.path.join(static_URL, 'resultFile', newStdinValue, 'outFill')

    data = xlrd.open_workbook(attrTalbe_url)
    table = data.sheet_by_name('outFill')
    colArr3 = table.col_values(3)
    colArr4 = table.col_values(4)
    area = 0
    volume = 0
    for i in colArr3:
        if i == 'VOLUME':
            pass
        else :
            volume += i
    for i in colArr4:
        if i == 'AREA':
            pass
        else :
            area += i
    data = {
        'status': 200,
        'msg': '',
        'content': {
            'area': area,
            'volume': volume,
            'attrTalbe_url': attrTalbe_url,
            'outfill_url': outfill_URL,
        }
    }
    return JsonResponse(data=data)
