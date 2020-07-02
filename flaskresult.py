# 计算土方量
from flask import Flask, request, jsonify, render_template, make_response, send_from_directory
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
from osgeo import ogr, osr, gdal
from string import Template
import os
import math
import json
import uuid
import shutil
import xlrd
import zipfile
import subprocess
import pymysql
app = Flask(__name__)
CORS(app, origins='*', allow_headers='*')
api = Api(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_URL = os.path.join(BASE_DIR, 'static')
conn = pymysql.connect(host="localhost", user="root", password="847650632syj", db='xatreepipe')
cursor = conn.cursor()
DateTimeFormat = '%Y-%c-%d %H:%i:%s'
class EarthVolumeRecord(Resource):
    # 入库土方量数据
    def post(self):
        data = request.get_data()
        data_json = json.loads(data.decode('utf-8'))
        section = data_json['section']
        coding = data_json['coding']
        creater = data_json['creater']
        outfillUrl = data_json['outfillUrl']
        tableUrl = data_json['tableUrl']
        volumeTotal = data_json['volumeTotal']
        areaTotal = data_json['areaTotal']
        print(section)
        ID = str(uuid.uuid1())
        Sql = """
            INSERT INTO earthvolume_record(ID, Section, Coding, Creater, OutfillUrl, TableUrl, VolumeTotal, AreaTotal) 
            VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
        """ % (ID, section, coding, creater, outfillUrl, tableUrl, volumeTotal, areaTotal)
        res = cursor.execute(Sql)
        print(Sql)
        conn.commit()
        result = {
            'code': 1,
            'msg': 'ok',
            'content': ID,
        }
        return result
api.add_resource(EarthVolumeRecord, '/arcgis/earthvolumerecord/')

class UploadShapefileDegree(Resource):
    # 上传
    def post(self):
        section = request.form['section']
        file_type = request.form['filetype']
        file_obj = request.files['file']
        file_name = file_obj.filename.split('.zip')[0]
        uuidValue = str(uuid.uuid1())[0 : -13]
        stdinValue = section + '_' + str(uuidValue)
        newStdinValue = stdinValue.replace('-', '')
        processFile = os.path.join(static_URL, 'processFile', newStdinValue)
        if not os.path.exists(processFile):
            os.makedirs(processFile)
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
        features = []
        if dataSource is None:
            print('Could not open %s' % (shp_file))
        else:
            layer = dataSource.GetLayer(0)
            for i in range(layer.GetFeatureCount()):
                feature = layer.GetFeature(i)
                feadict = json.loads(feature.ExportToJson())
                geometry = feadict['geometry']
                properties = feadict['properties']
                if geometry['type'] == 'Point':
                    arr = geometry['coordinates']
                    Elevation = properties['Elevation']
                    wkt = 'POINT(%f %f)' %(arr[0], arr[1])
                    ID = uuid.uuid1()
                    features.append({
                        'ID': str(ID),
                        'Coding': i,
                        'Geom': wkt,
                        'lng': arr[0],
                        'lat': arr[1],
                        'GD': Elevation,
                        "Section": section,
                        "Type": file_type
                    })
                elif geometry['type'] == 'Polygon':
                    coordinates = geometry['coordinates']
                    coordinatesArr = coordinates[0]
                    wkt = 'POLYGON(('
                    for arr in coordinatesArr:
                        newc = str(arr[0]) + ' ' + str(arr[1])
                        wkt += newc + ','
                    finally_wkt = wkt[0: -1] + '))'
                    ID = uuid.uuid1()
                    features.append({
                        'ID': str(ID),
                        'Coding': i,
                        'Geom': finally_wkt,
                        "Section": section,
                        "Type": file_type
                    })
        print(features)
        result = {
            'code': 1,
            'msg': '成功',
            'content': newStdinValue,
            'features': features
        }
        return result
api.add_resource(UploadShapefileDegree, '/arcgis/uploadshapefiledegree/')

class DownloadOutFill(Resource):
    def get(self):
        filename = request.args.get('filename')
        return send_from_directory(static_URL + '/resultFile', filename=filename, as_attachment=True)
api.add_resource(DownloadOutFill, '/arcgis/downloadoutfill/')

class DownloadOutFillXlrd(Resource):
    def get(self):
        filename = request.args.get('filename')
        return send_from_directory(static_URL + '/resultFile', filename=filename, as_attachment=True)
api.add_resource(DownloadOutFillXlrd, '/arcgis/downloadoutfillxlrd/')

def MinZValueHandle(point_list, X, Y):
    minArr = []
    minZArr = []
    for point in point_list:
        wkt = point['the_geom']
        touyin_arr = wkt[6: -1].split(' ')
        Y_touyin = touyin_arr[0]
        X_touyin = touyin_arr[1]
        valueY = math.fabs(float(Y_touyin) - Y)
        valueX = math.fabs(float(X_touyin) - X)
        if valueY == 0:
            value = valueX
        elif valueX == 0:
            value = valueY
        else :
            value = math.hypot(valueX, valueY)
        minArr.append(value)
        minZArr.append(point['GD'])
    minValue = min(minArr)
    minKey= minArr.index(minValue)
    minZValue = minZArr[minKey]
    return minZValue

def createShapefileHandle (newStdinValue, beforeList, afterList, redlineList):
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
    # 坐标转换
    spatial = osr.SpatialReference()
    spatial.ImportFromEPSG(4326)

    layerBefore = beforeds.CreateLayer('point', spatial, ogr.wkbPoint)
    layerAfter = afterds.CreateLayer('point', spatial, ogr.wkbPoint)
    layerRedline = redlineds.CreateLayer('polygon', spatial, ogr.wkbPolygon)
    
    fieldf_elevation = ogr.FieldDefn('Elevation', ogr.OFTReal)
    fieldf_coding = ogr.FieldDefn('Coding', ogr.OFTReal)
    layerBefore.CreateField(fieldf_elevation)
    layerBefore.CreateField(fieldf_coding)
    layerAfter.CreateField(fieldf_elevation)
    layerAfter.CreateField(fieldf_coding)
    
    for point in beforeList:
        wkt = point['the_geom']
        geom_before = ogr.CreateGeometryFromWkt(wkt)
        feat = ogr.Feature(layerBefore.GetLayerDefn())
        feat.SetField('Elevation', point['GD'])
        feat.SetField('Coding', point['Title'])
        feat.SetGeometry(geom_before)
        layerBefore.CreateFeature(feat)

    for point in afterList:
        wkt = point['the_geom']
        geom_after = ogr.CreateGeometryFromWkt(wkt)
        feat = ogr.Feature(layerAfter.GetLayerDefn())
        feat.SetField('Elevation', point['GD'])
        feat.SetField('Coding', point['Title'])
        feat.SetGeometry(geom_after)
        layerAfter.CreateFeature(feat)
    for point in redlineList:
        wkt_redline =  point['the_geom']
        point_Arr = wkt_redline[9:-2].split(',')
        for index in range(len(point_Arr)):
            if index != 0:
                wkt_point = 'POINT(%s)' % point_Arr[index]
                touyin_arr= point_Arr[index].split(' ')
                Y = float(touyin_arr[0])
                X = float(touyin_arr[1])
                minZValueBefore = MinZValueHandle(beforeList, X, Y)
                minZValueAfter = MinZValueHandle(afterList, X, Y)
                geom_point = ogr.CreateGeometryFromWkt(wkt_point)

                featBefore = ogr.Feature(layerBefore.GetLayerDefn())
                featBefore.SetField('Elevation', float(minZValueBefore))
                featBefore.SetGeometry(geom_point)
                layerBefore.CreateFeature(featBefore)
                featAfter = ogr.Feature(layerAfter.GetLayerDefn())
                featAfter.SetField('Elevation', float(minZValueAfter))
                featAfter.SetGeometry(geom_point)
                layerAfter.CreateFeature(featAfter)
        geom_redline = ogr.CreateGeometryFromWkt(wkt_redline)
        featRedline = ogr.Feature(layerRedline.GetLayerDefn())
        featRedline.SetGeometry(geom_redline)
        layerRedline.CreateFeature(featRedline)
    beforeds.Destroy()
    afterds.Destroy()
    redlineds.Destroy()

class EarthVolumeCalculateDegree(Resource):
    # 土方量计算经纬度
    def post(self):
        data = request.get_data()
        data_json = json.loads(data.decode('utf-8'))
        section = data_json['section']
        beforeData = data_json['before']
        afterData = data_json['after']
        redlineData = data_json['redline']
        uuidValue = str(uuid.uuid1())[0 : -13]
        stdinValue = section + '_' + str(uuidValue)
        newStdinValue = stdinValue.replace('-', '')
        # 生成shapefile文件
        createShapefileHandle(newStdinValue, beforeData, afterData, redlineData)
        # 生成土方量
        try:
            arcGIS_file = os.path.join(static_URL, 'python', 'arcGIS.py')
            subprocess.check_call(['C:\Python27\ArcGIS10.6\python.exe', arcGIS_file, newStdinValue])
        except:
            result = {
                'code': 0,
                'msg': '土方量生成有误',
                'content': newStdinValue,
            }
            return result
        finally:
            # 删除多余文件
            processFile_URL = os.path.join(static_URL, 'processFile', newStdinValue)
            if os.path.exists(processFile_URL):
                shutil.rmtree(processFile_URL)
        attrTalbe_url = os.path.join(static_URL, 'resultFile', newStdinValue, 'outFill.xls')
        result_URL = os.path.join(static_URL, 'resultFile', newStdinValue)
        # 压缩文件
        zip_url = os.path.join(static_URL, 'resultFile', newStdinValue + '.zip')
        create_zipfile = zipfile.ZipFile(zip_url, mode='a', compression=zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(result_URL):
            fpath = dirpath.replace(result_URL, '')
            fpath = fpath and fpath + os.sep or ''
            for filename in filenames:
                create_zipfile.write(os.path.join(dirpath, filename), fpath + filename)
        create_zipfile.close()
        # 获取填挖方的面要素
        driver = ogr.GetDriverByName('ESRI Shapefile')
        outfillshp_file = os.path.join(result_URL, 'outFill.shp')
        dataSource = driver.Open(outfillshp_file, 0)
        # 获取体积/面积
        data = xlrd.open_workbook(attrTalbe_url)
        table = data.sheet_by_name('outFill')
        volumeTotal = 0
        areaTotal = 0
        TableList = []
        if dataSource is None:
            print('Could not open %s' % (outfillshp_file))
        else:
            layer = dataSource.GetLayer(0)
            for index in range(table.nrows):
                if index == 0:
                    pass
                else:
                    record = table.row_values(index)
                    volumeTotal += record[3]
                    areaTotal += record[4]
                    coord = ''
                    for i in range(layer.GetFeatureCount()):
                        feature = layer.GetFeature(i)
                        feadict = json.loads(feature.ExportToJson())
                        geometry = feadict['geometry']
                        properties = feadict['properties']
                        if properties['gridcode'] == record[1]:
                            coord = geometry['coordinates']
                    TableList.append({
                        'key': record[1],
                        'Count': record[2],
                        'Volume': record[3],
                        'Area': record[4],
                        'coord': coord
                    })
        result = {
            'code': 1,
            'msg': newStdinValue,
            'content': {
                'volumeTotal': round(volumeTotal, 2),
                'areaTotal': round(areaTotal, 2),
                'attrTalbe_url': newStdinValue + '/outFill.xls',
                'outfill_url': newStdinValue + '.zip',
                'TableList': TableList,
            }
        }
        return result
api.add_resource(EarthVolumeCalculateDegree, '/arcgis/earthvolumecalculatedegree/')
class EarthVolumeCalculate(Resource):
    # 土方量计算
    def post(self):
        data = request.get_data()
        data_json = json.loads(data.decode('utf-8'))
        section = data_json['section']
        beforeData = data_json['before']
        afterData = data_json['after']
        redlineData = data_json['redline']
        uuidValue = str(uuid.uuid1())[0 : -13]
        stdinValue = section + '_' + str(uuidValue)
        newStdinValue = stdinValue.replace('-', '')
        print(newStdinValue)
        # 生成shapefile文件
        createShapefileHandle(newStdinValue, beforeData, afterData, redlineData)
        # 生成土方量
        try:
            arcGIS_file = os.path.join(static_URL, 'python', 'arcGIS.py')
            subprocess.check_call(['C:\Python27\ArcGIS10.6\python.exe', arcGIS_file, newStdinValue])
        except:
            result = {
                'code': 0,
                'msg': '土方量生成有误',
                'content': newStdinValue,
            }
            return result
        finally:
            # 删除多余文件
            processFile_URL = os.path.join(static_URL, 'processFile', newStdinValue)
            if os.path.exists(processFile_URL):
                shutil.rmtree(processFile_URL)
        attrTalbe_url = os.path.join(static_URL, 'resultFile', newStdinValue, 'outFill.xls')
        result_URL = os.path.join(static_URL, 'resultFile', newStdinValue)
        # 压缩文件
        zip_url = os.path.join(static_URL, 'resultFile', newStdinValue + '.zip')
        create_zipfile = zipfile.ZipFile(zip_url, mode='a', compression=zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(result_URL):
            fpath = dirpath.replace(result_URL, '')
            fpath = fpath and fpath + os.sep or ''
            for filename in filenames:
                create_zipfile.write(os.path.join(dirpath, filename), fpath + filename)
        create_zipfile.close()
        # 获取填挖方的面要素
        driver = ogr.GetDriverByName('ESRI Shapefile')
        outfillshp_file = os.path.join(result_URL, 'outFill.shp')
        dataSource = driver.Open(outfillshp_file, 0)
        # 获取体积/面积
        data = xlrd.open_workbook(attrTalbe_url)
        table = data.sheet_by_name('outFill')
        volumeTotal = 0
        areaTotal = 0
        TableList = []
        if dataSource is None:
            print('Could not open %s' % (outfillshp_file))
        else:
            layer = dataSource.GetLayer(0)
            for index in range(table.nrows):
                if index == 0:
                    pass
                else:
                    record = table.row_values(index)
                    volumeTotal += record[3]
                    areaTotal += record[4]
                    coord = ''
                    for i in range(layer.GetFeatureCount()):
                        feature = layer.GetFeature(i)
                        feadict = json.loads(feature.ExportToJson())
                        geometry = feadict['geometry']
                        properties = feadict['properties']
                        if properties['gridcode'] == record[1]:
                            coord = geometry['coordinates']
                    TableList.append({
                        'key': record[1],
                        'Count': record[2],
                        'Volume': record[3],
                        'Area': record[4],
                        'coord': coord
                    })
        result = {
            'code': 1,
            'msg': newStdinValue,
            'content': {
                'volumeTotal': round(volumeTotal, 2),
                'areaTotal': round(areaTotal, 2),
                'attrTalbe_url': newStdinValue + '/outFill.xls',
                'outfill_url': newStdinValue + '.zip',
                'TableList': TableList,
            }
        }
        return result
api.add_resource(EarthVolumeCalculate, '/arcgis/earthvolumecalculate/')

class EarthVolumeImport(Resource):
    # 删除导入记录
    def delete(self, id):
        filetype = request.args.get('filetype')
        if filetype == 'before' or filetype == 'after':
            Sql = """
                DELETE FROM investigation_point WHERE ImportID = '%s'
            """ % id
            res = cursor.execute(Sql)
            conn.commit()
        else:
            Sql = """
                DELETE FROM investigation_polygon WHERE ImportID = '%s'
            """ % id
            res = cursor.execute(Sql)
            conn.commit()
        Sql_import = """
            DELETE FROM earthvolume_import WHERE ID = '%s'
        """ % id
        print(Sql_import)
        res_import = cursor.execute(Sql_import)
        conn.commit()
        if res_import == 1:
            msg = '删除成功，该次入库的数据全部删除'
        else:
            msg = '删除失败'
        result = {
            'code': 1,
            'msg': msg,
            'content': []
        }
        return result
api.add_resource(EarthVolumeImport, '/arcgis/earthvolumeimport/<string:id>/')

class EarthVolumeImports(Resource):
    # 查询导入列表
    def get(self):
        section = request.args.get('section')
        datatype = request.args.get('datatype')
        Sql = """
            SELECT ID, Section, DATE_FORMAT(CreateTime, '%s'), DataType, Creater 
            FROM earthvolume_import 
            WHERE Section like '%s%%' AND DataType = '%s'
        """ % (DateTimeFormat, section, datatype)
        cursor.execute(Sql)
        dataList = cursor.fetchall()
        content = []
        for record in dataList:
            content.append({
                'ID': record[0],
                'Section': record[1],
                'CreateTime': record[2],
                'DataType': record[3],
                'Creater': record[4],
            })
        result = {
            'code': 200,
            'msg': '',
            'content': content
        }
        return result
api.add_resource(EarthVolumeImports, '/arcgis/earthvolumeimports/')

class UploadShapefile(Resource):
    # 上传高程点/项目红线文件
    def post(self):
        section = request.form['section']
        file_type = request.form['filetype']
        file_obj = request.files['file']
        uuidValue = str(uuid.uuid1())[0 : -13]
        stdinValue = section + '_' + str(uuidValue)
        newStdinValue = stdinValue.replace('-', '')
        processFile = os.path.join(static_URL, 'processFile', newStdinValue)
        if not os.path.exists(processFile):
            os.makedirs(processFile)
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
        features = []
        if dataSource is None:
            print('Could not open %s' % (shp_file))
        else:
            layer = dataSource.GetLayer(0)
            for i in range(layer.GetFeatureCount()):
                feature = layer.GetFeature(i)
                feadict = json.loads(feature.ExportToJson())
                geometry = feadict['geometry']
                properties = feadict['properties']
                if geometry['type'] == 'Point':
                    arr = geometry['coordinates']
                    Elevation = properties['Elevation']
                    Coding = properties['Coding']
                    wkt = 'POINT(%f %f)' %(arr[0], arr[1])
                    print(wkt)
                    ID = uuid.uuid1()
                    features.append({
                        'ID': str(ID),
                        'Geom': wkt,
                        'GD': Elevation,
                        "Coding": Coding,
                        "Section": section,
                        "Type": file_type
                    })
                elif geometry['type'] == 'Polygon':
                    coordinates = geometry['coordinates']
                    coordinatesArr = coordinates[0]
                    wkt = 'POLYGON(('
                    for arr in coordinatesArr:
                        newc = str(arr[0]) + ' ' + str(arr[1])
                        wkt += newc + ','
                    finally_wkt = wkt[0: -1] + '))'
                    print(finally_wkt)
                    ID = uuid.uuid1()
                    features.append({
                        'ID': str(ID),
                        'Geom': finally_wkt,
                        "Section": section,
                        "Type": file_type
                    })
        result = {
            'features': features
        }
        return result
api.add_resource(UploadShapefile, '/arcgis/uploadshapefile/')

class InvestigationPoint(Resource):
    # 编辑高程点数据
    def put(self):
        data = request.get_data()
        data_json = json.loads(data.decode('utf-8'))
        ID = data_json['ID']
        Title = data_json['Title']
        Remark = data_json['Remark']
        GD = data_json['GD']
        update_value = "Title = '%s', Remark = '%s'" % (Title, Remark)
        if GD:
            update_value = update_value + ", GD = '%s'" % GD
        Sql = """
            UPDATE investigation_point SET %s WHERE ID = '%s'
        """ % (update_value, ID)
        print(Sql)
        res = cursor.execute(Sql)
        conn.commit()
        if res == 1:
            msg = '编辑高程点成功'
        else:
            msg = '编辑高程点失败'
        result = {
            'code': 1,
            'msg': msg,
            'content': ''
        }
        return result
api.add_resource(InvestigationPoint, '/arcgis/investigationpoint/')
class InvestigationPointMultiple(Resource):
    # 批量入库高程点数据
    def post(self):
        data = request.get_data()
        data_json = json.loads(data.decode('utf-8'))
        print(data_json)
        Section = data_json['Section']
        DataType = data_json['DataType']
        Creater = data_json['Creater']
        codes = []
        codeerr = 0
        codesecc = 0
        import_ID = str(uuid.uuid1())
        Sql_import = """
            INSERT INTO earthvolume_import(ID, Section, DataType, Creater) 
            VALUES('%s', '%s', '%s', '%s');
        """ % (import_ID, Section, DataType, Creater)
        cursor.execute(Sql_import)
        conn.commit()
        for record in data_json['content']:
            Coding = record['Coding']
            GD = record['GD']
            Geom = record['Geom']
            ID = record['ID']
            InvestigationType = 0
            if DataType == 'before' :
                InvestigationType = 0
            elif DataType == 'after' :
                InvestigationType = 1
            Sql = """
                INSERT INTO investigation_point(ID, Land, the_geom, InvestigationType, GD, Creater, Title, ImportID) 
                VALUES('%s', '%s', ST_GeometryFromText('%s', 4326), '%s', '%s', '%s', '%s', '%s');
            """ % (ID, Section, Geom, InvestigationType, GD, Creater, Coding, import_ID)
            res = cursor.execute(Sql)
            codes.append(res)
            if res == '0':
                codeerr += 1 
            else:
                codesecc += 1
            conn.commit()
            print(res)
        result = {
            'code': 1,
            'codes': codes,
            'msg': '新增成功%s条数据, 失败%s条数据' % (codesecc, codeerr),
            'content': import_ID
        }
        return result
    # 删除高程点数据
    def delete(self):
        data = request.get_data()
        json_data = json.loads(data.decode('utf-8'))
        section = json_data['section']
        Sql = "DELETE FROM investigation_point WHERE Land='%s'" % section
        res = cursor.execute(Sql)
        print(res)
        conn.commit()
        result = {
            'code': 1,
            'msg': '删除高程点成功',
            'content': '成功删除%s条数据' % res
        }
        return result
api.add_resource(InvestigationPointMultiple, '/arcgis/investigationpointMultiple/')

class InvestigationPolygon(Resource):
    # 编辑红线数据
    def put(self):
        data = request.get_data()
        data_json = json.loads(data.decode('utf-8'))
        print(data_json)
        pass
api.add_resource(InvestigationPolygon, '/arcgis/investigationpolygon/')

class InvestigationPolygonMultiple(Resource):
    # 入库红线数据
    def post(self):
        data = request.get_data()
        data_json = json.loads(data.decode('utf-8'))
        print(data_json)
        Section = data_json['Section']
        DataType = data_json['DataType']
        Creater = data_json['Creater']
        codes = []
        codeerr = 0
        codesecc = 0
        import_ID = str(uuid.uuid1())
        Sql_import = """
            INSERT INTO earthvolume_import(ID, Section, DataType, Creater) 
            VALUES('%s', '%s', '%s', '%s');
        """ % (import_ID, Section, DataType, Creater)
        cursor.execute(Sql_import)
        conn.commit()
        for record in data_json['content']:
            Geom = record['Geom']
            ID = record['ID']
            InvestigationType = 0
            if DataType == 'redline' :
                InvestigationType = 0
            Sql = """
                INSERT INTO investigation_polygon(ID, Land, the_geom, InvestigationType, Creater, ImportID) 
                VALUES('%s', '%s', ST_GeometryFromText('%s', 4326), '%s', '%s', '%s');
            """ % (ID, Section, Geom, InvestigationType, Creater, import_ID)
            res = cursor.execute(Sql)
            codes.append(res)
            if res == '0':
                codeerr += 1 
            else:
                codesecc += 1
            conn.commit()
            print(res)
        result = {
            'code': 1,
            'codes': codes,
            'msg': '新增成功%s条数据, 失败%s条数据' % (codesecc, codeerr),
            'content': import_ID
        }
        return result
api.add_resource(InvestigationPolygonMultiple, '/arcgis/investigationpolygonmultiple/')
class InvestigationDatas(Resource):
    # 获取高程点 / 项目红线列表数据
    def get(self):
        data = request.get_data()
        section = request.args.get('section')
        dataType = request.args.get('type')
        page = request.args.get('page')
        pagesize = request.args.get('pagesize')
        result = {
            'content': [],
            'pageinfo': {
                'total': 0,
                'page': 0
            }
        }
        if dataType == 'before' or dataType == 'after':
            if dataType == 'before':
                InvestigationType = 0
            else:
                InvestigationType = 1
            Sql = """
                SELECT ID, Land, st_astext(the_geom), InvestigationType, DATE_FORMAT(CreateTime, '%s'), Creater, Title, 
                Remark, DATE_FORMAT(UpdateTime, '%s'), Version, Pics, Audios, Videos, GD, XJ, TreeType, ImportID
                FROM investigation_point WHERE Land like '%s%%' AND InvestigationType = '%s'
            """ % (DateTimeFormat, DateTimeFormat, section, InvestigationType)
            res = cursor.execute(Sql)
            if res == 0:
                pass
            else:
                dataList = cursor.fetchall()
                result['pageinfo']['total'] = len(dataList)
                cursor.scroll(0, mode='absolute')
                if pagesize:
                    if page:
                        scrollValue = (int(page) - 1) * int(pagesize)
                        cursor.scroll(scrollValue, mode='absolute')
                        dataList = cursor.fetchmany(int(pagesize))
                        result['pageinfo']['page'] = int(page)
                for record in dataList:
                    result['content'].append({
                        'ID': record[0],
                        'Land': record[1],
                        'the_geom': record[2],
                        'InvestigationType': record[3],
                        'CreateTime': record[4],
                        'Creater': record[5],
                        'Title': record[6],
                        'Remark': record[7],
                        'UpdateTime': record[8],
                        'Version': record[9],
                        'Pics': record[10],
                        'Audios': record[11],
                        'Videos': record[12],
                        'GD': record[13],
                        'XJ': record[14],
                        'TreeType': record[15],
                        'ImportID': record[16]
                    })
        elif dataType == 'redline':
            Sql = """
                SELECT ID, Land, st_astext(the_geom), DATE_FORMAT(CreateTime, '%s'), Creater, Title, 
                Remark, DATE_FORMAT(UpdateTime, '%s'), Version, Pics, Audios, Videos, Area, ImportID
                FROM investigation_polygon WHERE Land like '%s%%'
            """ % (DateTimeFormat, DateTimeFormat, section)
            res = cursor.execute(Sql)
            if res == 0:
                pass
            else:
                dataObj = cursor.fetchone()
                result['pageinfo']['total'] = 1
                result['content'].append({
                    'ID': dataObj[0],
                    'Land': dataObj[1],
                    'the_geom': dataObj[2],
                    'CreateTime': dataObj[3],
                    'Creater': dataObj[4],
                    'Title': dataObj[5],
                    'Remark': dataObj[6],
                    'UpdateTime': dataObj[7],
                    'Version': dataObj[8],
                    'Pics': dataObj[9],
                    'Audios': dataObj[10],
                    'Videos': dataObj[11],
                    'Area': dataObj[12],
                    'ImportID': dataObj[13]
                })
        response = make_response(jsonify(result))
        return response
api.add_resource(InvestigationDatas, '/arcgis/investigationdatas/')
if __name__ == '__main__':
    app.run()