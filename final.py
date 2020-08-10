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
countWeather = 1
countWarnings = 3
countNotice = 16
Headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Cookie": "FSSBBIl1UgzbN7N443S=9iHrYuX2kPlKp9ROGzoXAEkcVsAUf_rBF4GwHI1LgtLhk3pkd64cZaUutwB2LS_g; FSSBBIl1UgzbN7N80S=Y2Ms08cD3.Fbwj_KUyRPRobcsatjmNRR5FESRbI0CeyyzL74llHTmu57DpxF2Vus; Hm_lvt_89a42a8529b1127d2cd6fa639511a328=1592978122,1593307026,1593308364,1593317749; JSESSIONID=2wP5cYRrSlpZu24krq9hERSd217iGTjCUyShp5LJRpZo81VvpLBy!-1446521199; FSSBBIl1UgzbN7N80T=1suEYZOvAJxD3SkEojLGy2ji8ThB5t0xQNy_7ZHTnURzYnuc2dSNFAOb.jRYPpmi5HoJV7fIQ9DinzL0YK4RX6u8uvNDS5oBWoD9DsLkppcUFEt0hJZRkDCsjwMY.I7Bqjm5XxD467H6zA2god7deNwcDkIkrvNiBuI8My7LpFm5vNxKi8kgKfE_LvL_dR0Lq.dd5nCSyCmRfaKICoGsXAz8lSpKstgxx.vk.nz3YsdLt; Hm_lpvt_89a42a8529b1127d2cd6fa639511a328=1593325194; FSSBBIl1UgzbN7N443T=1c1mzFIMzdZoHeGZCj7r8rSbpOxSVQ58R.lSFg3CFfjN8gtwJamtQZaQClRiufuNg6K2DYWpjCTM7P_44p6ZdhUMX7b4mfGZfAWd7Ez0kwtvFvIb2.v1U35UuLQzvmfKSSCmSbcktYM1elYZzD6O3uCGISmSwNHjvIIwgF4t6vvfNIblsKSmBZ..pSOIhMbA9u1Id5pq8QE5CDNjVfEXikJw7YNTUv4un.ksPk4z_Cc.yKrp0Xo.Nr5X.21twfDGGBA",
}
regionWeather = {
    'NorthSea': "北部海区",
    'EastSea': "东部海区",
    'SouthSea': "南部海区",
}
regionNotice = {
    '8DBDED82-F3E5-413B-824E-51445C79726C': "上海海事局",
    '2410A8D3-6F58-469B-89B6-4910C40590AE': "天津海事局",
    '50763510-C4FC-4F01-80ED-D95F3304F47E': "辽宁海事局",
    'F24BC59D-2AA3-4F33-8A1F-6EFA3BED3C93': "河北海事局",
    'E8A9BF8F-7A10-4C13-BAD3-7A6A80A85612': "山东海事局",
    'DC8D821B-39FB-4690-8FD5-0924C86A7AC7': "浙江海事局",
    '3D725583-AC13-4DFC-B74A-A8C47B14A164': "福建海事局",
    '32FA3793-3941-48F7-B5C3-EC112D2BF8AF': "广东海事局",
    '8375B077-B2CF-4281-A46B-68E2FF8AA08F': "广西海事局",
    '5EB28631-6746-4A6F-AAA1-FCA5BFF0A2A9': "海南海事局",

    'FB8539BB-3EEF-4C84-B2D8-8046A3F0FA36': "长江海事局",
    'BD86D1EE-D69D-4A1F-918C-438F6E750071': "江苏海事局",
    '262E87DA-2376-497E-8641-8B877EB91584': "黑龙江海事局",
    '9A9209E8-7533-462E-8CA4-6A13B1709752': "深圳海事局",
    '23E8B7D1-F2BD-411E-A9AE-F24F27C706C5': "连云港海事局",
    '6E5E69A7-33FF-4B64-B59D-D7584E28695B': "重庆市地方海事局",
    '5BF518AA-3B6B-46FD-985E-61DE4155BCDC': "江苏省地方海事局",
    '85D97B81-B449-445F-A512-9DD96B0514CD': "山东省地方海事局",
    'B14708F9-04FD-4916-B47C-FA38A5EB9925': "浙江省地方海事局",
    'B10AE251-A585-459F-8D35-5CC65ACE002F': "江西省地方海事局",
    
    'EDF6BD24-2E7B-4F39-A069-9F0CE8077662': "福建省地方海事局",
    '9BEAC18F-D909-4796-9693-A24E6467ACC6': "湖南省地方海事局",
    '9DD3C7B1-75B4-4AAE-8143-6228DAB7DE1A': "湖北省地方海事局",
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
regionWeatherArr = list(regionWeather.keys())
regionNoticeArr = list(regionNotice.keys())
regionWarningsArr = list(regionWarnings.keys())
# 气象信息
# def weatherInfo():
#     print('weatherInfo开始')
#     codes = []
#     origin_name = ''
#     global countWeather
#     global paramsRegion
#     countWeather = countWeather + 1
#     if countWeather > 2:
#         countWeather = 0
#     weatherOrigin = regionWeatherArr[countWeather]
#     if weatherOrigin in regionWeather:
#         origin_name = regionWeather[weatherOrigin]
#     rep = requests.get(url='https://www.msa.gov.cn/msacncms_weather/query/', params={
#         'weatherOrigin': weatherOrigin,
#         'pageNum': 1,
#         'pageSize': 10,
#     }, headers=Headers)
#     weatherinfoJson = rep.json()
#     if 'success' in weatherinfoJson:
#         weatherData = weatherinfoJson['weather']['data']
#         for record in weatherData:
#             try:
#                 Sql = """
#                     INSERT INTO maritime_info(origin_id, origin_no, origin_name, create_time, content, title, type) 
#                     VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s');
#                 """ % (record['weatherId'], record['weatherOrigin'], origin_name, record['weatherDate'], record['weatherContent'], record['weatherTitle'], '2')
#                 print(Sql)
#                 code = cursor.execute(Sql)
#                 conn.commit()
#             except pymysql.err.IntegrityError:
#                 print('记录已存在')
#                 code = 0
#             except:
#                 code = 4
#             codes.append(code)
#         result = {
#             'codes': codes,
#             'msg': 'ok',
#             'content': '%s_气象信息成功新增%d条，已存在%d条, 其他%d条' % (origin_name, codes.count(1), codes.count(0), codes.count(4))
#         }
#         print(result)

# 航行通告
def sailingNotice():
    print('sailingNotice开始')
    codes = []
    code = 0
    origin_name = ''
    global countNotice
    global paramsRegion
    countNotice = countNotice + 1
    if countNotice > 22:
        countNotice = 0
    channelId = regionNoticeArr[countNotice]
    if channelId in regionNotice:
        origin_name = regionNotice[channelId]
    session = HTMLSession()
    rep = session.get('https://www.msa.gov.cn/page/openInfo/articleList.do', params={
        'channelId': channelId,
        'pageNo': 1,
        'pageSize': 10,
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
        content = ''
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
            code = 3
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
        # 成功打开页面
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        content = response.html.find('#ch_p', first=True).text.split('收藏')[0]
        patternYear = re.compile(r'(\d{4})\s?\u5e74')
        patternMonth = re.compile(r'([1-9]|[1][0-2])\s?\u6708')
        patternDay = re.compile(r'([1-9]|[1-3][0-9])\s?\u65e5')
        patternHour = re.compile(r'(\d{2,4})\s?\u65f6')
        # print(content)
        patternXSecond = re.compile(r'(\d{2})°(\d{2})′(\d+)″[N][\W]') # 度分秒格式 38°51′41″N　121°38′12″E
        patternYSecond = re.compile(r'[\W](\d{3})°(\d{2})′(\d+)″[E]') # 度分秒格式
        patternXMinute = re.compile(r'\D(\d{2})[°-](\d{2}.\d+)[′]?N') # 度分格式 A：20°00.000′N、108°27.834′E；# 度分格式 29-41.26N 122-31.31E
        patternYMinute = re.compile(r'\D(\d{3})[°-](\d{2}.\d+)[′]?E')
        yearArr = patternYear.findall(content)
        mouthArr = patternMonth.findall(content)
        dayArr = patternDay.findall(content)
        hourArr = patternHour.findall(content)
        print(yearArr)
        print(mouthArr)
        print(dayArr)
        print(hourArr)
        coordType = ''
        resultX = []
        resultY = []
        if len(patternXSecond.findall(content)) > 0 and len(patternYSecond.findall(content)) > 0:
            resultX = patternXSecond.findall(content)
            resultY = patternYSecond.findall(content)
            coordType = 'Second'
        if len(patternXMinute.findall(content)) > 0 and len(patternYMinute.findall(content)) > 0:
            resultX = patternXMinute.findall(content)
            resultY = patternYMinute.findall(content)
            coordType = 'Minute'
        defaultYear = time.strftime("%Y", time.localtime())
        print(coordType)
        print(resultX)
        print(resultY)
        if len(resultX) < 3 or len(resultY) < 3 or len(resultX) != len(resultY) or len(dayArr) < 1 or content.find('拖带') > -1:
            print('没有区域坐标')
            Sql = """
                INSERT INTO maritime_info(origin_id, link_url, title, create_time, origin_name, origin_no, type, content) 
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
            """ % (origin_id, link_url, title, create_time, origin_name, channelId, '0', content)
        else:
            coordXArr = []
            coordYArr = []
            if coordType == 'Second':
                for X in resultX:
                    coordX = format(int(X[0]) + int(X[1]) / 60 + int(X[2]) / 3600, '.7f')
                    coordXArr.append(coordX)
                for Y in resultY:
                    coordY = format(int(Y[0]) + int(Y[1]) / 60 + int(Y[2]) / 3600, '.7f')
                    coordYArr.append(coordY)
            elif coordType == 'Minute':
                for X in resultX:
                    coordX = format(int(X[0]) + float(X[1]) / 60, '.7f')
                    coordXArr.append(coordX)
                for Y in resultY:
                    coordY = format(int(Y[0]) + float(Y[1]) / 60, '.7f')
                    coordYArr.append(coordY)
            PolygonWKT = 'POLYGON(('
            PointArr = []
            for index in range(len(coordXArr)):
                X = coordXArr[index]
                Y = coordYArr[index]
                PolygonWKT = PolygonWKT + X + ' ' + Y + ', '
                PointArr.append(X + ' ' + Y)
            finalWKT = PolygonWKT + PointArr[0] + '))'
            if len(dayArr) > 1:
                # 多天
                if len(mouthArr) > 1:
                    # 多月
                    if len(yearArr) > 1:
                        # 多年
                        startDate = '%s-%s-%s' % (yearArr[0], mouthArr[0], dayArr[0])
                        endDate = '%s-%s-%s' % (yearArr[1], mouthArr[1], dayArr[1])
                    elif len(yearArr) == 1:
                        startDate = '%s-%s-%s' % (defaultYear, mouthArr[0], dayArr[0])
                        endDate = '%s-%s-%s' % (defaultYear, mouthArr[1], dayArr[1])
                elif len(mouthArr) == 1:
                    # 单月
                    startDate = '%s-%s-%s' % (defaultYear, mouthArr[0], dayArr[0])
                    endDate = '%s-%s-%s' % (defaultYear, mouthArr[0], dayArr[1])
            elif len(dayArr) == 1:
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
                """ % (origin_id, link_url, title, create_time, origin_name, channelId, '0', content)
            else:
                Sql = """
                    INSERT INTO maritime_info(origin_id, link_url, title, create_time, origin_name, origin_no, type, content, start_time, end_time, the_geom) 
                    VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ST_GeomFromText('%s'));
                """ % (origin_id, link_url, title, create_time, origin_name, channelId, '0', content, startDateTime, endDateTime, finalWKT) 
        try:
            print(Sql)
            code = cursor.execute(Sql)
            conn.commit()
        except:
            code = 0
            print('入库失败')
        codes.append(code)
    result = {
        'codes': codes, # 1成功 2 已存在 3 英文版 4 未打开 0 失败
        'msg': 'ok',
        'content': '%s_航行警告成功新增%d条，已存在%d条，英文版%d条，未打开%d条，失败%d条' % (origin_name, codes.count(1), codes.count(2), codes.count(3), codes.count(4), codes.count(0)),
    }
    print(result)

# 航行警告
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
        'pageNo': 1,
        'pageSize': 10,
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
        content = ''
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
            code = 3
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
        driver.quit()
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Cookie": finalCookie,
        }
        session = HTMLSession()
        response = session.get(link_url, headers=headers)
        if response.status_code != 200:
            print('未成功打开页面')
            code = 4
            codes.append(code)
            continue
        print('成功打开页面')
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        content = response.html.find('#ch_p', first=True).text.split('收藏')[0]
        patternYear = re.compile(r'(\d{4})\s?\u5e74')
        patternMonth = re.compile(r'([1-9]|[1][0-2])\s?\u6708')
        patternDay = re.compile(r'([1-9]|[1-3][0-9])\s?\u65e5')
        patternHour = re.compile(r'(\d{4})\s?\u65f6')
        # 度分秒格式1 38°51′41″N　121°38′12″E 度分秒格式2 40°37′38.8″N  122°07′48.2″E 度分秒格式3 40°40′16″.43N/121°58′01″.62E
        patternXSecond = re.compile(r'\D(\d{2})°(\d{2})′(\d+)(\.\d+)?″(\.\d+)?N')
        patternYSecond = re.compile(r'\D(\d{3})°(\d{2})′(\d+)(\.\d+)?″(\.\d+)?E') # 度分秒格式
        # 度分格式1 A：20°00.000′N、108°27.834′E；# 度分格式2 29-41.26N 122-31.31E 度分格式3 38°47′718N,122°11′036E；
        patternXMinute = re.compile(r'\D(\d{2})[°-](\d{2})(\.\d+)?′?(\d+)?N')
        patternYMinute = re.compile(r'\D(\d{3})[°-](\d{2})(\.\d+)?′?(\d+)?E')
        yearArr = patternYear.findall(content)
        mouthArr = patternMonth.findall(content)
        dayArr = patternDay.findall(content)
        hourArr = patternHour.findall(content)
        resultX = []
        resultY = []
        coordXArr = []
        coordYArr = []
        if len(patternXSecond.findall(content)) > 0 and len(patternYSecond.findall(content)) > 0:
            resultX = patternXSecond.findall(content)
            resultY = patternYSecond.findall(content)
            for X in resultX:
                coordX = format(int(X[0]) + int(X[1]) / 60 + int(X[2]) / 3600, '.7f')
                coordXArr.append(coordX)
            for Y in resultY:
                coordY = format(int(Y[0]) + int(Y[1]) / 60 + int(Y[2]) / 3600, '.7f')
                coordYArr.append(coordY)
        elif len(patternXMinute.findall(content)) > 0 and len(patternYMinute.findall(content)) > 0:
            resultX = patternXMinute.findall(content)
            resultY = patternYMinute.findall(content)
            for X in resultX:
                coordX = format(int(X[0]) + float(X[1]) / 60, '.7f')
                coordXArr.append(coordX)
            for Y in resultY:
                coordY = format(int(Y[0]) + float(Y[1]) / 60, '.7f')
                coordYArr.append(coordY)
        print(resultX)
        print(resultY)
        defaultYear = time.strftime("%Y", time.localtime())
        if len(resultX) < 3 or len(resultY) < 3 or len(resultX) != len(resultY) or len(dayArr) < 1:
            print('没有区域坐标') 
            Sql = """
                INSERT INTO maritime_info(origin_id, link_url, title, create_time, origin_name, origin_no, type, content) 
                VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
            """ % (origin_id, link_url, title, create_time, origin_name, channelId, '1', content)
        else:
            PolygonWKT = 'POLYGON(('
            PointArr = []
            for index in range(len(coordXArr)):
                X = coordXArr[index]
                Y = coordYArr[index]
                PolygonWKT = PolygonWKT + X + ' ' + Y + ', '
                PointArr.append(X + ' ' + Y)
            finalWKT = PolygonWKT + PointArr[0] + '))'
            print(finalWKT)
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

# sailingWarnings()
# sailingNotice()

def loop_Body():
    # asyncio.run(main())
    # weatherInfo()
    # sailingWarnings()
    sailingNotice()
def loop_func(func, second):
    while True:
        timer = Timer(second, func)
        timer.start()
        timer.join()
loop_func(loop_Body, 10)


