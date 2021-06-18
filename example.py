from typing import Dict
from BurbnBot import Burbnbot
from InstagramAPI import InstagramAPI
import json
import time

bot = Burbnbot()


#faster way to get data
api = InstagramAPI(USERNAME, PASS)
api.login()
user_id = api.username_id

def getTotalFollowers():
    followers = []
    next_max_id = True
    while next_max_id:
        # first iteration hack
        if next_max_id is True:
            next_max_id = ''

        _ = api.getUserFollowers(user_id, maxid=next_max_id)
        followers.extend(api.LastJson.get('users', []))
        next_max_id = api.LastJson.get('next_max_id', '')
    return followers

def getTotalFollowing():
    followers = []
    next_max_id = True
    while next_max_id:
        # first iteration hack
        if next_max_id is True:
            next_max_id = ''

        _ = api.getUserFollowings(user_id, maxid=next_max_id)
        followers.extend(api.LastJson.get('users', []))
        next_max_id = api.LastJson.get('next_max_id', '')
    return followers

def nonFollowers(followers, following):
    nonFollowers = {}
    dictFollowers = {}
    for follower in followers:
        dictFollowers[follower['username']] = follower['pk']

    for followedUser in following:
        if followedUser['username'] not in dictFollowers:
            nonFollowers[followedUser['username']] = followedUser['pk']

    return nonFollowers

def getAllData():
    followers = getTotalFollowers()
    following = getTotalFollowing()
    nonFollow = nonFollowers(followers, following)
    i = len(nonFollow)
    print('Number of followers:', len(followers))
    with open("followers.txt","w", encoding="utf-8") as f:
        f.write(str(followers))

    time.sleep(3)
    print('Number of following:', len(following))
    with open("following.txt","w", encoding="utf-8") as f:
        f.write(str(following))

    time.sleep(3)
    print('Number of nonFollowers:', i)
    with open("nonFollowers.txt","w", encoding="utf-8") as f:
        f.write(str(nonFollow))

    time.sleep(3)

#call this only once to fetch data and store it
getAllData()

#For unfollowing non followers
i = 1
with open("nonFollowers.json","r", encoding="utf-8") as f:
    users : Dict = json.load(f)
    usernames = list(Dict.fromkeys(users))
    print(usernames)
with open("unfollwed.txt","a") as f:
    for user in usernames:
        # unfollow who don't follow you back
        bot.unfollow(username=user)
        f.writelines(str(user) + "\n")
        print(f"unfollowed: {i}")

        users.pop(user)
        f.flush()
        with open("nonFollowers.json","w", encoding="utf-8") as f2:
            json.dump(users,f2)
        #set limit for no of unfollows
        if(i==30):
            break
        i=i+1    
        time.sleep(3)

# get the following list (take a long time)
users_following = bot.get_following_list()

# get the followers list (take a long time)
users_followers = bot.get_followers_list()

for user in [u for u in users_following if u not in users_followers]:
    # unfollow who don't follow you back
    bot.unfollow(username=user)

# open explorer session, follow 10 new  users
# and save the posts in a collection with name
# yyyy-mm-dd. This way you can check the users
# followed by the app
bot.follow_n_save(amount=10)

users_following = bot.get_following_list()
if len(users_following):
    for u in users_following:
        # Unfollow who hasn't made a new post for the past 90 days
        if bot.get_days_lastpost(username=u) > 90:
            bot.unfollow(username=u)

# Open hashtag's feed 'creative',
# check if the hashtag is banned
# move to Recent tab and
# click in the first picture
if bot.open_tag(tag="creative", tab="Recent", check_banned=True):
    # swipe and like 5 pictures do feed opened before
    bot.like_n_swipe(5)

# open the profile "badgalriri"
if bot.open_profile(username="badgalriri", open_post=True):
    # swipe and like 3 pictures do feed opened before
    bot.like_n_swipe(3)

# open the post https://www.instagram.com/p/B_nrbNPndh0/
if bot.open_media(media_code="B_nrbNPndh0"):
    bot.like_n_swipe()

# open home feed and like 15 posts
if bot.open_home_feed():
    bot.like_n_swipe(15)

# return the last users who interacted with you
notification_users = bot.get_notification_users()
for u in notification_users:
    if bot.open_profile(username=u):
        bot.like_n_swipe(1)  # like the last post from users who interacted with you

# return the hashtags followed by you
followed_hashtags = bot.get_followed_hashtags()
for hashtag in followed_hashtags:
    if bot.open_tag(tag=hashtag, tab="Recent"):  # open the hashtag feed in the 'Recent' tab
        bot.like_n_swipe(amount=10)  # like 10 posts

# like accounts you've interacted with the least in the last 90 days
usernames = bot.get_least_interacted()
for u in usernames:
    if bot.open_profile(username=u, open_post=True):
        bot.like_n_swipe(3)
