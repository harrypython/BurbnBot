from BurbnBot import Burbnbot

bot = Burbnbot()

# get the following list (take a long time)
users_following = bot.get_following_list()

# get the followers list (take a long time)
users_followers = bot.get_followers_list()

for user in [u for u in users_following if u not in users_followers]:
    # unfollow who don't follow you back
    bot.unfollow(username=user)

# Open hashtag's feed 'creative',
# move to Recent tab and
# click in the first picture
bot.open_tag(tag="creative", tab="Recent")

# swipe and like 5 pictures do feed opened before
bot.like_n_swipe(5)

# open the profile "badgalriri"
bot.open_profile(username="badgalriri", open_post=True)
# swipe and like 3 pictures do feed opened before
bot.like_n_swipe(3)

# open the post https://www.instagram.com/p/B_nrbNPndh0/
bot.open_media(media_code="B_nrbNPndh0")
bot.like_n_swipe()

# open home feed and like 15 posts
bot.open_home_feed()
bot.like_n_swipe(15)

# return the last users who interacted with you
notification_users = bot.get_notification_users()
for u in notification_users:
    bot.like_n_swipe(1)  # like the last post from users who interacted with you
