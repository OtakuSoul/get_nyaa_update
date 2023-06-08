# from plyer import notification
# from winotify import Notification, audio
import requests
from lxml import etree
import json
import time
import schedule
from datetime import datetime, timedelta
import os
import urllib
from re import match
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
# import io
import webbrowser
from win10toast_click import ToastNotifier


# 'https://sukebei.nyaa.si/?f=0&c=1_1&q='
url = 'https://sukebei.nyaa.si/user/hikiko123'
filename = "stored_data.json"


# 点击回调
def open_web(url=url):
    webbrowser.open(url)

# title 传入弹窗的标题
# message 弹窗的正文信息
# app_icon 这个是可选参数，传入ico图标文件的路径，显示在弹窗上。
# timeout 弹窗的显示时间，以秒（s）作为单位
# def plyer_notification(title,message,icon_name,timeout):
#     appname = 'nyaa更新提醒' # appname暂时无效或者我理解错误
#     # message = ''  # 正文信息
#     icon = get_full_filepath(icon_name)
#     notification.notify(
#         title=title, 
#         message=message,
#         app_name=appname,
#         timeout=timeout,
#         app_icon=icon
#         )
    
def notication_warning(message):
    title = "警告"
    icon_name = "warning.ico"
    timeout = 5
    # winotify_notification(title=title, message=message, icon_name=icon_name, timeout=timeout,type='warning')
    wintoast_natification(title=title, message=message, icon_name=icon_name, timeout=timeout,type='warning')
    # plyer_notification(title=title, message=message, icon_name=icon_name, timeout=timeout)


def notication_message(message="hikiko123上传了新内容，快去看！"):
    title = 'nyaa有新内容更新了'
    icon_name = "nyaa.ico"
    timeout = 5
    # winotify_notification(title=title, message=message, icon_name=icon_name, timeout=timeout,type='message')
    wintoast_natification(title=title, message=message, icon_name=icon_name, timeout=timeout,type='message')
    # plyer_notification(title=title, message=message, icon_name=icon_name, timeout=timeout)

 
# def winotify_notification(title,message,icon_name,timeout,type):
#     icon = get_full_filepath(icon_name)
#     toast = Notification(app_id="nyaa update",
#                     title=title,
#                     msg=message,
#                     icon=icon,
#                     )
#     if type == 'message':
#         toast.set_audio(audio.Mail, loop=False)
#         toast.add_actions(label="Button text", 
#                   launch=url)
#     else:
#         toast.set_audio(audio.Default, loop=False)
#     toast.show()
        


def wintoast_natification(title,message,icon_name,timeout,type):
    toaster = ToastNotifier()
    icon = get_full_filepath(icon_name)
    if type == "message":
        toaster.show_toast(title=title,msg=message,icon_path=icon,duration=timeout,threaded=True,callback_on_click=open_web)
    else:
        toaster.show_toast(title=title,msg=message,icon_path=icon,duration=timeout,threaded=True)


# winotify_notification()
 
# plyer_notification()

# 获取工作目录
def get_full_dirpath():
    return os.path.dirname(os.path.abspath(__file__))

# 获取文件路径
def get_full_filepath(filename):
    return os.path.join(get_full_dirpath(),filename)

