# 爬虫海事局
import requests
import re
import time
import asyncio
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
Headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Cookie": "FSSBBIl1UgzbN7N443S=9iHrYuX2kPlKp9ROGzoXAEkcVsAUf_rBF4GwHI1LgtLhk3pkd64cZaUutwB2LS_g; FSSBBIl1UgzbN7N80S=Y2Ms08cD3.Fbwj_KUyRPRobcsatjmNRR5FESRbI0CeyyzL74llHTmu57DpxF2Vus; Hm_lvt_89a42a8529b1127d2cd6fa639511a328=1592978122,1593307026,1593308364,1593317749; JSESSIONID=2wP5cYRrSlpZu24krq9hERSd217iGTjCUyShp5LJRpZo81VvpLBy!-1446521199; FSSBBIl1UgzbN7N80T=1suEYZOvAJxD3SkEojLGy2ji8ThB5t0xQNy_7ZHTnURzYnuc2dSNFAOb.jRYPpmi5HoJV7fIQ9DinzL0YK4RX6u8uvNDS5oBWoD9DsLkppcUFEt0hJZRkDCsjwMY.I7Bqjm5XxD467H6zA2god7deNwcDkIkrvNiBuI8My7LpFm5vNxKi8kgKfE_LvL_dR0Lq.dd5nCSyCmRfaKICoGsXAz8lSpKstgxx.vk.nz3YsdLt; Hm_lpvt_89a42a8529b1127d2cd6fa639511a328=1593325194; FSSBBIl1UgzbN7N443T=1c1mzFIMzdZoHeGZCj7r8rSbpOxSVQ58R.lSFg3CFfjN8gtwJamtQZaQClRiufuNg6K2DYWpjCTM7P_44p6ZdhUMX7b4mfGZfAWd7Ez0kwtvFvIb2.v1U35UuLQzvmfKSSCmSbcktYM1elYZzD6O3uCGISmSwNHjvIIwgF4t6vvfNIblsKSmBZ..pSOIhMbA9u1Id5pq8QE5CDNjVfEXikJw7YNTUv4un.ksPk4z_Cc.yKrp0Xo.Nr5X.21twfDGGBA",
}
regionWarnings = {
    '94DF14CE-1110-415D-A44E-67593E76619F': "上海海事局",
    'BDBA5FAD-6E5D-4867-9F97-0FCF8EFB8636': "天津海事局",
    'C8896863-B101-4C43-8705-536A03EB46FF': "辽宁海事局",
    '93B73989-D220-45F9-BC32-70A6EBA35180': "河北海事局",
    '36EA3354-C8F8-4953-ABA0-82D6D989C750': "山东海事局",
    '8E10EA74-EB9E-4C96-90F8-F891968ADD80': "浙江海事局",
    '7B084057-6038-4570-A0FB-44E9204C4B1D': "福建海事局",
    '1E478D40-9E85-4918-BF12-478B8A19F4A8': "广东海事局",
    '86DE2FFF-FF2C-47F9-8359-FD1F20D6508F': "广西海事局",
    'D3340711-057B-494B-8FA0-9EEDC4C5EAD9': "海南海事局",

    '93404234-06CC-4507-B2FB-8AF2492D2A3D': "长江海事局",
    'B5B0F3C7-630D-4967-B1E6-B06208575D15': "江苏海事局",
    '325FDC08-92B4-4313-A63E-E5C165BE98EC': "深圳海事局",
    'FA4501F3-DBE4-4F70-BC72-6F27132D4E04': "连云港海事局",
    'D14ED012-960B-4064-9712-70459A4A0D4D': "江苏省地方海事局",
    '533B3954-E373-4C81-83E9-7D85B76BC9C5': "江西省地方海事局",
}
regionWarningsArr = list(regionWarnings.keys())

