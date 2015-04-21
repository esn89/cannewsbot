import os
import praw
import requests

from selenium import webdriver
from PIL import Image
from xvfbwrapper import Xvfb
from config_bot import *

# Check that the file that contains my bot's username and password exists
if not os.path.isfile("config_bot.py"):
    print "You need a config file"
    exit(1)

# Login and bot info ===================
user_agent = ("CanNewsIMG")
r = praw.Reddit(user_agent=user_agent)
r.login(REDDIT_USERNAME, REDDIT_PASS)
# ======================================

# Have we run this before?
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
# Else we have run this before, so open list:
else:
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = filter(None, posts_replied_to)


vdisplay = Xvfb()
vdisplay.start()
fox = webdriver.Firefox()


def getScreenShot(url):
    fox.get(url)

    element = fox.find_element_by_id('content')
    comment = fox.find_element_by_id('storytools')

    end = comment.location
    location = element.location
    size = element.size

    fox.save_screenshot('screenshot.jpg')
    im = Image.open('screenshot.jpg')

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    # The 150 is to trim away a bit of the comments header
    # - 180 for CBC
    bottom = location['y'] + end['y'] - 180

    im = im.crop((left, top, right, bottom))
    im.save('screenshot.jpg', "JPEG")

# ======

reddits = {'canada'}

posts = r.get_domain_listing('cbc.ca', sort='hot', limit=10)
for s in posts:
    # checks to see if it is mobile
    if 'ca/news/' in str(s.url):
        # it isn't a mobile link, check if i commented on that post before:
        if s.id not in posts_replied_to:
            getScreenShot(s.url.rstrip())

            response = requests.post(
                url="http://pomf.se/upload.php",
                files={"files[]": open('screenshot.jpg', "rb")})

            link = "http://a.pomf.se/" + response.text.split('"')[17]
            print link

fox.quit()
vdisplay.stop()
# getScreenShot('http://www.cbc.ca/news/trending/maple-syrup-could-help-fight-bacterial-infections-canadian-scientists-find-1.3037681')
