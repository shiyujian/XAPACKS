# 查询会话ID
import requests
import time
from threading import Timer
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import pymysql
conn = pymysql.connect(host="101.37.86.189", user="root", password="88060022", db='ocean_platform')
cursor = conn.cursor()
chrome_options = Options()
chrome_options.add_argument('headless')
DateTimeFormat = "%Y-%m-%d %H:%M:%S"
def Dialogue():
    driver = webdriver.Chrome(options=chrome_options)
    link_url = 'http://www.hifleet.com/queryMyFleetsShips.do'
    driver.get(link_url)
    cookie = driver.get_cookies()
    JSESSIONIDValue = ''
    for record in cookie:
        if record['name'] == 'JSESSIONID':
            JSESSIONIDValue = record['value']
    print(cookie)
    print(JSESSIONIDValue)
    createTime = time.strftime(DateTimeFormat, time.localtime())
    print(createTime)
    Sql = """
        UPDATE pass_cookie SET pass_cookie = '%s', create_time = '%s' WHERE ID = 0
    """ % (JSESSIONIDValue, createTime)
    # Sql = """
    #     INSERT INTO pass_cookie(pass_cookie, create_time)
    #     VALUES('%s', '%s');
    # """ % (JSESSIONIDValue, createTime)
    codes = []
    code = cursor.execute(Sql)
    conn.commit()
    codes.append(code)
    result = {
        'codes': codes,
        'msg': 'ok',
        'content': '会话ID成功新增%d条，失败%d条' % (codes.count(1), codes.count(0))
    }
    print(result)
# Dialogue()
def loop_Body():
    Dialogue()
def loop_func(func, second):
    while True:
        timer = Timer(second, func)
        timer.start()
        timer.join()
loop_func(loop_Body, 60)