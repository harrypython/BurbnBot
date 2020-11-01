import argparse
import random
import datetime
from time import sleep
from huepy import *
import sys
import uiautomator2


class MediaType(object):
    """Type of medias on Instagram"""
    PHOTO: int = 1  #: Photo media type
    VIDEO: int = 2  #: Video media type
    CAROUSEL: int = 8  #: A album with photos and/or videos


class Burbnbot:
    device: uiautomator2.Device
    version_app: str = "158.0.0.30.123"
    version_android: str = "9"

    def __init__(self, device: str = None) -> None:
        """
        Args:
            device (str): Device serial number, use 'adb devices' to a list of
                connected devices
        """
        parser = argparse.ArgumentParser(add_help=True)
        parser.add_argument("-d", "--device", type=str, default=device, help="Device serial number", required=False)
        args = parser.parse_args()

        self.device = uiautomator2.connect(addr=args.device)
        if len(self.device.app_list("com.instagram.android")) == 0:
            print(bad("Instagram not installed."))
            quit()

        self.device.app_stop_all()

        self.device.app_start(package_name="com.instagram.android")

        if not self.device.app_info(package_name="com.instagram.android")['versionName'] == self.version_app:
            print(info(
                "You are using a different version than the recommended one, this can generate unexpected errors."))

    def wait(self, i: int = None, muted=False):
        """Wait the device :param i: number of seconds to wait, if None will be
        a random number between 1 and 3 :type i: int

        Args:
            i (int): seconds to wait
        """
        if i is None:
            i = random.randint(1, 3)
        if muted:
            sleep(i)
        else:
            for remaining in range(i, 0, -1):
                print(run('Waiting for {} seconds.'.format(remaining)), end='\r', flush=True)
                sleep(1)
            sys.stdout.write("\033[K")  # Clear to the end of line

    def __reset_app(self):
        print(good("Restarting app"))
        self.device.app_stop_all()
        self.wait()
        self.device.app_start(package_name="com.instagram.android")
        self.wait()

    def __str_to_number(self, n: str):
        """format (string) numbers in thousands, million or billions :param n:
        string to convert :type n: str

        Args:
            n (str):
        """
        n = n.strip().replace(",", "")
        num_map = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        if n.isdigit():
            return n
        else:
            n = float(n[:-1]) * num_map.get(n[-1].upper(), 1)
        return int(n)

    def __scroll_elements_vertically(self, e: uiautomator2.UiObject):
        """take the last element informed in e and scroll to the first element
        :param e (u2.UiObject): Element informed

        Args:
            e (uiautomator2.UiObject):
        """
        if e.count > 2:
            fx = e[-1].info['visibleBounds']['right'] / 2
            fy = e[-1].info['visibleBounds']['top']
            # tx = e[0].info['visibleBounds']['left']
            tx = fx
            ty = e[0].info['visibleBounds']['bottom']
            self.device.swipe(fx, fy, tx, ty, duration=0)

    def __scrool_elements_horizontally(self, e: uiautomator2.UiObject):
        """take the last element informed in e and scroll to the first element
        :param e (u2.UiObject): Element informed

        Args:
            e (uiautomator2.UiObject):
        """
        if e.count > 2:
            fx = e[-1].info['visibleBounds']['left']
            fy = e[-1].info['visibleBounds']['top']
            tx = e[0].info['visibleBounds']['left']
            ty = e[0].info['visibleBounds']['bottom']
            self.device.swipe(fx, fy, tx, ty, duration=0)

    def __get_type_media(self) -> int:
        if self.device(resourceId="com.instagram.android:id/carousel_media_group").exists:
            return MediaType.CAROUSEL
        if self.device(resourceId="com.instagram.android:id/row_feed_photo_imageview").info['contentDescription']. \
                startswith("Video by "):
            return MediaType.VIDEO
        return MediaType.PHOTO

    def open_home_feed(self):
        print(good("Opening home feed"))
        self.__reset_app()
        self.device(resourceId='com.instagram.android:id/tab_icon', instance=0).click()
        self.device(resourceId='com.instagram.android:id/tab_icon', instance=0).click()

    def get_users_liked_by_you(self, amount):
        self.device(resourceId="com.instagram.android:id/profile_tab").click()
        self.device(resourceId="com.instagram.android:id/profile_tab").click()
        self.device(description="Options").click()
        self.device(resourceId="com.instagram.android:id/menu_settings_row").click()
        self.device(resourceId="com.instagram.android:id/row_simple_text_textview", text="Account").click()
        self.device(resourceId="com.instagram.android:id/row_simple_text_textview", text="Posts You've Liked").click()
        u = []
        while not self.device(resourceId="com.instagram.android:id/media_set_row_content_identifier").exists:
            self.wait()
        while True:
            for c in [r.child(className="android.widget.ImageView") for r in
                      self.device(resourceId="com.instagram.android:id/media_set_row_content_identifier")]:
                for p in c:
                    p.click()
                    if self.device(resourceId="com.instagram.android:id/button", text="Follow").exists:
                        u.append(self.device(
                            resourceId="com.instagram.android:id/row_feed_photo_profile_name").get_text().split()[0])
                    self.device.press("back")
            self.__scroll_elements_vertically(
                self.device(resourceId="com.instagram.android:id/media_set_row_content_identifier"))
            while self.device(resourceId="com.instagram.android:id/row_load_more_button").exists:
                self.device(resourceId="com.instagram.android:id/row_load_more_button").click()
                self.wait()
            u = list(dict.fromkeys(u))
            if len(u) > amount:
                break

        return u[:amount]

    def login(self, username: str, password: str, reset: bool = False):
        """
        Args:
            username (str):
            password (str):
            reset (bool):
        """
        if reset:
            self.device.app_clear("com.instagram.android")
        self.device.app_start(package_name="com.instagram.android")
        if self.device(text="Log In").exists:
            self.device(text="Log In").click()
        if self.device(resourceId='com.instagram.android:id/login_username').exists and self.device(
                resourceId='com.instagram.android:id/password').exists:
            self.device(resourceId='com.instagram.android:id/login_username').send_keys(username)
            self.device(resourceId='com.instagram.android:id/password').send_keys(password)
            self.device(resourceId='com.instagram.android:id/button_text').click()
            self.wait()

    def open_media(self, media_code: str) -> bool:
        """Open a post by the code eg. in
        https://www.instagram.com/p/CFr6-Q-sAFi/ the code is CFr6-Q-sAFi

        Args:
            media_code (str): media code of the post

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        url = "https://www.instagram.com/p/{}/".format(media_code)
        print(good("Opening post {}.".format(url)))
        self.device.shell("am start -a android.intent.action.VIEW -d {}".format(url))
        return self.device.xpath(
            "//*[@resource-id='android:id/list']//*[@class='android.widget.FrameLayout'][2]").exists

    def open_location(self, locationcode: int, tab: str = "Top"):
        """Open a location

        Args:
            locationcode (int): locationcode
            tab (str): options are: Recent and Top

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        print(good("Opening location code: {}.".format(locationcode)))
        self.__reset_app()
        url = "https://www.instagram.com/explore/locations/{}/".format(locationcode)
        print(good("Opening location {}.".format(url)))
        self.device.shell("am start -a android.intent.action.VIEW -d {}".format(url))
        self.wait(5)
        if tab is not None:
            while not self.device(resourceId="com.instagram.android:id/tab_layout").child_by_text(tab).exists:
                self.wait(1)
            self.device(resourceId="com.instagram.android:id/tab_layout").child_by_text(tab).click()
        self.wait(5)
        self.device(resourceId='com.instagram.android:id/image_button').click()

    def open_profile(self, username: str, open_post: bool = False) -> bool:
        """Open a profile

        Args:
            username (str): username you want to
            open_post (bool): if true open the first post

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        url = "https://www.instagram.com/{}/".format(username)
        print(good("Opening profile {}.".format(url)))
        self.device.shell("am start -a android.intent.action.VIEW -d {}".format(url))
        self.wait()
        r = self.device(resourceId='com.instagram.android:id/row_profile_header_imageview').exists
        if open_post:
            if self.device(resourceId="com.instagram.android:id/profile_viewpager").child(
                    className="android.widget.ImageView").exists:
                self.device(resourceId="com.instagram.android:id/profile_viewpager").child(
                    className="android.widget.ImageView").click()
            else:
                print(bad("Looks like this profile have zero posts."))
                return False
        return r

    def open_tag(self, tag: str, tab: str = "Recent"):
        """Search a hashtag

        Args:
            tag (str): hashtag
            tab (str): options are: Recent and Top

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        print(good("Opening hashtag: "), green(tag))
        self.__reset_app()
        while not self.device(resourceId="com.instagram.android:id/action_bar_textview_title").exists:
            url = "https://www.instagram.com/explore/tags/{}/".format(tag)
            self.device.shell("am start -a android.intent.action.VIEW -d {}".format(url))

        self.wait(5)
        if tab is not None:
            while not self.device(resourceId="com.instagram.android:id/tab_layout").child_by_text(tab).exists:
                self.wait(1)
            self.device(resourceId="com.instagram.android:id/tab_layout").child_by_text(tab).click()

        if self.device.xpath("//*[@resource-id='com.instagram.android:id/hashtag_media_count']").exists:
            self.device(resourceId='com.instagram.android:id/image_button').click()

    def __double_click(self, e: uiautomator2.UiObject):
        """Double click center the element :param e: Element

        Args:
            e (uiautomator2.UiObject): Element
        """
        x, y = e.center()
        self.device.double_click(x, y, duration=0.1)

    def get_following_list(self):
        list_following = []
        self.__reset_app()
        self.device(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
        self.device(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
        print(good("Opening following list"))
        following_count = self.__str_to_number(
            self.device(resourceId="com.instagram.android:id/row_profile_header_textview_following_count").get_text())
        print(good("{} followings".format(following_count)))
        self.device(resourceId="com.instagram.android:id/row_profile_header_following_container").click(timeout=10)
        self.wait()
        while not self.device(resourceId="com.instagram.android:id/follow_list_sorting_option_radio_button").exists:
            self.device(resourceId="com.instagram.android:id/sorting_entry_row_icon").click()
            self.wait()
        self.device(resourceId="com.instagram.android:id/follow_list_sorting_option_radio_button")[2].click(timeout=10)
        self.wait()
        if self.device(resourceId="com.instagram.android:id/follow_list_username").exists:
            while True:
                try:
                    list_following = list_following + [elem.get_text() for elem in self.device(
                        resourceId="com.instagram.android:id/follow_list_username") if elem.exists]
                    if not self.device(text="Suggestions for you").exists:
                        self.__scroll_elements_vertically(
                            self.device(resourceId="com.instagram.android:id/follow_list_container")
                        )
                        self.wait(random.randint(15, 60))
                    else:
                        break
                except:
                    pass
                print(run("Following: #{}".format(len(list(dict.fromkeys(list_following))))), end="\r", flush=True)
            print(good("Done"), "\r")
        return list(dict.fromkeys(list_following))

    def get_followers_list(self):
        self.__reset_app()
        list_following = []
        self.device(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
        self.device(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
        print(good("Opening followers list"))
        followers_count = self.__str_to_number(
            self.device(resourceId="com.instagram.android:id/row_profile_header_textview_followers_count").get_text())
        print(good("{} followers".format(followers_count)))
        self.device(resourceId="com.instagram.android:id/row_profile_header_followers_container").click(timeout=10)
        self.wait()
        if self.device(resourceId="com.instagram.android:id/follow_list_username").exists:
            t = 0
            while t < 5:
                try:
                    list_following = list_following + [elem.get_text() for elem in self.device(
                        resourceId="com.instagram.android:id/follow_list_username") if elem.exists]
                    self.__scroll_elements_vertically(
                        self.device(resourceId="com.instagram.android:id/follow_list_container"))
                    self.wait(random.randint(15, 60))
                    if list_following[-1] == self.device(
                            resourceId="com.instagram.android:id/follow_list_username").get_text():
                        t += 1
                    else:
                        t = 0
                    self.device(resourceId="com.instagram.android:id/row_load_more_button").click_exists(timeout=2)
                except:
                    pass

                print(run("Followers #: {}".format(len(list(dict.fromkeys(list_following))))), end="\r", flush=True)
            print(good("Done"), "\r")
        return list(dict.fromkeys(list_following))

    def __click_n_wait(self, elem: uiautomator2.UiObject, t: int = 0):
        if elem.exists:
            elem.click()
            self.wait(random.randint(5, 10), muted=True)

    def like_n_swipe(self, amount: int = 1):
        """
        Args:
            amount (int):
            :param amount:
            :type amount:
            :param wait:
            :type wait:
        """
        lk = 0
        while lk < amount:
            self.wait(muted=True)
            self.device.dump_hierarchy()
            try:
                if self.device(description="Like", className="android.widget.ImageView").exists:
                    lk = lk + len([self.__click_n_wait(e) for e in
                                   self.device(description="Like", className="android.widget.ImageView")])
                    print(run("Liking: {}/{}".format(lk, amount)), end="\r", flush=True)
                else:
                    self.device(resourceId="com.instagram.android:id/refreshable_container").swipe(direction="up",
                                                                                                   steps=15)
            except Exception as e:
                print(bad(e))
                pass
            self.device.dump_hierarchy()

        sys.stdout.write("\033[K")  # Clear to the end of line
        print(good("Liked: {}/{}".format(lk, amount)))
        print(good("End of likes."))

    def unfollow(self, username: str):
        """
        Args:
            username (str):
        """
        print(good("Unfollowing user: {}".format(username)))
        self.device(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
        self.device(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
        self.device(resourceId="com.instagram.android:id/row_profile_header_following_container").click(timeout=10)
        self.wait()
        self.device(resourceId="com.instagram.android:id/row_search_edit_text").send_keys(username)
        self.wait()
        if self.device(resourceId="com.instagram.android:id/button").count == 1:
            if self.device(resourceId="com.instagram.android:id/button").get_text() == 'Following':
                self.device(resourceId="com.instagram.android:id/button").click(timeout=5)
        else:
            return False
        return self.device(resourceId="com.instagram.android:id/button").get_text() == 'Follow'

    def follow(self, username: str):
        """
        Args:
            username (str):
        """
        if self.open_profile(username):
            if self.device(resourceId="com.instagram.android:id/button").get_text() == "Follow":
                print(good("Following user: {}".format(username)))
                self.device(resourceId="com.instagram.android:id/button").click()
        return self.device(resourceId="com.instagram.android:id/button").get_text() == "Following"

    def save_user(self, username: str, colletion: str = None):
        """
        Args:
            username (str):
            colletion (str):
        """
        if colletion is None:
            colletion = str(datetime.date.today())
        if self.open_profile(username):
            if self.device(resourceId="com.instagram.android:id/profile_viewpager").child(
                    className="android.widget.ImageView").exists:
                self.device(resourceId="com.instagram.android:id/profile_viewpager").child(
                    className="android.widget.ImageView").click()
                self.wait()
                self.device(resourceId="com.instagram.android:id/row_feed_button_save").long_click(duration=3)
                if self.device(resourceId="com.instagram.android:id/collection_name").exists:
                    collections_name = [e.get_text() for e in
                                        self.device(resourceId="com.instagram.android:id/collection_name")]
                    lst = ""
                    while not lst == collections_name[-1]:
                        if self.device(text=colletion).exists:
                            self.device(text=colletion).click()
                            return True
                        collections_name = collections_name + [e.get_text() for e in self.device(
                            resourceId="com.instagram.android:id/collection_name")]
                        self.__scrool_elements_horizontally(
                            self.device(resourceId="com.instagram.android:id/selectable_image"))
                        lst = self.device(resourceId="com.instagram.android:id/collection_name")[-1].get_text()

                    self.device(resourceId='com.instagram.android:id/save_to_collection_new_collection_button').click()
                    self.wait()
                    self.device(resourceId='com.instagram.android:id/create_collection_edit_text').send_keys(colletion)
                    self.device(resourceId='com.instagram.android:id/save_to_collection_action_button').click()
                    return True
        return False

    def get_notification_users(self) -> list:
        """return the last users who interacted with you"""
        list_users = []
        self.device(resourceId="com.instagram.android:id/notification").click()
        self.device(resourceId="com.instagram.android:id/notification").click()
        while not self.device(text="Suggestions for you").exists:
            try:
                list_users = list_users + [e.get_text().split()[0] for e in
                                           self.device(resourceId="com.instagram.android:id/row_text")]
                self.__scrool_elements_horizontally(self.device(resourceId="com.instagram.android:id/row_text"))
            except:
                pass
        return list(dict.fromkeys(list_users))

    def get_followed_hashtags(self) -> list:
        """return the hashtags followed by you"""
        fh = []
        self.device(resourceId="com.instagram.android:id/profile_tab").click()
        self.device(resourceId="com.instagram.android:id/profile_tab").click()
        self.device(resourceId="com.instagram.android:id/row_profile_header_following_container").click()
        self.device(resourceId="com.instagram.android:id/row_hashtag_image").click()
        self.wait()
        while True:
            fh = fh + [l.info.get("contentDescription").split()[1] for l in
                       self.device(resourceId="com.instagram.android:id/follow_button", text="Following")]
            self.__scroll_elements_vertically(
                self.device(resourceId="com.instagram.android:id/follow_list_user_imageview"))
            if self.device(resourceId="com.instagram.android:id/row_header_textview", text="Suggestions").exists:
                fh = fh + [l.info.get("contentDescription").split()[1] for l in
                           self.device(resourceId="com.instagram.android:id/follow_button", text="Following")]
                break
        return list(dict.fromkeys(fh))

    def logout_other_devices(self):
        self.device(resourceId="com.instagram.android:id/profile_tab").click()
        self.device(resourceId="com.instagram.android:id/profile_tab").click()
        self.device(description="Options").click()
        self.wait()
        self.device(resourceId="com.instagram.android:id/menu_settings_row").click()
        self.wait()
        self.device(resourceId="com.instagram.android:id/row_simple_text_textview", text="Security").click()
        self.wait()
        self.device(resourceId="com.instagram.android:id/row_simple_text_textview", text="Login Activity").click()
        self.wait()
        str_xpath = '//*[@resource-id="android:id/list"]/android.widget.LinearLayout[2]/android.widget.ImageView[2]'
        while self.device.xpath(str_xpath).exists:
            self.device.xpath(str_xpath).click()
            self.device(text="Log Out").click()
            self.device(text="Okay").click()
            print(
                good("Logout '{}, {}'".format(
                    self.device(resourceId="com.instagram.android:id/body_message_device").get_text(),
                    self.device(resourceId="com.instagram.android:id/title_message").get_text())
                )
            )
            self.wait()
            self.device.dump_hierarchy()
