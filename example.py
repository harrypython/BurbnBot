from BurbnBot import Burbnbot

bot = Burbnbot()

# get the following list (take a long time)
users_following = bot.get_following_list()

# get the followers list (take a long time)
users_followers = bot.get_followers_list()

for user in [u for u in users_following if u not in users_followers]:
    # unfollow who don't follow you back
    bot.unfollow(username=user)


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
