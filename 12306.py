import requests
import base64
import re
import config

login_page_url = 'https://kyfw.12306.cn/otn/resources/login.html'
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}
session = requests.session()#自动处理cookie
session.headers.update(headers)#更新headers 反爬
# print(session.headers)

#获取cookie
cookie_url = 'https://kyfw.12306.cn/otn/login/conf'
response = session.get(cookie_url)
# print(session.cookies)

#下载验证码
captcha_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&1543046094418&callback=jQuery1910039553863543768886_1543044966858&_=1543044966860'
response = session.get(captcha_url)
data = response.text
img_base64 = re.findall(r'"image":"(.*?)"',data)[0]
# print(img_base64)

#转换成图片
img_data = base64.b64decode(img_base64)
img_file = open('./images/验证码.jpg','wb')
img_file.write(img_data)
img_file.close()

#校验验证码
def get_point(index):
    map = {
        '1':'37,46',
        '2':'110,46',
        '3':'181,46',
        '4':'253,46',
        '5':'37,116',
        '6':'110,116',
        '7':'181,116',
        '8':'253,116',
    }
    index = index.split(',')
    temp = []
    for item in index:
        temp.append(map[item])
    print(temp)
    return ','.join(temp)

check_captcha = 'https://kyfw.12306.cn/passport/captcha/captcha-check?callback=jQuery191025775112970659064_1543047229106&rand=sjrand&login_site=E&_=1543047229109'
# print(check_captcha)
response = session.get(check_captcha,params={'answer':get_point(input('请输入正确坐标>>:'))})
# print(response.text)
res = response.text
code = re.findall(r'"result_code":"(.*?)"',res)[0]
print(code,type(code))
if code == '4':
    print('验证码校验成功!')
    login_url = 'https://kyfw.12306.cn/passport/web/login'
    form_data = {
        'username':config.username,
        'password':config.password,
        'appid':'otn',
    }
    response = session.post(login_url,data=form_data)
    print(response.text)
    res = response.json()
    print(res["result_message"])
    # 校验用户名，密码
    if res["result_code"] == 0:
        print('用户名密码校验成功')
        #获取权限token
        uamtk_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        response = session.post(uamtk_url,data={'appid':'otn'})
        print(response.text)
        res = response.json()
        if res["result_code"] == 0:
            print('获取token成功!')
            check_token = 'https://kyfw.12306.cn/otn/uamauthclient'
            response = session.post(check_token,data={'tk':res["newapptk"]})
            print(response.text)

else:
    print('验证码校验失败!')
