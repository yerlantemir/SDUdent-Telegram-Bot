FROM python:3.7

RUN pip install python-telegram-bot
RUN pip install selenium
RUN pip install beautifulsoup4
RUN pip install pyrebase
RUN pip install python-firebase
RUN pip install requests
RUn pip install telebot 

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python /app/setup.py