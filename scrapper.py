import requests
from lxml import html
import secret_data as sd
from bs4 import BeautifulSoup

name = sd.get_login()
password = sd.get_password()

payload = {"username": name, "password" : password, "LogIn":" Log in "}
session_requests = requests.session()

login_url = "https://my.sdu.edu.kz/"
result = session_requests.get(login_url)

tree = html.fromstring(result.text)
auth_token = list(set(tree.xpath("//input[@name='LogIn']/@value")))[0]

result = session_requests.post(
    login_url,
    data=payload,
    headers = dict(referer = login_url)
)

url = 'https://my.sdu.edu.kz/index.php?mod=schedule'
result = session_requests.get(url,headers = dict(referer = url))

tree = html.fromstring(result.content)

soup = BeautifulSoup(result.content,'html.parser')

print(soup)