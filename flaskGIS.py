from flask import Flask, request, jsonify, render_template, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
from osgeo import ogr, osr, gdal
from string import Template
import os
import math
import xlsxwriter
import json
import uuid
import zipfile
import pymysql
import subprocess
'''
xapacks 库
根据库里高程点数据生成shapefile
ProduceShapefile
根据shapefile获取数据
'''
app = Flask(__name__)
CORS(app, allow_headers='*')
api = Api(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_URL = os.path.join(BASE_DIR, 'static')
conn = pymysql.connect(host="localhost", user="root", password="847650632syj", db='xapacks')
cursor = conn.cursor()
DateTimeFormat = '%Y-%c-%d %H:%i:%s'
class CoordChange(Resource):
    # 国家2000，东经116的雄安投影坐标转换为经纬度
    def post(self):
        try:
            arcGIS_file = os.path.join(static_URL, 'python', 'gischange.py')
            subprocess.check_call(['C:\Python27\ArcGIS10.6\python.exe', arcGIS_file])
        except:
            result = {
                'code': 0,
                'msg': '土方量生成有误',
            }
            return result
        pass
api.add_resource(CoordChange, '/arcgis/coordchange/')
class ReadShapefile(Resource):
    # 读取shapefile
    def post(self):
        section = request.form['section']
        file_type = request.form['filetype']
        file_obj = request.files['file']
        file_name = file_obj.filename.split('.zip')[0]
        uuidValue = str(uuid.uuid1())[0 : -13]
        stdinValue = section + '_' + str(uuidValue)
        newStdinValue = stdinValue.replace('-', '')
        print(newStdinValue)
        processFile = os.path.join(static_URL, 'processFile', newStdinValue)
        try:
            exampleZip = zipfile.ZipFile(file_obj)
            exampleZip.extractall(path=processFile)
        finally:
            exampleZip.close
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shp_file = os.path.join(processFile, file_name+'.shp')
        if not os.path.exists(shp_file):
            shp_file = os.path.join(processFile, file_name, file_name+'.shp')
        dataSource = driver.Open(shp_file, 0)
        if dataSource is None:
            print('Could not open %s' % (shp_file))
        else:
            layer = dataSource.GetLayer(0)
            for i in range(layer.GetFeatureCount()):
                feature = layer.GetFeature(i)
                feadict = json.loads(feature.ExportToJson())
                geometry = feadict['geometry']
                properties = feadict['properties']
                print(geometry)
        result = {
            'msg': '读取shapefile成功',
            'content': newStdinValue
        }
        return result
api.add_resource(ReadShapefile, '/arcgis/readshapefile/')
class ProduceExcel(Resource):
    # 生成表格高程点
    def post(self):
        section = request.form['section']
        file_type = request.form['filetype']
        file_obj = request.files['file']
        uuidValue = str(uuid.uuid1())[0 : -13]
        stdinValue = section + '_' + str(uuidValue)
        newStdinValue = stdinValue.replace('-', '')
        print(newStdinValue)
        processFile = os.path.join(static_URL, 'processFile', newStdinValue)
        try:
            exampleZip = zipfile.ZipFile(file_obj)
            exampleZip.extractall(path=processFile)
        finally:
            exampleZip.close
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shp_file = os.path.join(processFile, file_type+'.shp')
        if not os.path.exists(shp_file):
            shp_file = os.path.join(processFile, file_type, file_type+'.shp')
        dataSource = driver.Open(shp_file, 0)
        if dataSource is None:
            print('Could not open %s' % (shp_file))
        else:
            layer = dataSource.GetLayer(0)
            workbook = xlsxwriter.Workbook(processFile + '/'+ file_type +'.xlsx')
            worksheet = workbook.add_worksheet('高程点')
            headings = ['Coding','X_touyin','Y_touyin', 'Z_touyin']
            bold = workbook.add_format({
                'bold':  True,
                'border': 2,
            })
            worksheet.write_row('A1', headings, bold)
            for i in range(layer.GetFeatureCount()):
                feature = layer.GetFeature(i)
                feadict = json.loads(feature.ExportToJson())
                geometry = feadict['geometry']
                properties = feadict['properties']
                Y_touyin = geometry['coordinates'][0]
                X_touyin = geometry['coordinates'][1]
                Z_touyin = geometry['coordinates'][2]
                worksheet.write_row('A' + str(i + 2), [i, X_touyin, Y_touyin, Z_touyin])
            workbook.close()
        result = {
            'msg': '123',
            'content': newStdinValue,
        }
        return result
api.add_resource(ProduceExcel, '/arcgis/produceexcel/')
# class UploadShapefile(Resource):
#     # 根据shapefile获取数据
#     def post(self):
#     result = {
#             'msg': '123',
#             'content': newStdinValue,
#             'msg': '成功插入%s条数据, 失败%s条数据' % (len(codesSucc), len(codesErr))
#         }
#     return result
# api.add_resource(UploadShapefile, '/arcgis/uploadshapefile/')
def MinZValueHandle(point_list, X, Y):
    minArr = []
    minZArr = []
    for point in point_list:
        valueY = math.fabs(float(point['Y_touyin']) - Y)
        valueX = math.fabs(float(point['X_touyin']) - X)
        if valueY == 0:
            value = valueX
        elif valueX == 0:
            value = valueY
        else :
            value = math.hypot(valueX, valueY)
        minArr.append(value)
        minZArr.append(point['Z_touyin'])
    minValue = min(minArr)
    minKey= minArr.index(minValue)
    minZValue = minZArr[minKey]
    return minZValue
def createShapefileHandle (newStdinValue, section):
    processFile_URL = os.path.join(static_URL, 'processFile', newStdinValue)
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
    fieldf_coding = ogr.FieldDefn('Coding', ogr.OFTReal)
    layerbefore.CreateField(fieldf_elevation)
    layerbefore.CreateField(fieldf_coding)
    layerafter.CreateField(fieldf_elevation)
    layerafter.CreateField(fieldf_coding)
    
    sqlPoint = """
        SELECT * FROM investigation_point;
    """
    sqlPolygon = """
        SELECT * FROM investigation_polygon;
    """
    cursor.execute(sqlPoint)
    beforeList = []
    afterList = []
    for point in cursor.fetchall():
        if point[2] == 'before' and point[3] == section:
            beforeList.append({
                'ID': point[0],
                'Coding': point[1],
                'InvestigationType': point[2],
                'Section': point[3],
                'X_touyin': point[4],
                'Y_touyin': point[5],
                'Z_touyin': point[6]
            })
            wkt = 'POINT(%f %f)' % (float(point[5]), float(point[4]))
            geom = ogr.CreateGeometryFromWkt(wkt)
            feat = ogr.Feature(layerbefore.GetLayerDefn())
            feat.SetField('Elevation', point[6])
            feat.SetField('Coding', point[1])
            feat.SetGeometry(geom)
            layerbefore.CreateFeature(feat)
        elif point[2] == 'after' and point[3] == section:
            afterList.append({
                'ID': point[0],
                'Coding': point[1],
                'InvestigationType': point[2],
                'Section': point[3],
                'X_touyin': point[4],
                'Y_touyin': point[5],
                'Z_touyin': point[6]
            })
            wkt = 'POINT(%f %f)' % (float(point[5]), float(point[4]))
            geom = ogr.CreateGeometryFromWkt(wkt)
            feat = ogr.Feature(layerafter.GetLayerDefn())
            feat.SetField('Elevation', point[6])
            feat.SetField('Coding', point[1])
            feat.SetGeometry(geom)
            layerafter.CreateFeature(feat)
    print(beforeList)
    cursor.execute(sqlPolygon)
    for point in cursor.fetchall():
        coordinates = point[4]
        coordinates_arr = coordinates[2:-2].split('], [')
        for index in range(len(coordinates_arr)):
            if index != 0:
                arr = coordinates_arr[index].split(', ')
                Y = float(arr[0])
                X = float(arr[1])
                minZValueBefore = MinZValueHandle(beforeList, X, Y)
                minZValueAfter = MinZValueHandle(afterList, X, Y)
                wkt = 'POINT(%f %f)' % (Y, X)
                geom = ogr.CreateGeometryFromWkt(wkt)
                featBefore = ogr.Feature(layerbefore.GetLayerDefn())
                featBefore.SetField('Elevation', float(minZValueBefore))
                featBefore.SetGeometry(geom)
                layerbefore.CreateFeature(featBefore)
                featAfter = ogr.Feature(layerbefore.GetLayerDefn())
                featAfter.SetField('Elevation', float(minZValueAfter))
                featAfter.SetGeometry(geom)
                layerafter.CreateFeature(featAfter)
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

parser = reqparse.RequestParser()
parser.add_argument('section', type=str)
class ProduceShapefile(Resource):
    # 根据库里高程点数据生成shapefile
    def get(self):
        data = parser.parse_args()
        section = data.get('section')
        uuidValue = str(uuid.uuid1())[0 : -13]
        stdinValue = section + '_' + str(uuidValue)
        newStdinValue = stdinValue.replace('-', '')
        print(newStdinValue)

        # 生成shapefile文件
        createShapefileHandle(newStdinValue, section)
        result = {
            'msg': '生成shapefile文件',
            'content': newStdinValue
        }
        return result
api.add_resource(ProduceShapefile, '/arcgis/produceshapefile/')
if __name__ == '__main__':
    app.run()