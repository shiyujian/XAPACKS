# 查询会话ID中国港口
import requests
import time
from string import Template
from threading import Timer
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
chrome_options = Options()
chrome_options.add_argument('headless')

def Dialogue():
    Headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Cookie": 'jsid=4337d4bb-0834-4873-985b-10b89e52c06f; Hm_lvt_112cc63ae7d0082ab4d30ec2c3a16614=1596089672; UM_distinctid=1739e9ddfd530-0351a279b538f2-31607305-15f900-1739e9ddfd69c4; CNZZDATA3453251=cnzz_eid%3D1948899232-1596090987-%26ntime%3D1596090987; Hm_lpvt_112cc63ae7d0082ab4d30ec2c3a16614=1596094094'
    }
    rep = requests.post(url='http://ship.chinaports.com/Login/UserInfo', params={
    }, headers=Headers)
    print(rep)
    print(rep.text)
Dialogue()