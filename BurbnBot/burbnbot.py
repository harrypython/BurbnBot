import argparse
import random
import datetime
from time import sleep
from loguru import logger
from huepy import *
import uiautomator2 as u2


class MediaType(object):
    """Type of medias on Instagram"""
    PHOTO: int = 1  #: Photo media type
    VIDEO: int = 2  #: Video media type
    CAROUSEL: int = 8  #: A album with photos and/or videos


class Burbnbot:
    device: u2.Device
    logPath: str = "log/"
    logger: logger = logger  #: Logger
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

        self.device = u2.connect(addr=args.device)
        if len(self.device.app_list("com.instagram.android")) == 0:
            print(bad("Instagram not installed."))
            quit()

        self.device.app_stop_all()
        self.device.app_start(package_name="com.instagram.android")
        self.device(resourceId='com.instagram.android:id/profile_tab').click()

        self.user = self.device.xpath("//*[@resource-id='com.instagram.android:id/title_view']").info['text']
        self.logger.add("log/{}-{}.log".format(datetime.date.today(), self.user),
                        backtrace=True, diagnose=True, level="DEBUG")

        if not self.device.app_info(package_name="com.instagram.android")['versionName'] == self.version_app:
            print(info(
                "You are using a different version than the recommended one, this can generate unexpected errors."))

    def __printcount(self, msg: str, i: int):
        print(good(msg + ' [%d]\r' % i), end="")

    def __wait(self, i: int = None):
        """Wait the device :param i: number of seconds to wait, if None will be
        a random number between 1 and 3 :type i: int

        Args:
            i (int): seconds to wait
        """
        if i is None:
            i = random.randint(1, 3)
        sleep(i)

    def __reset_app(self):
        print(good("Restarting app"))
        self.device.app_stop_all()
        self.__wait()
        self.device.app_start(package_name="com.instagram.android")
        self.__wait()

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

    def __scroll_elements_vertically(self, e: u2.UiObject):
        """take the last element informed in e and scroll to the first element
        :param e (u2.UiObject): Element informed

        Args:
            e:
        """
        if e.count > 2:
            fx = e[-1].info['visibleBounds']['right'] / 2
            fy = e[-1].info['visibleBounds']['top']
            # tx = e[0].info['visibleBounds']['left']
            tx = fx
            ty = e[0].info['visibleBounds']['bottom']
            self.device.swipe(fx, fy, tx, ty, duration=0)

    def __scrool_elements_horizontally(self, e: u2.UiObject):
        """take the last element informed in e and scroll to the first element
        :param e (u2.UiObject): Element informed

        Args:
            e:
        """
        if e.count > 2:
            fx = e[-1].info['visibleBounds']['right'] / 2
            fy = e[-1].info['visibleBounds']['top']
            tx = e[0].info['visibleBounds']['left'] / 2
            ty = e[0].info['visibleBounds']['bottom']
            self.device.swipe(fx, fy, tx, ty, duration=0)

    def __get_type_media(self) -> int:
        if self.device(resourceId="com.instagram.android:id/carousel_media_group").exists:
            return MediaType.CAROUSEL
        if self.device(resourceId="com.instagram.android:id/row_feed_photo_imageview").info['contentDescription']. \
                startswith("Video by "):
            return MediaType.VIDEO
        return MediaType.PHOTO

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
        self.__wait()
        r = self.device(resourceId='com.instagram.android:id/row_profile_header_imageview').exists
        if open_post:
            if self.device(resourceId="com.instagram.android:id/profile_viewpager").child(
                    className="android.widget.ImageView").exists:
                self.device(resourceId="com.instagram.android:id/profile_viewpager").child(
                    className="android.widget.ImageView").click()
            else:
                print(bad("Looks like this profile have zero posts."))
        return r

    def open_tag(self, tag: str, tab: str = "Recent") -> bool:
        """Search a hashtag

        Args:
            tag (str): hashtag
            tab (str): options are: Recent and Top

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        url = "https://www.instagram.com/explore/tags/{}/".format(tag)
        self.device.shell("am start -a android.intent.action.VIEW -d {}".format(url))
        print(good("Opening hashtag: "), green(tag))
        self.__wait(5)
        if tab is not None:
            while not self.device(resourceId="com.instagram.android:id/tab_layout").child_by_text(tab).exists:
                self.__wait(1)
            self.device(resourceId="com.instagram.android:id/tab_layout").child_by_text(tab).click()

        if self.device.xpath("//*[@resource-id='com.instagram.android:id/hashtag_media_count']").exists:
            self.device(resourceId='com.instagram.android:id/image_button').click()

    def __center(self, element: u2.UiObject):
        """Find the center of an element

        Args:
            element (u2.UiObject): Element

        Returns:
            int, int
        """
        lx, ly, rx, ry = element.bounds()
        width, height = rx - lx, ry - ly
        x = lx + width * 0.5
        y = ly + height * 0.5
        return x, y

    def __double_click(self, e: u2.UiObject):
        """Double click center the element :param e: Element

        Args:
            e: (u2.UiObject): Element
        """
        x, y = self.__center(element=e)
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
        self.__wait()
        while not self.device(resourceId="com.instagram.android:id/follow_list_sorting_option_radio_button").exists:
            self.device(resourceId="com.instagram.android:id/sorting_entry_row_icon").click()
            self.__wait()
        self.device(resourceId="com.instagram.android:id/follow_list_sorting_option_radio_button")[2].click(timeout=10)
        self.__wait()
        if self.device(resourceId="com.instagram.android:id/follow_list_username").exists:
            while True:
                try:
                    list_following = list_following + [elem.get_text() for elem in self.device(
                        resourceId="com.instagram.android:id/follow_list_username") if elem.exists]
                    if not self.device(text="Suggestions for you").exists:
                        self.__scroll_elements_vertically(
                            self.device(resourceId="com.instagram.android:id/follow_list_container")
                        )
                    else:
                        break
                except:
                    pass
                self.__printcount(msg="Following: ", i=len(list(dict.fromkeys(list_following))))
            print(info("Done"), "\r")
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
        self.__wait()
        if self.device(resourceId="com.instagram.android:id/follow_list_username").exists:
            t = 0
            while t < 5:
                try:
                    list_following = list_following + [elem.get_text() for elem in self.device(
                        resourceId="com.instagram.android:id/follow_list_username") if elem.exists]
                    self.__scroll_elements_vertically(
                        self.device(resourceId="com.instagram.android:id/follow_list_container"))
                    if list_following[-1] == self.device(
                            resourceId="com.instagram.android:id/follow_list_username").get_text():
                        t += 1
                    else:
                        t = 0
                    self.device(resourceId="com.instagram.android:id/row_load_more_button").click_exists(timeout=2)
                except:
                    pass
                self.__printcount(msg="Following: ", i=len(list(dict.fromkeys(list_following))))
            print(info("Done"), "\r")
        return list(dict.fromkeys(list_following))

    def like_n_swipe(self, amount: int = 1):
        """
        Args:
            amount (int):
        """
        lk = 0
        while lk < amount:
            self.__wait()
            try:
                if self.device(description="Like", className="android.widget.ImageView").exists:
                    lk = lk + len(
                        [e.click() for e in self.device(description="Like", className="android.widget.ImageView")])
                else:
                    self.device(resourceId="com.instagram.android:id/refreshable_container").swipe(direction="up")
            except:
                pass
            self.__printcount(msg="Liked: ", i=lk)
        print(info("End of likes."))

    def unfollow(self, username: str):
        """
        Args:
            username (str):
        """
        self.device(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
        self.device(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
        self.device(resourceId="com.instagram.android:id/row_profile_header_following_container").click(timeout=10)
        self.__wait()
        self.device(resourceId="com.instagram.android:id/row_search_edit_text").send_keys(username)
        self.__wait()
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
                self.device(resourceId="com.instagram.android:id/button").click()
        return self.device(resourceId="com.instagram.android:id/button").get_text() == "Following"


