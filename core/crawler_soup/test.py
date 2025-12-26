from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def convert_to_datetime(text):
    if 'hours ago' in text:
        hours = int(text.split()[0])
        timedelta_obj = timedelta(hours=hours)
    elif 'days ago' in text:
        days = int(text.split()[0])
        timedelta_obj = timedelta(days=days)
    elif 'minutes ago' in text:
        minutes = int(text.split()[0])
        timedelta_obj = timedelta(minutes=minutes)
    elif 'hour ago' in text:
        hours = int(text.split()[0])
        timedelta_obj = timedelta(hours=hours)
    elif 'minute ago' in text:
        minutes = int(text.split()[0])
        timedelta_obj = timedelta(minutes=minutes)
    elif 'day ago' in text:
        days = 0
        timedelta_obj = timedelta(days=days)
    elif 'just now' in text:
        datetime_obj = datetime.now()
        return datetime_obj
    else:
        raise ValueError("Geçersiz zaman formatı: {}".format(text))

    datetime_obj = datetime.now() - timedelta_obj
    return datetime_obj


def getposts():

    subreddit = "Home"
    
    url = f"https://www.reddit.com/r/{subreddit}/new/"

    chrome_options = Options()
    chrome_options.add_argument("--headless")


    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # time.sleep(30)

   
    scroll_pause_time = 1
    scroll_count = 0
    max_scroll_count = 10


    while scroll_count < max_scroll_count:
        time.sleep(scroll_pause_time)
        scroll_count += 1



    content = driver.page_source

    driver.quit()

    # time.sleep(30)

    soup = BeautifulSoup(content, 'html.parser')

    # time.sleep(30)


    posts = soup.find_all('div', {'data-testid': 'post-container'})

    #time.sleep(10)

    len_posts=len(posts)

    if(len_posts>0):
        for post in posts:
            title = post.find('h3', {'class': '_eYtD2XCVieq6emjKBH3m'}).getText()
            vote = post.find('div', {'class': '_1rZYMD_4xY3gRcSS3p8ODO _3a2ZHWaih05DgAOtvu6cIo'}).getText()
            author = post.find('div', {'class': '_2mHuuvyV9doV3zwbZPtIPG'}).getText().split("/")[1]
            text = post.find('div', {'class': 'Chtkt3BCZQruf0LtmFg2c'})
            img = post.find('div', {'class': '_3Oa0THmZ3f5iZXAQ0hBJ0k'})
            if img is None:
                img = post.find('img', {'class': '_1dwExqTGJH2jnA-MYGkEL-'})
                if img is not None:
                    img = img.find("img")
            else:
                img = img.find("img")
                img = img["src"]


            datetimeText = post.find('span', {'class', '_2VF2J19pUIMSLJFky-7PEI'}).getText()
            datetime = convert_to_datetime(datetimeText)
            
            if vote=="Vote":
                vote = 0
            else:
                vote = int(vote)
            print(f'Başlık {title}')
            print(f'Vote:{vote}')
            print(type(vote))
            print(f'Author:{author}')
            print(f'Datetime:{datetime}')
            if text is not None:
                print(f"Text:{text.getText()}")
            if img is not None:
                print(f"Image:{img}")
            print("\n")

getposts()
        