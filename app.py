import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

def check(phone_number):
        # 1. 创建session并设置cookies
        session = requests.Session()
        session.cookies.update({
            'permitExtJSESSIONID': '5590DA79D7CD34F84A73A5717B4D7C95',
            'paiwu80_cookie': '45380249',
        })

        # 2. 获取页面和CSRF token
        get_response = session.get('https://permit.mee.gov.cn/permitExt/outside/getusercode.jsp')
        csrf_token = re.search(r'name=["\']csrfRandom["\'][^>]*value=["\']([^"\']+)["\']', get_response.text, re.IGNORECASE).group(1)

        # 3. 发送POST请求
        response = session.post(
            'https://permit.mee.gov.cn/permitExt/outside/getusercode',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://permit.mee.gov.cn',
                'Referer': 'https://permit.mee.gov.cn/permitExt/outside/getusercode.jsp',
            },
            data={
                'csrfRandom': csrf_token,
                'email': phone_number,
                'validtype': '5',
            }
        )
        print(f"状态码: {response.status_code}")

        # 4. 解析数据
        soup = BeautifulSoup(response.text, 'lxml')
        context_ = soup.select('h3')[0].text
        # 5. 返回响应
        if not context_:
            return {
                'status': 'error',
                'message': '未发现注册结果'
            }

        registered = False
        if "账号已经发送到您的手机" in context_:
            registered = True
        elif "您输入的手机号不存在" in context_:
            registered = False
        else:
            return {
                'status': 'unknown',
                'message': f'未知状态:{context_}'
            }
        return {
            'status': 'success',
            'registered': registered,
            'message': context_
        }


@app.route('/api/<number>')
def api_check(number):

    if not number or not re.match(r'^1[3-9]\d{9}$', number):
        return {
            'status': 'Invalid',
            'message': '无效号码，请输入11位有效号码'
        }

    result = check(number)
    return jsonify(result)

if __name__ == '__main__':
    context = ('certificate.crt', 'private.key')
    app.run(host='0.0.0.0', port=5000, ssl_context=context)