# 航行警告
countWarnings = 4
def sailingWarnings():
    print('sailingWarnings开始')
    codes = []
    code = 0
    origin_name = ''
    global countWarnings
    global paramsRegion
    countWarnings = countWarnings + 1
    if countWarnings > 15:
        countWarnings = 0
    channelId = regionWarningsArr[countWarnings]
    if channelId in regionWarnings:
        origin_name = regionWarnings[channelId]
    session = HTMLSession()
    rep = session.get('https://www.msa.gov.cn/page/openInfo/articleList.do', params={
        'channelId': channelId,
        'pageNo': 5,
        'pageSize': 1,
        'isParent': 0
    }, headers=Headers)
    for li in rep.html.find('.main_list_li'):
        a = li.find('a', first=True)
        textSpan = a.find('.name', first=True)
        timeSpan = a.find('.time', first=True)
        title = textSpan.text
        create_time = timeSpan.text
        link_url = 'https' + a.attrs['href'][4:]
        articleArr = link_url.split('articleId=')
        if len(articleArr) == 2:
            origin_id = articleArr[1][0:36]
        else:
            origin_id = link_url[-41 : -5]
        finalWKT = ''
        patternChinese = re.compile(r'[\u4E00-\u9FA5]')
        print(title)
        if origin_id:
            SelectSql = """
                SELECT *
                FROM maritime_info 
                WHERE origin_id = '%s' AND origin_no = '%s'
            """ % (origin_id, channelId)
            SelectCode = cursor.execute(SelectSql)
            if SelectCode == 1:
                code = 2
                codes.append(code)
                print('已存在略过')
                continue
        if len(patternChinese.findall(title)) == 0:
            code = 2
            codes.append(code)
            print('舍弃全英文')
            continue
        # 打开页面
        driver = webdriver.Chrome(options=chrome_options)
        print(link_url)
        driver.get(link_url)
        cookie = driver.get_cookies()
        cookieStr = ''
        for record in cookie:
            cookieStr = cookieStr + '%s=%s; ' % (record['name'], record['value'])
        finalCookie = cookieStr[0:-2]
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Cookie": finalCookie,
        }
        driver.quit()
        session = HTMLSession()
        response = session.get(link_url, headers=headers)
        if response.status_code != 200:
            code = 4
            codes.append(code)
            print('未成功打开页面')
            continue
        print('成功打开页面')
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        content = response.html.find('#ch_p', first=True).text.split('收藏')[0]
        patternYear = re.compile(r'(\d{4})\s?\u5e74')
        patternMonth = re.compile(r'([1-9]|[1][0-2])\s?\u6708')
        patternDay = re.compile(r'([1-9]|[1-3][0-9])\s?\u65e5')
        patternHour = re.compile(r'(\d{4})\s?\u65f6')
        yearArr = patternYear.findall(content)
        mouthArr = patternMonth.findall(content)
        dayArr = patternDay.findall(content)
        hourArr = patternHour.findall(content)
        defaultYear = time.strftime("%Y", time.localtime())
        # 度分秒格式1 38°51′41″N　121°38′12″E 度分秒格式2 40°37′38.8″N  122°07′48.2″E 度分秒格式3 40°40′16″.43N/121°58′01″.62E
        patternXSecond = re.compile(r'\D(\d{2})°(\d{2})′(\d+)(\.\d+)?″(\.\d+)?N')
        patternYSecond = re.compile(r'\D(\d{3})°(\d{2})′(\d+)(\.\d+)?″(\.\d+)?E') # 度分秒格式
        # 度分格式1 A：20°00.000′N、108°27.834′E；# 度分格式2 29-41.26N 122-31.31E 度分格式3 38°47′718N,122°11′036E；
        patternXMinute = re.compile(r'\D(\d{2})[°-](\d{2})(\.\d+)?′?(\d+)?N')
        patternYMinute = re.compile(r'\D(\d{3})[°-](\d{2})(\.\d+)?′?(\d+)?E')
        resultX = []
        resultY = []
        coordXArr = []
        coordYArr = []
        if len(patternXSecond.findall(content)) > 0 and len(patternYSecond.findall(content)) > 0:
            resultX = patternXSecond.findall(content)
            resultY = patternYSecond.findall(content)
            for X in resultX:
                second = int(X[2])
                if X[3]:
                    second = int(X[2]) + float(X[3])
                elif X[4]:
                    second = int(X[2]) + float(X[4])
                coordX = format(int(X[0]) + int(X[1]) / 60 + second / 3600, '.7f')
                coordXArr.append(coordX)
            for Y in resultY:
                second = int(Y[2])
                if Y[3]:
                    second = int(Y[2]) + float(Y[3])
                elif Y[4]:
                    second = int(Y[2]) + float(Y[4])
                coordY = format(int(Y[0]) + int(Y[1]) / 60 + second / 3600, '.7f')
                coordYArr.append(coordY)
        elif len(patternXMinute.findall(content)) > 0 and len(patternYMinute.findall(content)) > 0:
            resultX = patternXMinute.findall(content)
            resultY = patternYMinute.findall(content)
            for X in resultX:
                minute = int(X[1])
                if X[2]:
                    minute = int(X[1]) + float(X[2])
                coordX = format(int(X[0]) + minute / 60, '.7f')
                coordXArr.append(coordX)
            for Y in resultY:
                minute = int(Y[1])
                if Y[2]:
                    minute = int(Y[1]) + float(Y[2])
                coordY = format(int(Y[0]) + minute / 60, '.7f')
                coordYArr.append(coordY)
        print(resultX)
        print(resultY)
        # 有中心半径的
        if content.find('为中心') > -1 or content.find('半径') > -1:
            patternMi = re.compile(r'\D(\d+)[米m]')
            resultMi = patternMi.findall(content)
            radius = 0
            if resultMi[0]:
                radius = int(resultMi[0])
            finalWKT = "POINT(%s %s)" % (coordXArr[0], coordYArr[0])
            Sql = """
                INSERT INTO maritime_info(origin_id, link_url, title, create_time, origin_name, origin_no, type, content, radius, center_coord) 
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s'));
            """ % (origin_id, link_url, title, create_time, origin_name, channelId, '1', content, radius, finalWKT)
            print('圆形区域')
        # 有多边形区域的
        elif content.find('连线') > -1 or content.find('试航水域') > -1:
            PolygonWKT = 'POLYGON(('
            PointArr = []
            for index in range(len(coordXArr)):
                X = coordXArr[index]
                Y = coordYArr[index]
                PolygonWKT = PolygonWKT + X + ' ' + Y + ', '
                PointArr.append(X + ' ' + Y)
            finalWKT = PolygonWKT + PointArr[0] + '))'
            if len(dayArr) == 2:
                # 多天
                if len(mouthArr) == 2:
                    # 多月
                    if len(yearArr) == 2:
                        # 多年
                        startDate = '%s-%s-%s' % (yearArr[0], mouthArr[0], dayArr[0])
                        endDate = '%s-%s-%s' % (yearArr[1], mouthArr[1], dayArr[1])
                    else:
                        startDate = '%s-%s-%s' % (defaultYear, mouthArr[0], dayArr[0])
                        endDate = '%s-%s-%s' % (defaultYear, mouthArr[1], dayArr[1])
                else:
                    # 单月
                    startDate = '%s-%s-%s' % (defaultYear, mouthArr[0], dayArr[0])
                    endDate = '%s-%s-%s' % (defaultYear, mouthArr[0], dayArr[1])
            else:
                # 单天
                startDate = '%s-%s-%s' % (defaultYear, mouthArr[0], dayArr[0])
                endDate = '%s-%s-%s' % (defaultYear, mouthArr[0], dayArr[0])
            if len(hourArr) == 2:
                startTime = '%s:%s:00' % (hourArr[0][0:2], hourArr[0][2:4])
                endTime = '%s:%s:00' % (hourArr[1][0:2], hourArr[1][2:4])
                if hourArr[0][0:2] == '24':
                    startTime = '23:59:59'
                if hourArr[1][0:2] == '24':
                    endTime = '23:59:59'
            elif len(hourArr) == 0:
                startTime = '00:00:00'
                endTime = '23:59:59'
            else:
                startTime = '%s:%s:00' % (hourArr[0][0:2], hourArr[0][2:4])
                endTime = '%s:%s:00' % (hourArr[0][0:2], hourArr[0][2:4])
                if hourArr[0][0:2] == '24':
                    startTime = '23:59:59'
                    endTime = '23:59:59'
            startDateTime = startDate + ' ' + startTime
            endDateTime = endDate + ' ' + endTime
            if startDateTime == endDateTime:
                # 没有时间范围
                Sql = """
                    INSERT INTO maritime_info(origin_id, link_url, title, create_time, origin_name, origin_no, type, content) 
                    VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
                """ % (origin_id, link_url, title, create_time, origin_name, channelId, '1', content)
            else:
                Sql = """
                    INSERT INTO maritime_info(origin_id, link_url, title, create_time, origin_name, origin_no, type, content, start_time, end_time, the_geom) 
                    VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s'));
                """ % (origin_id, link_url, title, create_time, origin_name, channelId, '1', content, startDateTime, endDateTime, finalWKT) 
                print('多边形')
        
        elif len(resultX) < 3 or len(resultY) < 3 or len(resultX) != len(resultY) or len(dayArr) < 1: 
            Sql = """
                INSERT INTO maritime_info(origin_id, link_url, title, create_time, origin_name, origin_no, type, content) 
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
            """ % (origin_id, link_url, title, create_time, origin_name, channelId, '1', content)
        else:
            Sql = """
                INSERT INTO maritime_info(origin_id, link_url, title, create_time, origin_name, origin_no, type, content) 
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
            """ % (origin_id, link_url, title, create_time, origin_name, channelId, '1', content)
        try:
            print(Sql)
            code = cursor.execute(Sql)
            conn.commit()
        except:
            code = 0
            print('入库失败')
        codes.append(code)
    result = {
        'codes': codes, # 1成功新增 2 已存在 3 英文不入库 4 页面打不开 0 新增失败
        'msg': 'ok',
        'content': '%s_航行警告成功新增%d条，已存在%d条，英文版%d条，未打开%d条，失败%d条' % (origin_name, codes.count(1), codes.count(2), codes.count(3), codes.count(4), codes.count(0)),
    }
    print(result)

sailingWarnings()
