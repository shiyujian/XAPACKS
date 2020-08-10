# 查询会话ID
import requests
import time
from string import Template
from threading import Timer
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import pymysql
# conn = pymysql.connect(host="101.37.86.189", user="root", password="88060022", db='ocean_platform')
# cursor = conn.cursor()
chrome_options = Options()
chrome_options.add_argument('headless')
# # chrome_options.add_argument('lang=zh_CN.UTF-8')

# chrome_options.add_argument("Cookie='username=ojfU1wWU3Tz4GV66hOZtxr9daKBo; Hm_lvt_84473a6a12c8d159c951667173ed0678=1594100182; JSESSIONID=9F8E561CB82EC4FAEC8DB4D8B8E96B75; Hm_lvt_5a549381614f27b883ebd27bf0e218a0=1594100195,1594171875,1594619543,1595830335; hisvisit=HUADONGYUAN%203; userlon=121.414; userlat=36.45212000000001; userzoom=14'")
# # DateTimeFormat = "%Y-%m-%d %H:%M:%S"
# Headers = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
#     "Cookie": "username=shiyujian1314@qq.com; shiyujian1314@qq.com=48818238; Hm_lvt_84473a6a12c8d159c951667173ed0678=1594100182; JSESSIONID=9F8E561CB82EC4FAEC8DB4D8B8E96B75; Hm_lvt_5a549381614f27b883ebd27bf0e218a0=1594100195,1594171875,1594619543,1595830335; hisvisit=HUADONGYUAN%203; Hm_lpvt_5a549381614f27b883ebd27bf0e218a0=1595832393; userlon=121.414; userlat=36.45212000000001; userzoom=12",
# }
def Dialogue():
    # driver = webdriver.Chrome()
    # link_url = """
    #     http://www.hifleet.com/prelogin.do
    # """
    # driver.get(link_url)
    
    Headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Cookie": 'username=shiyujian1314@qq.com; shiyujian1314@qq.com=48818238; JSESSIONID=ACC4AE099AA0A0B73F603C0E12EA1EF9; userzoom=2; userlon=0; userlat=0; duetime=2020-08-11%2016%3A41%3A51; Hm_lvt_5a549381614f27b883ebd27bf0e218a0=1595830335,1595838080,1596069912,1596071835; Hm_lpvt_5a549381614f27b883ebd27bf0e218a0=1596074597'
    }
    rep = requests.post(url='http://www.hifleet.com/logincheck.do', params={
        'password': '48818238',
        'email': 'hiyujian1314@qq.com'
    }, headers=Headers)
    print(rep)
    print(rep.text)

    newwindow='window.open("http://www.hifleet.com/index.html")'
    driver.delete_all_cookies()
    driver.add_cookie({'name':'userzoom','value':'2'})
    driver.add_cookie({'name':'username','value':'shiyujian1314@qq.com'})
    driver.add_cookie({'name':'userlon','value':'0'})
    driver.add_cookie({'name':'userlat','value':'0'})
    driver.add_cookie({'name':'shiyujian1314@qq.com','value':'48818238'})
    driver.add_cookie({'name':'duetime','value':'2020-08-11%2016%3A41%3A51'})
    driver.add_cookie({'name':'JSESSIONID','value':'ACC4AE099AA0A0B73F603C0E12EA1EF9'})
    driver.add_cookie({'name':'Hm_lvt_5a549381614f27b883ebd27bf0e218a0','value':'1595830335,1595838080,1596069912,1596071835'})
    driver.add_cookie({'name':'Hm_lpvt_5a549381614f27b883ebd27bf0e218a0','value':'1596074597'})
    driver.execute_script(newwindow)
    cookie = driver.get_cookies()
    print(cookie)

    Headers2 = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Cookie": 'username=shiyujian1314@qq.com; shiyujian1314@qq.com=48818238; JSESSIONID=02BC4D3F3D7DCF5573DB696F39CF6CD2; userzoom=2; userlon=0; userlat=0; duetime=2020-08-11%2016%3A41%3A51; Hm_lvt_5a549381614f27b883ebd27bf0e218a0=1595830335,1595838080,1596069912,1596071835; Hm_lpvt_5a549381614f27b883ebd27bf0e218a0=1596074604'
    }
    rep = requests.get(url='http://www.hifleet.com/getMyArea.do', params={
    }, headers=Headers2)

    print(rep)
    print(rep.text)

    time.sleep(60)
    # rep = requests.post(url='http://www.hifleet.com/loginByWeChat.do', params={
    #     'code': '001rb2dL0gGRAa22cafL01XjdL0rb2dd'
    # }, headers=Headers)
    # print(rep)
    # print(rep.text)
    # driver = webdriver.Chrome()
    # link_url = """
    #     http://www.hifleet.com/getnewtrajectory.do?mmsis=414401240&startdates=2020-07-23+17%3A04%3A00&endates=2020-07-27+17%3A04%3A00&zoom=12&bbox=121.22791906738281%2C36.35084395173486%2C121.60008093261717%2C36.55326398752108
    # """
    # driver.get(link_url)
    # newwindow='window.open("http://www.hifleet.com/getnewtrajectory.do?mmsis=414401240&startdates=2020-07-23+17%3A04%3A00&endates=2020-07-27+17%3A04%3A00&zoom=12&bbox=121.22791906738281%2C36.35084395173486%2C121.60008093261717%2C36.55326398752108");'
    # driver.delete_all_cookies()
    # driver.add_cookie({'name':'JSESSIONID','value':'ACC4AE099AA0A0B73F603C0E12EA1EF7'})
    # driver.execute_script(newwindow)
    # time.sleep(60)

    # driver.add_cookie({
    #     'name': 'userzoom',
    #     'value': '14'
    # })
    # driver.add_cookie({
    #     'name': 'userlon',
    #     'value': '121.414'
    # })
    # driver.add_cookie({
    #     'name': 'Hm_lvt_84473a6a12c8d159c951667173ed0678',
    #     'value': '1594100182'
    # })
    # driver.add_cookie({
    #     'name': 'hisvisit',
    #     'value': 'HUADONGYUAN%203'
    # })
    # driver.add_cookie({
    #     'name': 'Hm_lvt_5a549381614f27b883ebd27bf0e218a0',
    #     'value': '1594100195,1594171875,1594619543,1595830335'
    # })
    # driver.add_cookie({
    #     'name': 'userlat',
    #     'value': '36.45212000000001'
    # })
    # driver.add_cookie({
    #     'name': 'JSESSIONID',
    #     'value': '9F8E561CB82EC4FAEC8DB4D8B8E96B75'
    # })
    # driver.add_cookie({
    #     'name': 'username',
    #     'value': 'ojfU1wWU3Tz4GV66hOZtxr9daKBo'
    # })
    # Headers = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    # }
    # rep = requests.get(url='http://www.hifleet.com/getnewtrajectory.do', params={
    #     'mmsis': '414401240',
    #     'startdates': '2020-07-23 14:46:00',
    #     'endates': '2020-07-27 14:46:00',
    #     'zoom': 12,
    #     'bbox': '121.22706076049805,36.35084395173486,121.60093923950194,36.55326398752108'
    # }, headers=Headers)
    # print(rep)
    # createTime = time.strftime(DateTimeFormat, time.localtime())
    # print(createTime)
    # driver.get(link_url, {
    #     'mmsis': '414401240',
    #     'startdates': '2020-07-23 14:46:00',
    #     'endates': '2020-07-27 14:46:00',
    #     'zoom': 12,
    #     'bbox': '121.22706076049805,36.35084395173486,121.60093923950194,36.55326398752108'
    # })
    # cookie = driver.get_cookies()
    # JSESSIONIDValue = ''
    # for record in cookie:
    #     if record['name'] == 'JSESSIONID':
    #         JSESSIONIDValue = record['value']
    # JSESSION = 'JSESSIONID=%s;' %(JSESSIONIDValue)
    # a = Template('username=ojfU1wWU3Tz4GV66hOZtxr9daKBo; Hm_lvt_84473a6a12c8d159c951667173ed0678=1594100182; JSESSIONID=${key}; Hm_lvt_5a549381614f27b883ebd27bf0e218a0=1594100195,1594171875,1594619543,1595830335; hisvisit=HUADONGYUAN%203; Hm_lpvt_5a549381614f27b883ebd27bf0e218a0=1595832393; userlon=121.414; userlat=36.45212000000001; userzoom=12')
    # Headers = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    #     "Cookie": a.substitute(key=JSESSIONIDValue)
    # }
    # print(Headers)
    # rep = requests.get(url='http://www.hifleet.com/getnewtrajectory.do', params={
    #     'mmsis': '414401240',
    #     'startdates': '2020-07-23 14:46:00',
    #     'endates': '2020-07-27 14:46:00',
    #     'zoom': 12,
    #     'bbox': '121.22706076049805,36.35084395173486,121.60093923950194,36.55326398752108'
    # }, headers=Headers)
    # print(rep)
    # JSESSIONStr = 'JSESSIONID=%s' % JSESSIONIDValue
    # print(JSESSIONStr)
    # Sql = """
    #     UPDATE pass_cookie SET pass_cookie = '%s', create_time = '%s' WHERE ID = 1
    # """ % (JSESSIONStr, createTime)
    # # Sql = """
    # #     INSERT INTO pass_cookie(pass_cookie, create_time)
    # #     VALUES('%s', '%s');
    # # """ % (JSESSIONIDValue, createTime)
    # codes = []
    # code = cursor.execute(Sql)
    # conn.commit()
    # codes.append(code)
    # result = {
    #     'codes': codes,
    #     'msg': 'ok',
    #     'content': '会话ID成功新增%d条，失败%d条' % (codes.count(1), codes.count(0))
    # }
    # print(result)
Dialogue()
# def loop_Body():
#     Dialogue()
# def loop_func(func, second):
#     while True:
#         timer = Timer(second, func)
#         timer.start()
#         timer.join()
# loop_func(loop_Body, 60)