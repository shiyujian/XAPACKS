import os
import xlrd
import uuid
value1 = uuid.uuid1()
value2 = uuid.uuid1()
print(value1)
print(str(value2)[0 : -13])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_URL = os.path.join(BASE_DIR)
resultExcel_URL = os.path.join(static_URL, 'resultExcel', 'P1930101_2289cb1ea3e011ea9ca37440bb207f18.xls')
# with open(resultExcel_URL, 'rb') as xlsfile:
#         list = xlsfile.readlines()
#         print(list)
data = xlrd.open_workbook(resultExcel_URL)
table = data.sheet_by_name('P1930101_2289cb1ea3e011ea9ca3')
colArr3 = table.col_values(3)
colArr4 = table.col_values(4)
print(colArr3)
print(colArr4)
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
print(volume)
print(area)
