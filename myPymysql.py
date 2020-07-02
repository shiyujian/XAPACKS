# 数据库连接
from flask import Flask, request, jsonify, render_template, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
from osgeo import ogr, osr, gdal
from string import Template
import os
import json
import uuid
import zipfile
import pymysql
app = Flask(__name__)
CORS(app, allow_headers='*')
api = Api(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_URL = os.path.join(BASE_DIR, 'static')
conn = pymysql.connect(host="localhost", user="root", password="847650632syj", db='xatreepipe')
cursor = conn.cursor()
DateTimeFormat = '%Y-%c-%d %H:%i:%s'
Sql = """
    INSERT INTO investigation_point(ID, Land, the_geom, Remark, GD) 
    VALUES('9cea8b21-abbc-11ea-aa12-544810bf656f', 'P193-01-01', ST_GeometryFromText('POINT(4.000000 9.000000)', 4326), 'afrter', '3.0');
"""
cursor.execute(Sql)
conn.commit()