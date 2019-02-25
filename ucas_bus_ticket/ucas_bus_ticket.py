
# coding: utf-8

# In[ ]:


#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
    Author: Xingwang Xiong
    Date:    2019-02-22
'''

import time
import json
import requests
from bs4 import BeautifulSoup


# `Server 酱` 的**SCKEY 码**，用于发送 订单信息 到微信。

# In[ ]:


SCKEY='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'


# 下面是**用户信息** 和 **车次信息**

# In[ ]:


header={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}
# sep.ucas.ac.cn 账号和密码
usr = 'XXXXXXXXXXXXXXXXXX'
pwd = 'XXXXXXXXXXXXXXXXX'
# 学号
sno = 'XXXXXXXXXXXXXXXXXX'
# 联系电话
tel = 'XXXXXXXXXXXXXXXXXX'
# 路线时间
route_time = '13:00:00'
# 预定时间
booking_date = '2019-02-27'


# In[ ]:


session = requests.Session()


# In[ ]:


i1=session.get('http://sep.ucas.ac.cn/slogin')
i1_cookies=i1.cookies.get_dict()


# In[ ]:


# 登录到 sep.ucas.ac.cn
i2 = session.post(url='http://sep.ucas.ac.cn/slogin',data={'userName': usr, 'pwd': pwd, 'site': 'yikatongzhifu', 'sb': 'sb'}, cookies=i1_cookies)


# In[ ]:


# 进入一卡通支付
i3=session.get('http://sep.ucas.ac.cn/portal/site/311')
i4=session.get(url='http://payment.ucas.ac.cn/NetWorkUI/sepLoginAction!findbyIdserial.do?idserial='+sno,data={'idserial': sno}, headers=header)


# In[ ]:


# 获取车次详情
i5=session.post(url='http://payment.ucas.ac.cn/NetWorkUI/queryBusByDate', data={"bookingdate": '2019-02-25', "factorycode": "R001"})
# 输出 booking_date 当天所有的车次，用于调试
# print(json.dumps(i5.json(), sort_keys=True, indent=4, ensure_ascii=False))
# 路线编号, 路线名称, 路线详情
route_code, route_name, route_detail = (None, None, None)
print(json.dumps(i5.json(), sort_keys=True, indent=4, ensure_ascii=False))
for route in i5.json()['routelist']:
    if route['routetime'] == route_time:
        route_code = route['routecode']
        route_name = route['routename']
        route_detail = route['routedetail']
        break
assert route_code != None and route_name != None, '路线不存在'
print('您选择了 [%s] 的校车\n\t路线编号(route_code)：%s, \n\t路线名称(route_name): %s, \n\t路线详情(route_detail): %s\n' % (route_time, route_code, route_name, route_detail))


# In[ ]:


i6=session.post(url='http://payment.ucas.ac.cn/NetWorkUI/queryRemainingSeats', data={'routecode': route_code, 'bookingdate': booking_date, 'factorycode': 'R001'})
assert i6.json()['returncode'] == 'SUCCESS', json.dumps(i6.json(), sort_keys=True, indent=4, ensure_ascii=False)
free_seat=int(i6.json()['returndata']['freeseat'])
print(free_seat)
assert free_seat > 0, '所选的班车没有座位啦！:( } \n' + json.dumps(i6.json(), sort_keys=True, indent=4, ensure_ascii=False)
i6=session.post(url='http://payment.ucas.ac.cn/NetWorkUI/openReservedBusInfoConfirm', data={ "carno": route_code, "payProjectId":"4", "factorycode":"R001", "payamtstr":"6.00", "freeseat": free_seat, "routecode": route_code, "bookingdate": booking_date, "routeName": route_name, "payAmt":"6.00"})


# 轮询发送`创建订单`的请求。如果支付成功，那么支付链接即为：
# - 电脑端：`'http://payment.ucas.ac.cn/NetWorkUI/showUserSelectPayType25'+str(i7.json()['payOrderTrade']['id'])`
# - 手机端：`'http://payment.ucas.ac.cn/MNetWorkUI/showUserSelectPayType25'+str(i7.json()['payOrderTrade']['id'])`

# In[ ]:


while True:
    i7=session.post(url='http://payment.ucas.ac.cn/NetWorkUI/reservedBusCreateOrder', data={ "routecode": route_code, "payAmt":"6.00", "bookingdate": booking_date, "payProjectId":"4", "tel": tel, "factorycode":"R001" })
    print(json.dumps(i7.json(), sort_keys=True, indent=4, ensure_ascii=False))
    break
    if i7.json()['returncode'] == 'SUCCESS': break
    time.sleep(5)


# 然后，通过`Server 酱`将支付页面推送到您的微信上。需要用Github 账号去`Server 酱`上注册一个**SCKEY码**。
# `Server 酱`的使用方法可以参考其官网：http://sc.ftqq.com/3.version

# In[ ]:


requests.post(url='https://sc.ftqq.com/%s.send' % SCKEY, data={"text": "UCAS 校车订单请尽快支付~", "desp": "- 移动端：http://payment.ucas.ac.cn/MNetWorkUI/showUserSelectPayType25%s\n\n- 电脑端：http://payment.ucas.ac.cn/NetWorkUI/showUserSelectPayType25%s" % (str(i7.json()['payOrderTrade']['id']), str(i7.json()['payOrderTrade']['id'])) })

