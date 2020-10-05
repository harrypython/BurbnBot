import argparse
import random
import re
import datetime
import sys
from time import sleep
from .ElementXpath import elxpath
from loguru import logger
import uiautomator2 as u2


class UserNotFound(Exception):
    pass


class MediaType(object):
    PHOTO = 1
    VIDEO = 2
    CAROUSEL = 8


class Burbnbot:
    session = None
    appium_env = {}
    logPath: str = "log/"
    logger: logger = logger
    version_app: str = "158.0.0.30.123"
    version_android: str = "9"

    def __init__(self, device: str = None) -> None:

        parser = argparse.ArgumentParser(add_help=True)
        parser.add_argument("-d", "--device", type=str, default=None, help="Device serial number", required=False)
        args = parser.parse_args()

        device = u2.connect(addr=args.device)
        self.session = device.session(package_name="com.instagram.android")
        self.session.app_stop_all()
        self.session.app_start(package_name="com.instagram.android")
        self.session.xpath(elxpath.tab_bar_profile).click()

        self.user = self.session.xpath("//*[@resource-id='com.instagram.android:id/title_view']").info['text']

        self.logger.add("log/{}-{}.log".format(datetime.date.today(), self.user),
                        backtrace=True, diagnose=True, level="DEBUG")

        if not self.session.app_info(package_name="com.instagram.android")['versionName'] == self.version_app:
            self.logger.warning("You are using a different version than the recommended one, "
                                "this can generate unexpected errors.")

    def __wait(self, i: int = None):
        if i is None:
            i = random.randint(1, 3)
        # self.logger.info("Waiting {} seconds".format(i))
        sleep(i)

    def __reset_app(self):
        self.session.app_stop_all()
        self.__wait()
        self.session.app_start(package_name="com.instagram.android")
        self.__wait()

    def __treat_exception(self, err):
        self.logger.exception(err)
        pass
        self.__reset_app()
        return False

    def __scroll_down(self):
        e = "com.instagram.android:id/refreshable_container"
        startX = int(self.session(resourceId=e).info['visibleBounds']['right']/2)
        startY = int(self.session(resourceId=e).info['visibleBounds']['bottom']*0.90)
        endX = startX
        endY = int(self.session(resourceId=e).info['visibleBounds']['top'])
        self.session.swipe(fx=startX, fy=startY, tx=endX, ty=endY)

    def __scroll_element_by_element(self, e):
        if e.count > 2:
            fx = e[-1].info['visibleBounds']['right']/2
            fy = e[-1].info['visibleBounds']['top']
            # tx = e[0].info['visibleBounds']['left']
            tx = fx
            ty = e[0].info['visibleBounds']['bottom']
            self.session.swipe(fx, fy, tx, ty, duration=0)

    def __get_type_media(self) -> int:
        if self.session(resourceId="com.instagram.android:id/carousel_media_group").exists:
            return MediaType.CAROUSEL
        if self.session(resourceId="com.instagram.android:id/row_feed_photo_imageview").info['contentDescription'].\
                startswith("Video by "):
            return MediaType.VIDEO
        return MediaType.PHOTO

    def open_media(self, media_code: str) -> bool:
        url = "https://www.instagram.com/p/{}/".format(media_code)
        self.logger.info("Opening post {}.".format(url))
        self.session.shell("am start -a android.intent.action.VIEW -d {}".format(url))
        return self.session.xpath(elxpath.post_media_area).exists

    def open_profile(self, username: str) -> bool:
        url = "https://www.instagram.com/{}/".format(username)
        self.session.shell("am start -a android.intent.action.VIEW -d {}".format(url))
        return self.session.xpath(elxpath.row_profile_header_imageview).exists

    def open_tag(self, tag: str, aba: str = "Recent") -> bool:
        url = "https://www.instagram.com/explore/tags/{}/".format(tag)
        self.session.shell("am start -a android.intent.action.VIEW -d {}".format(url))
        self.__wait(5)
        if aba is not None:
            while not self.session(resourceId="com.instagram.android:id/tab_layout").child_by_text(aba).exists:
                self.__wait(1)
            self.session(resourceId="com.instagram.android:id/tab_layout").child_by_text(aba).click()

        return self.session.xpath("//*[@resource-id='com.instagram.android:id/hashtag_media_count']").exists

    def __center(self, element: None = ""):
        lx, ly, rx, ry = element.bounds()
        width, height = rx - lx, ry - ly
        x = lx + width * 0.5
        y = ly + height * 0.5
        return x, y

    def __double_click(self, e):
        x, y = self.__center(element=e)
        self.session.double_click(x, y, duration=0.1)

    def __like(self):
        row_feed_button_like = "com.instagram.android:id/row_feed_button_like"
        media_type = self.__get_type_media()
        while self.session(resourceId=row_feed_button_like, instance=0).info["contentDescription"] == 'Like':
            if media_type == MediaType.VIDEO:
                self.session(resourceId=row_feed_button_like, instance=0).click()
            else:
                if media_type == MediaType.CAROUSEL:
                    self.__swipe_carousel()

            self.__double_click(e=self.session(resourceId="android:id/list").child(className="android.widget.FrameLayout"))

            if self.session(resourceId=row_feed_button_like, instance=0).info["contentDescription"] == 'Like':
                self.session(resourceId=row_feed_button_like, instance=0).click()

        self.__wait()
        return self.session(resourceId=row_feed_button_like, instance=0).info["contentDescription"] == 'Liked'

    def like(self):
        return self.__like()

    def __swipe_carousel(self) -> None:
        try:
            n = int(re.search(r"(\d+).*?(\d+)",
                              self.session(resourceId="com.instagram.android:id/carousel_image")[0]
                              .info['contentDescription']).group(2))
        except Exception:
            n = 2  # if don't find the number of pictures work with only 2
            pass

        for x in range(n - 1):
            self.session(resourceId="com.instagram.android:id/carousel_image")[0].swipe("left")
            self.__wait()
        for x in range(n - 1):
            self.session(resourceId="com.instagram.android:id/carousel_image")[0].swipe("right")
            self.__wait()

    def get_following_list(self):
        list_following = []
        self.session(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
        self.session(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
        self.session(resourceId="com.instagram.android:id/row_profile_header_following_container").click(timeout=10)
        self.__wait()
        while not self.session(resourceId="com.instagram.android:id/follow_list_sorting_option_radio_button").exists:
            self.session(resourceId="com.instagram.android:id/sorting_entry_row_icon").click()
            self.__wait()
        self.session(resourceId="com.instagram.android:id/follow_list_sorting_option_radio_button")[2].click(timeout=10)
        self.__wait()
        t = 0
        while t < 3 and self.session(resourceId="com.instagram.android:id/follow_list_username").exists:
            list_following = list_following + [elem.get_text(timeout=50) for elem in self.session(resourceId="com.instagram.android:id/follow_list_username") if elem.exists]

            self.__scroll_element_by_element(self.session(resourceId="com.instagram.android:id/follow_list_container"))

            if list_following[-1] == self.session(resourceId="com.instagram.android:id/follow_list_username").get_text(timeout=50):
                t += 1
            else:
                t = 0
            self.session(resourceId="com.instagram.android:id/row_load_more_button").click_exists(timeout=2)
        list_following = list(dict.fromkeys(list_following))
        return list_following

    def get_followers_list(self):
        list_following = []
        self.session(resourceId="com.instagram.android:id/profile_tab").click(timeout=10)
        self.session(resourceId="com.instagram.android:id/profile_tab").click(timeout=5)
        self.session(resourceId="com.instagram.android:id/row_profile_header_followers_container").click(timeout=10)
        self.__wait()
        t = 0
        while t < 3 and self.session(resourceId="com.instagram.android:id/follow_list_username").exists:
            list_following = list_following + [elem.get_text(timeout=50) for elem in self.session(resourceId="com.instagram.android:id/follow_list_username") if elem.exists]

            self.__scroll_element_by_element(self.session(resourceId="com.instagram.android:id/follow_list_container"))

            if list_following[-1] == self.session(resourceId="com.instagram.android:id/follow_list_username").get_text(timeout=50):
                t += 1
            else:
                t = 0
            self.session(resourceId="com.instagram.android:id/row_load_more_button").click_exists(timeout=2)
        list_following = list(dict.fromkeys(list_following))
        return list_following










