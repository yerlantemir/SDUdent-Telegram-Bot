import requests
from lxml import html
import json
import constants
from PIL import Image
import urllib
from model import utils


def get_semester_data(username, password):
    tree = login(username, password)
    last_table = tree.xpath(constants.XPATH_TABLE_BLOCK)[-1]
    all_tds = last_table.xpath(constants.XPATH_TDS)

    # have 2 different blocks,one block with grades,second with assignments, we need first
    needed_tds = [td for td in all_tds if len(td.xpath('.//tr')) > constants.NUM_TRS_IN_NEEDED_BLOCK]

    subject_names = last_table.xpath(constants.XPATH_SUBJECT_NAMES)

    absences = [absence.xpath('.//text()')[0].replace(u'\xa0', u' ') for absence in
                last_table.xpath(constants.XPATH_ABSENCES)]
    grades = get_grades_data(needed_tds)
    semester_data = {}

    for index, subject_name in enumerate(subject_names):
        grades[index]['attendance'] = absences[index]
        semester_data[subject_name] = grades[index]

    return semester_data


def login(username, password, for_picture=False):
    payload = {"username": username, "password": password, "LogIn": " Log in "}
    session_requests = requests.session()

    session_requests.get(constants.LOGIN_URL)

    res = session_requests.post(
        constants.LOGIN_URL,
        data=payload,
        headers=dict(referer=constants.LOGIN_URL)
    )
    # if we login just to take picture, we just need response , because picture of user located on the first page
    if for_picture:
        return res

    url_of_grades = constants.LOGIN_URL + '/index.php'
    result2 = session_requests.post(url_of_grades, data=constants.REQ_PARAMS, headers=constants.REQ_HEADERS)
    tree = html.fromstring(json.loads(result2.text[1:])['DATA'])

    return tree


def get_user_info(username, password):

    response = login(username, password, for_picture=True)
    tree = html.fromstring(response.content)
    pic = tree.xpath("//img[@alt='Student']")[0]
    url = f'https://my.sdu.edu.kz/{pic.values()[0]}'
    resp = urllib.request.urlopen(url)
    image = Image.open(resp)
    feature = utils.get_feature(image)

    tds = tree.xpath('//td[@nowrap="nowrap"]')
    name_surname = tds[2].text_content()
    program = tds[5].text_content()

    return {'name_surname':name_surname,'program':program,'feature':feature.tolist()}


def get_grades_data(needed_tds):
    grades = []

    for td in needed_tds:
        trs_with_grade = td.xpath('.//tr')[3:]
        grade_for_subject = {}
        for index, tr in enumerate(trs_with_grade):
            grade = tr.xpath('.//*[position()=2]')[0].text_content().strip()
            grade_for_subject[constants.GRADE_STATES[index]] = grade
        grades.append(grade_for_subject)

    return grades


