import argparse
import datetime
import random
import uiautomator2
from time import sleep


class MediaType(object):
    """Type of medias on Instagram"""
    PHOTO: int = 1  #: Photo media type
    VIDEO: int = 2  #: Video media type
    CAROUSEL: int = 8  #: A album with photos and/or videos


class Burbnbot:
    d: uiautomator2.Device
    version_app: str = "173.0.0.39.120"
    version_android: str = "9"
    month_list: list = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                        "October", "November", "December"]
    checkfor = [" hours ago", " hour ago", " days ago", " day ago", " minute ago", " minutes ago"]

    def __init__(self, device: str = None) -> None:
        """
        Args:
            device (str): Device serial number, use 'adb devices' to a list of
                connected devices
        """

        uiautomator2.logger = uiautomator2.setup_logger(
            "uiautomator2",
            logfile="log/{}.log".format(str(datetime.date.today())),
            level=uiautomator2.logging.DEBUG)

        if device is None:
            parser = argparse.ArgumentParser(add_help=True)
            parser.add_argument("-d", "--device", type=str, default=device, help="Device serial number", required=False)
            args = parser.parse_args()
            device_addr = args.device
        else:
            device_addr = device

        try:

            self.d = uiautomator2.connect(addr=device_addr)

            if len(self.d.app_list("com.instagram.android")) == 0:
                raise EnvironmentError("Instagram not installed.")

            self.d.app_stop_all()

            self.d.app_start(package_name="com.instagram.android")

            if not self.d.app_info(package_name="com.instagram.android")['versionName'] == self.version_app:
                uiautomator2.logger.info(
                    "You are using a different version than the recommended one, this can generate unexpected errors.")

            if self.d(resourceId="com.instagram.android:id/default_dialog_title").exists:
                ri = "com.instagram.android:id/default_dialog_title"
                if self.d(resourceId=ri).get_text() == "You've Been Logged Out":
                    self.d.app_clear(package_name="com.instagram.android")
                    raise EnvironmentError("You've Been Logged Out. Please log back in.")

            if self.d(resourceId="com.instagram.android:id/login_username").exists:
                self.d.app_clear(package_name="com.instagram.android")
                raise EnvironmentError("You've Been Logged Out. Please log back in.")

        except Exception as e:
            uiautomator2.logger.error(e)
            quit()

    def __reset_app(self, muted: bool = True):
        if not muted:
            uiautomator2.logger.info("Restarting app")
        self.d.app_stop_all()
        self.d.app_start(package_name="com.instagram.android")
        self.wait()

    def __treat_exception(self, e: Exception):
        self.d.screenshot("log/{}.jpg".format(datetime.datetime.now().strftime("%Y-%m-%d_-_%H_%M_%S-%f%z")))
        uiautomator2.logger.error(e)

    def wait(self, i: int = None):
        """Wait the device :param i: number of seconds to wait, if None will be
        a random number between 1 and 3 :type i: int

        Args:
            i (int): seconds to wait
        """
        if i is None:
            i = random.randint(1, 3)
        sleep(i)

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

    def __scroll_elem_vert(self, e: uiautomator2.UiObject):
        """take the last element informed in e and scroll to the first element
        :param e (u2.UiObject): Element informed

        Args:
            e (uiautomator2.UiObject):
        """
        if e.exists and e.count > 1:
            i = e.count
            fx = e[i - 1].info['visibleBounds']['right'] / 2
            fy = e[i - 1].info['visibleBounds']['top']
            # tx = e[0].info['visibleBounds']['left']
            tx = fx
            ty = e[0].info['visibleBounds']['bottom']
            if fy == ty:
                e.swipe("up")
            else:
                self.d.swipe(fx, fy, tx, ty, duration=0)

    def __scrool_elem_hori(self, e: uiautomator2.UiObject):
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
            self.d.swipe(fx, fy, tx, ty, duration=0)

    def __get_type_media(self) -> int:
        if self.d(resourceId="com.instagram.android:id/carousel_media_group").exists:
            return MediaType.CAROUSEL
        if self.d(resourceId="com.instagram.android:id/row_feed_photo_imageview").info['contentDescription']. \
                startswith("Video by "):
            return MediaType.VIDEO
        return MediaType.PHOTO

    def open_home_feed(self) -> bool:
        try:
            uiautomator2.logger.info("Opening home feed")
            self.__reset_app()
            self.d(resourceId='com.instagram.android:id/tab_icon', instance=0).click()
            self.d(resourceId='com.instagram.android:id/tab_icon', instance=0).click()
        except Exception as e:
            uiautomator2.logger.error(e)
            return False
        else:
            return True

    def get_users_liked_by_you(self, amount):
        self.d(resourceId="com.instagram.android:id/profile_tab").click()
        self.d(resourceId="com.instagram.android:id/profile_tab").click()
        self.d(description="Options").click()
        self.d(resourceId="com.instagram.android:id/menu_settings_row").click()
        self.d(resourceId="com.instagram.android:id/row_simple_text_textview", text="Account").click()
        self.d(resourceId="com.instagram.android:id/row_simple_text_textview", text="Posts You've Liked").click()
        u = []
        while not self.d(resourceId="com.instagram.android:id/media_set_row_content_identifier").exists:
            self.wait()
        while True:
            for c in [r.child(className="android.widget.ImageView") for r in
                      self.d(resourceId="com.instagram.android:id/media_set_row_content_identifier")]:
                for p in c:
                    p.click()
                    if self.d(resourceId="com.instagram.android:id/button", text="Follow").exists:
                        u.append(self.d(
                            resourceId="com.instagram.android:id/row_feed_photo_profile_name").get_text().split()[0])
                    self.d.press("back")
            self.__scroll_elem_vert(self.d(resourceId="com.instagram.android:id/media_set_row_content_identifier"))
            while self.d(resourceId="com.instagram.android:id/row_load_more_button").exists:
                self.d(resourceId="com.instagram.android:id/row_load_more_button").click()
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
            self.d.app_clear("com.instagram.android")
        self.d.app_start(package_name="com.instagram.android")
        if self.d(text="Log In").exists:
            self.d(text="Log In").click()
        if self.d(resourceId='com.instagram.android:id/login_username').exists and self.d(
                resourceId='com.instagram.android:id/password').exists:
            self.d(resourceId='com.instagram.android:id/login_username').send_keys(username)
            self.d(resourceId='com.instagram.android:id/password').send_keys(password)
            self.d(resourceId='com.instagram.android:id/button_text').click()
            self.wait()

    def open_media(self, media_code: str) -> bool:
        """Open a post by the code eg. in
        https://www.instagram.com/p/B_qh-EYnrjW/ the code is B_qh-EYnrjW

        Args:
            media_code (str): media code of the post

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        try:
            url = "https://www.instagram.com/p/{}/".format(media_code)
            uiautomator2.logger.info("Opening post {}.".format(url))
            self.d.shell("am start -a android.intent.action.VIEW -d {}".format(url))
            r = self.d.xpath("//*[@resource-id='android:id/list']//*[@class='android.widget.FrameLayout'][2]").exists
        except Exception as e:
            uiautomator2.logger.error(e)
            return False
        else:
            return r

    def open_location(self, locationcode: int, tab: str = "Top"):
        """Open a location

        Args:
            locationcode (int): locationcode
            tab (str): options are: Recent and Top

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        try:
            self.__reset_app()
            url = "https://www.instagram.com/explore/locations/{}/".format(locationcode)
            uiautomator2.logger.info("Opening location {}.".format(url))
            self.d.shell("am start -a android.intent.action.VIEW -d {}".format(url))
            self.wait(5)
            if tab is not None:
                while not self.d(text="{}".format(tab)).exists:
                    self.wait(1)
                self.d(text="{}".format(tab)).click()
            self.wait(5)
            self.d(resourceId='com.instagram.android:id/image_button').click()
        except Exception as e:
            uiautomator2.logger.error(e)
            return False
        else:
            return True

    def open_profile(self, username: str, open_post: bool = False) -> bool:
        """Open a profile

        Args:
            username (str): username you want to
            open_post (bool): if true open the first post

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        try:
            self.__reset_app()
            url = "https://www.instagram.com/{}/".format(username)
            uiautomator2.logger.info("Opening profile {}.".format(url))
            while not self.d(resourceId="com.instagram.android:id/action_bar_title", text=username).exists:
                self.d.shell("am start -a android.intent.action.VIEW -d {}".format(url))
                self.wait(2)

                if self.d(resourceId="com.instagram.android:id/no_found_text").exists:
                    raise EnvironmentError("{}: {}".format(username, self.d(resourceId="com.instagram.android:id/no_found_text").get_text()))

            row_profile_header_textview_post_count = "com.instagram.android:id/row_profile_header_textview_post_count"
            if open_post:
                if self.d(resourceId=row_profile_header_textview_post_count).get_text() == "0":
                    raise EnvironmentError("User {} has no posts yet.".format(username))
                else:
                    while not self.d(resourceId="com.instagram.android:id/row_feed_button_like").exists:
                        self.d(resourceId="com.instagram.android:id/media_set_row_content_identifier", instance=0) \
                            .child(className="android.widget.ImageView", instance=0).click()

            return True
        except Exception as e:
            uiautomator2.logger.info(e)
            return False

    def open_tag(self, tag: str, tab: str = "Recent", check_banned: bool = True) -> bool:
        """Search a hashtag

        Args:
            tag (str): hashtag
            tab (str): options are: Recent and Top
            check_banned (bool): check if is a banned hashtag

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        try:
            url = "https://www.instagram.com/explore/tags/{}/".format(tag)
            uiautomator2.logger.info("Opening hashtag: {}".format(tag))
            while not self.d(resourceId="com.instagram.android:id/action_bar_new_title_layout").exists:
                self.d.shell("am start -a android.intent.action.VIEW -d {}".format(url))
                self.wait(5)
            if self.d(resourceId="com.instagram.android:id/empty_state_headline_component").exists:
                raise EnvironmentError(self.d(resourceId="com.instagram.android:id/igds_headline_body").get_text())
            if self.d(resourceId="com.instagram.android:id/igds_headline_body").exists:
                raise EnvironmentError("#{} there is no posts.".format(tag))
            if self.d(resourceId="com.instagram.android:id/inform_body").exists and check_banned:
                raise EnvironmentError(self.d(resourceId="com.instagram.android:id/inform_body").get_text())

            self.d(text="{}".format(tab)).click()
            self.wait()

            if self.d.xpath("//*[@resource-id='com.instagram.android:id/hashtag_media_count']").exists:
                self.d(resourceId='com.instagram.android:id/image_button').click()

        except Exception as e:
            uiautomator2.logger.error(e)
            return False
        else:
            return True

    def get_least_interacted(self):
        lu = []
        i = 0
        last_username = ""
        self.__reset_app()
        try:
            uiautomator2.logger.info("Opening profiles less interacted.")
            while not self.d(resourceId="com.instagram.android:id/action_bar_textview_title",
                             text="Least Interacted With").exists:
                self.d(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
                self.d(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
                self.d(resourceId="com.instagram.android:id/row_profile_header_following_container").click(timeout=10)
                self.d(resourceId="com.instagram.android:id/title", text="Least Interacted With").click()
            self.wait(5)
            while i < 3:
                if self.d(resourceId="com.instagram.android:id/follow_list_username").exists:
                    for e in self.d(resourceId="com.instagram.android:id/follow_list_username"):
                        lu.append(e.get_text())
                    self.__scroll_elem_vert(self.d(resourceId="com.instagram.android:id/follow_list_container",
                                                   className="android.widget.LinearLayout"))

                if last_username == lu[-1]:
                    i += 1
                else:
                    last_username = lu[-1]

        except Exception as e:
            uiautomator2.logger.error(e)

        return list(dict.fromkeys(lu))

    def __double_click(self, e: uiautomator2.UiObject):
        """Double click center the element :param e: Element

        Args:
            e (uiautomator2.UiObject): Element
        """
        x, y = e.center()
        self.d.double_click(x, y, duration=0.1)

    def get_following_list(self) -> list:
        list_following = []
        try:
            self.__reset_app()
            self.d(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
            self.d(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
            uiautomator2.logger.info("Opening following list")
            following_count = self.__str_to_number(
                self.d(resourceId="com.instagram.android:id/row_profile_header_textview_following_count").get_text())
            uiautomator2.logger.info("{} followings".format(following_count))
            self.d(resourceId="com.instagram.android:id/row_profile_header_following_container").click(timeout=10)
            self.wait()
            while not self.d(resourceId="com.instagram.android:id/follow_list_sorting_option_radio_button").exists:
                self.d(resourceId="com.instagram.android:id/sorting_entry_row_icon").click()
                self.wait()
            self.d(resourceId="com.instagram.android:id/follow_list_sorting_option", text="Date Followed: Earliest").click(timeout=10)
            self.wait()
            if self.d(resourceId="com.instagram.android:id/follow_list_username").exists:
                rscid = "com.instagram.android:id/sorting_entry_row_option"
                fx = self.d(resourceId=rscid).info['visibleBounds']['right'] / 2
                fy = self.d(resourceId=rscid).info['visibleBounds']['top']
                tx = fx
                ty = self.d(resourceId="com.instagram.android:id/row_search_edit_text").info['visibleBounds']['bottom']
                self.d.swipe(fx, fy, tx, ty, duration=0)
                while True:

                    try:
                        if self.d(resourceId="com.instagram.android:id/follow_list_username").exists:
                            if self.d(resourceId="com.instagram.android:id/follow_list_username").count > 0:
                                for elem in self.d(resourceId="com.instagram.android:id/follow_list_username"):
                                    list_following.append(elem.get_text())
                    except uiautomator2.exceptions.UiObjectNotFoundError:
                        pass
                    self.__scroll_elem_vert(self.d(resourceId="com.instagram.android:id/follow_list_container"))

                    if self.d(text="Suggestions for you").exists:
                        list_following = list_following + [elem.get_text() for elem in self.d(resourceId="com.instagram.android:id/follow_list_username") if elem.exists]
                        break

            uiautomator2.logger.info("Done: amount of following: {}".format(len(list(dict.fromkeys(list_following)))))
        except Exception as e:
            self.__treat_exception(e)
        return list(dict.fromkeys(list_following))

    def get_followers_list(self) -> list:
        list_followers = []
        try:
            finisher_str = "Suggestions for you"
            self.__reset_app()
            self.d(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
            self.d(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
            uiautomator2.logger.info("Opening followers list")
            followers_count = self.__str_to_number(
                self.d(resourceId="com.instagram.android:id/row_profile_header_textview_followers_count").get_text())
            uiautomator2.logger.info("{} followers".format(followers_count))
            self.d(resourceId="com.instagram.android:id/row_profile_header_followers_container").click(timeout=10)
            self.wait()
            if self.d(resourceId="com.instagram.android:id/follow_list_username").exists:
                while True:
                    try:
                        if self.d(resourceId="com.instagram.android:id/follow_list_username").exists:
                            if self.d(resourceId="com.instagram.android:id/follow_list_username").count > 0:
                                for elem in self.d(resourceId="com.instagram.android:id/follow_list_username"):
                                    list_followers.append(elem.get_text())
                    except uiautomator2.exceptions.UiObjectNotFoundError:
                        pass

                    self.__scroll_elem_vert(self.d(resourceId="com.instagram.android:id/follow_list_container"))

                    if self.d(description="Retry").exists:
                        self.wait(10)
                        self.d(description="Retry").click()

                    if self.d(resourceId="com.instagram.android:id/row_header_textview").exists:
                        if self.d(resourceId="com.instagram.android:id/row_header_textview").get_text() == finisher_str:
                            break

                    uiautomator2.logger.info("Amount of followers: {}".format(len(list(dict.fromkeys(list_followers)))))
        except Exception as e:
            self.__treat_exception(e)

        uiautomator2.logger.info("Done: amount of following: {}".format(len(list(dict.fromkeys(list_followers)))))
        return list(dict.fromkeys(list_followers))

    def __click_n_wait(self, elem: uiautomator2.UiObject):
        if elem.exists:
            elem.click()
            sleep(random.randint(3, 5))

    def like_n_swipe(self, amount: int = 1):
        """
        Args:
            amount (int): number of posts to like
        """
        lk = 0
        subtit: str = "com.instagram.android:id/secondary_label"
        try:
            while lk < amount:
                try:
                    if self.d(resourceId="com.instagram.android:id/secondary_label", text="Sponsored").exists:
                        self.__skip_sponsored()
                    if self.d(resourceId="com.instagram.android:id/row_feed_button_like", description="Like").exists:
                        lk = lk + len([self.__click_n_wait(e) for e in self.d(resourceId="com.instagram.android:id/row_feed_button_like", description="Like")])
                        uiautomator2.logger.info("Liking {}/{}".format(lk, amount))
                    else:
                        self.d(resourceId="com.instagram.android:id/refreshable_container").swipe(direction="up")
                except uiautomator2.exceptions.UiObjectNotFoundError as e:
                    self.__not_found_like(e)
                    pass
        except Exception as e:
            self.__treat_exception(e)
            return None

        uiautomator2.logger.info("Done: Liked {}/{}".format(lk, amount))

    def __skip_sponsored(self):
        uiautomator2.logger.info("Skipping sponsored post")
        str_id = "com.instagram.android:id/secondary_label"
        fx = self.d(resourceId=str_id, text="Sponsored", instance=0).info['bounds']['left']
        fy = self.d(resourceId=str_id, text="Sponsored", instance=0).info['bounds']['bottom']
        tx = fx
        ty = 0
        self.d.swipe(fx, fy, tx, ty, duration=0)
        str_id = "com.instagram.android:id/row_feed_view_group_buttons"
        fx = self.d(resourceId=str_id, instance=0).info['bounds']['left']
        fy = self.d(resourceId=str_id, instance=0).info['bounds']['bottom']
        tx = fx
        self.d.swipe(fx, fy, tx, ty, duration=0)

    def __not_found_like(self, e: uiautomator2.UiObjectNotFoundError):
        if self.d(resourceId="com.instagram.android:id/default_dialog_title").exists:
            if self.d(resourceId="com.instagram.android:id/default_dialog_title").get_text() == "Try Again Later":
                uiautomator2.logger.critical("ERROR: TOO MANY REQUESTS, TAKE A BREAK HAMILTON.")
                self.d.app_clear(package_name="com.instagram.android")
                quit(1)
        uiautomator2.logger.warning("Element not found: {} You probably don't have to worry about.".format(e.data))
        uiautomator2.logger.error(e)

        # sometimes a wrong click open a different screen
        if (self.d(resourceId="com.instagram.android:id/profile_header_avatar_container_top_left_stub").exists or
            self.d(resourceId="com.instagram.android:id/pre_capture_buttons_top_container").exists) or \
                (not self.d(resourceId="com.instagram.android:id/refreshable_container").exists and
                 self.d(resourceId="com.instagram.android:id/action_bar_new_title_container").exists):
            uiautomator2.logger.warning("It looks like we're in the wrong place, let's try to get back.")
            self.d.press("back")

    def unfollow(self, username: str):
        """
        Args:
            username (str):
        """
        try:
            if self.open_profile(username=username):
                uiautomator2.logger.info("Unfollowing user: {}".format(username))
                self.d(className="android.widget.Button", text="Following").click()
                self.d(resourceId="com.instagram.android:id/follow_sheet_unfollow_row").click()
                if self.d(resourceId="com.instagram.android:id/dialog_body").exists:
                    self.d(resourceId="com.instagram.android:id/primary_button").click()
                return True
        except Exception as e:
            uiautomator2.logger.error(e)
            return False

    def follow(self, username: str):
        """
        Args:
            username (str):
        """
        try:
            if self.open_profile(username):
                self.d(className="android.widget.Button", text="Follow").click()
                if self.d(className="android.widget.Button", text="Requested").exists:
                    uiautomator2.logger.info(("Requested following user: {}".format(username)))
                else:
                    uiautomator2.logger.info("Following user: {}".format(username))
            return True
        except Exception as e:
            uiautomator2.logger.error(e)
            return False

    def save_user(self, username: str, colletion: str = None):
        """
        Args:
            username (str):
            colletion (str):
        """
        if colletion is None:
            colletion = str(datetime.date.today())
        if self.open_profile(username):
            if self.d(resourceId="com.instagram.android:id/profile_viewpager").child(
                    className="android.widget.ImageView").exists:
                self.d(resourceId="com.instagram.android:id/profile_viewpager").child(
                    className="android.widget.ImageView").click()
                self.wait()
                self.d(resourceId="com.instagram.android:id/row_feed_button_save").long_click(duration=3)
                if self.d(resourceId="com.instagram.android:id/collection_name").exists:
                    collections_name = [e.get_text() for e in
                                        self.d(resourceId="com.instagram.android:id/collection_name")]
                    lst = ""
                    while not lst == collections_name[-1]:
                        if self.d(text=colletion).exists:
                            self.d(text=colletion).click()
                            return True
                        collections_name = collections_name + [e.get_text() for e in self.d(
                            resourceId="com.instagram.android:id/collection_name")]
                        self.__scrool_elem_hori(
                            self.d(resourceId="com.instagram.android:id/selectable_image"))
                        lst = self.d(resourceId="com.instagram.android:id/collection_name")[-1].get_text()

                    self.d(resourceId='com.instagram.android:id/save_to_collection_new_collection_button').click()
                    self.wait()
                    self.d(resourceId='com.instagram.android:id/create_collection_edit_text').send_keys(colletion)
                    self.d(resourceId='com.instagram.android:id/save_to_collection_action_button').click()
                    return True
        return False

    def get_notification_users(self) -> list:
        """return the last users who interacted with you"""
        list_users = []
        try:
            self.d(resourceId="com.instagram.android:id/notification").click()
            self.d(resourceId="com.instagram.android:id/notification").click()
            while not self.d(text="Suggestions for you").exists:
                try:
                    list_users = list_users + [e.get_text().split()[0] for e in
                                               self.d(resourceId="com.instagram.android:id/row_text")]
                    self.__scrool_elem_hori(self.d(resourceId="com.instagram.android:id/row_text"))
                except Exception as e:
                    uiautomator2.logger.error("Error: {}.".format(e))
                    self.__treat_exception(e)
                    pass
        except Exception as e:
            uiautomator2.logger.error(e)
            return []
        else:
            return list(dict.fromkeys(list_users))

    def get_followed_hashtags(self) -> list:
        """return the hashtags followed by you"""
        try:
            self.__reset_app()
            fh = []
            self.d(resourceId="com.instagram.android:id/profile_tab").click()
            self.d(resourceId="com.instagram.android:id/profile_tab").click()
            self.d(resourceId="com.instagram.android:id/row_profile_header_following_container").click()
            self.d(resourceId="com.instagram.android:id/row_hashtag_image").click()
            self.wait()
            while not self.d(resourceId="com.instagram.android:id/row_header_textview", text="Suggestions").exists:
                fh = fh + [lst_btn.info.get("contentDescription").split()[1] for lst_btn in
                           self.d(resourceId="com.instagram.android:id/follow_button", text="Following")
                           if self.d(resourceId="com.instagram.android:id/follow_button", text="Following").exists]
                self.__scroll_elem_vert(self.d(resourceId="com.instagram.android:id/follow_list_user_imageview"))
                if not self.d(resourceId="com.instagram.android:id/action_bar_textview_title").get_text() == "Hashtags":
                    self.d.press("back")

            fh = fh + [lst_btn.info.get("contentDescription").split()[1] for lst_btn in
                       self.d(resourceId="com.instagram.android:id/follow_button", text="Following")
                       if self.d(resourceId="com.instagram.android:id/follow_button", text="Following").exists]

        except Exception as e:
            uiautomator2.logger.error(e)
            return []
        else:
            return list(dict.fromkeys(fh))

    def __is_date(self, textview: str):
        if textview.startswith(tuple(self.month_list)):
            return True

        for c in self.checkfor:
            if c in textview:
                return True

        return False

    def __count_days(self, textview: str):
        try:
            y = 0
            m = 0
            d = 0
            textview = textview.replace(" • See Translation", "")
            if textview.startswith(tuple(self.month_list)):
                d = textview.split(" ")[1].replace(",", "")
                m = str(int(self.month_list.index(textview.split(" ")[0])) + 1)
                if len(textview.split(" ")) == 2:
                    # not showing year
                    y = datetime.datetime.now().year
                else:
                    y = textview.split(" ")[2]

            for c in self.checkfor:
                if c in textview:
                    if "hour ago" in textview or \
                            "hours ago" in textview or \
                            "minutes ago" in textview or \
                            "minute ago" in textview:
                        return 0
                    if "day" in textview or "days ago" in textview:
                        d = (datetime.datetime.now() - datetime.timedelta(days=int(textview.split(" ")[0]))).day
                        m = (datetime.datetime.now() - datetime.timedelta(days=int(textview.split(" ")[0]))).month
                        y = (datetime.datetime.now() - datetime.timedelta(days=int(textview.split(" ")[0]))).year

            return (datetime.date.today() - datetime.date(int(y), int(m), int(d))).days
        except Exception as e:
            uiautomator2.logger.error(e)

    def get_days_lastpost(self, username):
        try:
            if self.open_profile(username=username, open_post=True):
                self.wait(5)
                self.d(resourceId="android:id/list",
                       className="androidx.recyclerview.widget.RecyclerView").swipe("up")
                for txt in self.d(resourceId="android:id/list",
                                  className="androidx.recyclerview.widget.RecyclerView"). \
                        child(className="android.widget.TextView"):
                    if self.__is_date(txt.get_text()):
                        uiautomator2.logger.info("{} last post: {}".format(username, txt.get_text()))
                        return self.__count_days(txt.get_text())
            else:
                return 0
        except Exception as e:
            uiautomator2.logger.error(e)

    def logout_other_devices(self):
        self.d(resourceId="com.instagram.android:id/profile_tab").click()
        self.d(resourceId="com.instagram.android:id/profile_tab").click()
        self.d(description="Options").click()
        self.wait()
        self.d(resourceId="com.instagram.android:id/menu_settings_row").click()
        self.wait()
        self.d(resourceId="com.instagram.android:id/row_simple_text_textview", text="Security").click()
        self.wait()
        self.d(resourceId="com.instagram.android:id/row_simple_text_textview", text="Login Activity").click()
        self.wait()
        str_xpath = '//*[@resource-id="android:id/list"]/android.widget.LinearLayout[2]/android.widget.ImageView[2]'
        while self.d.xpath(str_xpath).exists:
            self.d.xpath(str_xpath).click()
            self.d(text="Log Out").click()
            self.d(text="Okay").click()
            uiautomator2.logger.info(("Logout '{}, {}'".format(
                self.d(resourceId="com.instagram.android:id/body_message_device").get_text(),
                self.d(resourceId="com.instagram.android:id/title_message").get_text())))
            self.wait()
