
> Kevin Systrom, the creativity researcher Keith Sawyer explains, was a  
> fan of Kentucky whiskeys. So when he created a location-based iPhone  
> app—one driven by the success of networking app Foursquare—he named it  
> after the booze. The app was complicated, but it took Systrom just a  
> few months to build: Burbn let users check in at particular locations,  
> make plans for future check-ins, earn points for hanging out with  
> friends, and post pictures of the meet-ups.  
> [Instagram Was First Called 'Burbn'.](https://www.theatlantic.com/technology/archive/2014/07/instagram-used-to-be-called-brbn/373815/)  
  
# BurbnBot
BurbnBot is a bot for automated interaction in a famous social media app using an Android device or an Android Virtual Devices.  
## Requirements  
- Android 9.0  
- Python 3.6+  
- [Android platform tools](https://developer.android.com/studio/releases/platform-tools).

#### Tested with:
[Instagram release 173.0.0.39.120](https://www.apkmirror.com/apk/instagram/instagram-instagram/instagram-instagram-173-0-0-39-120-release/).

## Installation
1. Download and install [Android platform tools](https://developer.android.com/studio/releases/platform-tools).  
1. Clone the repo: 
	```bash 
	git clone https://github.com/harrypython/BurbnBot.git
	cd BurbnBot 
	```  
1. Install the requirements: 
	```bash 
	pip install -r requirements.txt
	```  

## Get started  
1. Connect an Android device with a USB cable or run an [Android Virtual Device](https://developer.android.com/studio/run/emulator).
1. Make sure you [enabled adb debugging](https://developer.android.com/studio/command-line/adb.html#Enabling) on your device(s).
1. You can test the device with the command:
	```bash 
	adb devices 
	```
    The output must be something like this
    ```bash
   List of devices attached
   AB12C3456789	device
   emulator-5554	device
   ```
1. You can copy the example.py or create your script
	```bash 
	python example.py -d emulator-5554
	```
## Usage  
  
```python  

from BurbnBot import Burbnbot

bot = Burbnbot()

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


```  
  
## Features
- Open home feed
- Login
- Open post
- Open location feed
- Open profile
- Open hashtag feed
- List followings
- List followers
- List followed hashtags
- Like and scroll an opened feed
- Follow user
- Unfollow user
- How long ago the user last posted
- Logout from other devices
  
## Contributing  
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.  
  
Please make sure to update tests as appropriate.  
  
## License  
  
[ GNU GPLv3 ](https://choosealicense.com/licenses/gpl-3.0/)  
  
## Buy me a coffee  
  
<a href="https://www.buymeacoffee.com/harrypython" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" style="height: 37px !important;" ></a>
