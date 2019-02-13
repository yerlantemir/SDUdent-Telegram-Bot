import requests
from bs4 import BeautifulSoup

USERNAME = "170103024"
PASSWORD = "aapbxzam1999"

LOGIN_URL     = "https://my.sdu.edu.kz/"
DASHBOARD_URL = "https://my.sdu.edu.kz/index.php?mod=schedule"

def listLinks():
    s = requests.Session()

    # Perform login
    result = s.post(LOGIN_URL, data={
        "Student number": USERNAME, 
        "Password": PASSWORD
    })
    print(result)
    # Scrape url
    html = s.get(DASHBOARD_URL).content
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.select("div.repo-list--repo > a"):
        print("{}\t{}".format(link.text, link.attrs["href"]))
        print('hheey')



listLinks()


















