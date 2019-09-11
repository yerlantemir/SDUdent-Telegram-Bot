REQ_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Length': '57',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'my.sdu.edu.kz',
    'Origin': 'https://my.sdu.edu.kz',
    'Referer': 'https://my.sdu.edu.kz/index.php?mod=grades',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}
REQ_PARAMS = {
    'ajx': '1',
    'mod': 'grades',
    'action': 'GetGrades',
    'yt': '1#1'
}
LOGIN_URL = "https://my.sdu.edu.kz/"

GRADE_STATES = ['1st midterm', '2nd midterm', 'final', 'average']

XPATH_AUTH = "//input[@name='LogIn']/@value"
# If block contains our grades,in has more than 4 tr blocks
NUM_TRS_IN_NEEDED_BLOCK = 4

XPATH_ABSENCES = './/td[@class="crtd alignleft"]/following::td[3]'

XPATH_SUBJECT_NAMES = './/td[@class="crtd alignleft"]/text()'

XPATH_TABLE_BLOCK = '//table[@id="coursesTable"]'

XPATH_TDS = './/td[@valign="top"]'


LOGIN, PASSWORD, ASK_DATA = range(3)

PHOTO, ASK_INDEX = range(2)

THRESHOLD_SIMILARITY = 0.6