# 将更新的数据写入文件中
def write_store_data(stored_data,filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(stored_data, f, indent=4, ensure_ascii=False)

# 更新第一条数据并传递message
def fromGatherListHandleMessageAndStore(gather_list, filepath):
    stored_data = {}
    stored_data["title"] = gather_list[0]["title"]
    stored_data["date"] = gather_list[0]["date"]
    stored_data["timestamp"] = gather_list[0]["timestamp"]
    write_store_data(stored_data, filepath)
    message = "有" +str(len(gather_list)) + "条更新\n"
    tmp_list = gather_list[:1]
    for anime_dict in tmp_list:
        message += anime_dict["title"] + '\n'
    return message

# 获取系统代理
def get_sys_proxy():
    system_proxy = urllib.request.getproxies().values()
    proxies = {}
    if system_proxy:
        #格式应该为 'http://ip:port'
        proxies["http"] = next(iter(system_proxy))
        proxies["https"] = next(iter(system_proxy))
    else:
        proxies = None
    return proxies

def monitor_website(filename, logger):
    stored_data = {}
    filepath = get_full_filepath(filename)
    # 如果文件不存在或者为空。则默认stored_data为空
    if os.path.exists(filepath):
        with open(filepath,"r",encoding="utf-8") as f:
            try:
                stored_data = json.load(f)
            except json.decoder.JSONDecodeError:
                pass
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}

    proxies = get_sys_proxy()

    # response = requests.get('https://sukebei.nyaa.si/user/hikiko123', proxies=proxies)
    try:
        response = requests.get(url, headers=headers, proxies=proxies,timeout=5)
    except:
        log_message = "网络错误，或代理错误，无法访问网页"
        logger.warning(log_message)
        notication_warning(message = log_message)
        return
    html = response.content.decode('utf-8')
    # print(html)
    node = etree.HTML(html)
    # 找到table中的tbody，tbody里面的就是所有的tr,xpath返回的是一个找到所有符合条件的列表，如果每个下面还有内容，可直接for循环指代，不需要再次xpath
    # 如tbody[0]获取tbody项，for循环直接指向tbody里面的tr
    # 但是在下面注释的for循环中，由于xpath返回的是tr的列表，每一项是一个tr，而不是里面的td，所以后续仍需指出后续的td
    tbody_html = node.xpath("//tbody")[0]
    message = ""
    # 获取现在的时间
    now_timestamp = datetime.now()
    ts = now_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    # 获取上个月的起始时间
    last_month_end = datetime(now_timestamp.year, now_timestamp.month, 1) - timedelta(days=1)
    last_month_start = datetime(last_month_end.year, last_month_end.month, 1)
    # datetime..timetuple()直接转化为struct_time格式
    last_month_timestamp = int(time.mktime(last_month_start.timetuple()))
    anime_gatherNowTime_list = []
    # print("1234")
    # tr确定到对应的表格中的行，返回的是第一页的row
    # for循环和list存储以当前日期为基准第一个到上个月发布日期为准的所有数据
    for index,anime_html in enumerate(tbody_html):
    # for index,anime_html in enumerate(node.xpath("/html/body/div/div[2]/div[1]/table/tbody//tr")):
        anime_dict = {}
        title = ""
        titles = anime_html.xpath("td[2]/a")
        for a_title in titles:
            # 获取名称，因为有多个a标签，选取[开头和.mp4结尾的为标签
            # if a_title.text.startswith("[") and a_title.text.endswith(".mp4"):
            if a_title.text != '\n\t\t\t\t\t\t':
                title = a_title.text
        if not title:
            log_message = "第" + str(index+1) + "解析失败"
            logger.warning(log_message)
            # print(ts,index+1,"解析失败")
            continue
        # 匹配发布时间，如果不成功使用上传时间为准，默认网址都会在title字段中有发布时间
        pattern = "\[\d{6}\].*"
        timestamp_compare = 0
        if match(pattern=pattern, string = title):
            # strptime将str转化为time_struct
            # mktime将time_struct转化为timestamp
            release_date = title[1:7]
            release_timeArray = time.strptime(release_date, "%y%m%d")
            release_timeStamp = int(time.mktime(release_timeArray))
            timestamp_compare = release_timeStamp
        else:
            timestamp_compare =int(anime_html.xpath("td[5]/@data-timestamp")[0])
        # 只选取第一页中到上个月为止的数据，默认不跨页
        if timestamp_compare < last_month_timestamp:
            break
        anime_dict["title"] = title
        # anime_dict["release_timeStamp"] = release_timeStamp
        # 上传时间
        # 选取时间戳字段，而不用td[5]/text()，因为时间可能与时间戳不一致
        anime_dict["timestamp"] = int(anime_html.xpath("td[5]/@data-timestamp")[0])
        # time.localtime将timestamp转化为time_struct
        # strftime将time_struct转化为str
        anime_dict["date"] = time.strftime("%Y-%m-%d %H:%M",time.localtime(anime_dict["timestamp"]))
        anime_gatherNowTime_list.append(anime_dict)
    
    if len(anime_gatherNowTime_list) == 0:
        log_message ="没有找到到上月为止的数据，请检查网页中是否存在近两月的数据，如有解析失败，则可能由于无法解析导致数据全部丢失"
        logger.warning(log_message)
        # print(ts, "没有找到到上月为止的数据，请检查网页中是否存在近两月的数据，如有解析失败，则可能由于无法解析导致数据全部丢失")
        return
    # 如果没有存储数据 或者 存储的时间戳异常，不可能比网页中最新的还新，则显示前两条更新的数据
    if not stored_data or stored_data["timestamp"] > anime_gatherNowTime_list[0]["timestamp"]:
        message = fromGatherListHandleMessageAndStore(anime_gatherNowTime_list,filepath)
    # 获取在存储时间之后的数据,只显示最近两个月的数据
    else:
        anime_gatherStoreTime_list = [x for x in anime_gatherNowTime_list if stored_data['timestamp'] < x['timestamp'] ]
        if len(anime_gatherStoreTime_list) > 0:
            message = fromGatherListHandleMessageAndStore(anime_gatherStoreTime_list, filepath)
    if message:
        log_message = message.replace('\n','\t',1).replace('\n','')
        logger.info(log_message)
        # print(ts,"更新了")
        notication_message(message=message)
    else:
        log_message = "没有更新内容"
        logger.info(log_message)
        # print(ts,"没有更新内容")


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logdir = "logs"
    logname = 'nyaa.log'
    datefmt = '%Y-%m-%d %H:%M:%S'
    log_full_dir = get_full_filepath(logdir)
    if not os.path.exists(log_full_dir):
        os.mkdir(log_full_dir)
    logpath = os.path.join(log_full_dir,logname)
    fh = TimedRotatingFileHandler(filename=logpath, when='D',interval=1 , backupCount=7, encoding='utf-8')
    # fh = logging.FileHandler(filename=logpath,mode='a',encoding="utf-8")
    sh = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("[%(asctime)s]-[%(levelname)s]-[Msg:%(message)s]",datefmt=datefmt)
    fh.setFormatter(fmt=fmt)
    sh.setFormatter(fmt=fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger






def sched_task(logger):
    schedule.clear()
    schedule.every(30).minutes.do(monitor_website,filename = filename, logger = logger)
    # 先立刻执行一次
    schedule.run_all()
    while True:
        schedule.run_pending()



if __name__ == "__main__":
    # 需要Python 3.7
    sys.stdout.reconfigure(encoding='utf-8')
    # 低版本可以使用这个方式
    # sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
    logger = get_logger()
    sched_task(logger)
