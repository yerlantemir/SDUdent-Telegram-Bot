from selenium import webdriver
import secret_data as sd
from time import sleep
from bs4 import BeautifulSoup
import datetime

username = sd.get_login()
password = sd.get_password()

driver = webdriver.Firefox()

driver.get('https://my.sdu.edu.kz/')

class Subject:

    def __init__(self,title,teacher_name,room,weekday,timeAtt):
        
        self.title = title
        self.teacher_name = teacher_name
        self.room = room
        self.weekday = weekday
        self.timeAtt = timeAtt.split(':')
        self.time = datetime.time(int(self.timeAtt[0]),int(self.timeAtt[1]),00)
        
    

    def __lt__ (self, other):
        
        if self.weekday == other.weekday:
            return self.time < other.time
        return self.weekday < other.weekday

    def __eq__ (self, other):
        return self.weekday == other.weekday and self.time == other.time

    def __repr__(self):
        return '{},{},{},{},{}'.format(self.title,self.teacher_name,self.room,self.weekday,self.time)


def login():
    global driver
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_class_name("q-button").click()

def get_to_schedule():
    login()
    
    global driver
    driver.find_element_by_css_selector(".leftLinks a[href^='?mod=schedule'] ").click()
    sleep(2)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    return html
    

def get_schedule_data():
    
    html = get_to_schedule()
    soup = BeautifulSoup(html,'lxml')
    
    lists = soup.find('div',id='div_results').find_all('tr')
    subjects = []

    #i = time
    #j = day
    
    for i in range(1,len(lists)):
        
        tds = lists[i].find_all('td')

        for j in range(1,len(tds)):
            
            span = tds[j].find('span')

            if(len(span) == 1):
                continue

            
            title = span.find('a')["title"]
            
            imgs = span.find_all('img')
            teacher_name = imgs[0]["title"]
            
            room = imgs[1]["title"]
            
            time = tds[0].find('span').text
            subject = Subject(title,teacher_name,room,j,time)
            
            subjects.append(subject)
            
    subjects = sorted(subjects)
    for l in range(len(subjects)):
        print(subjects[l])
    

get_schedule_data()

