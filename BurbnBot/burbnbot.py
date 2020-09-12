import random
import re
import datetime
from time import sleep
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.appium_service import AppiumService
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from .ElementXpath import elxpath
from os.path import expanduser
from loguru import logger


class UserNotFound(Exception):
    pass


class MediaType(object):
    PHOTO = 1
    VIDEO = 2
    CAROUSEL = 8


class Burbnbot:
    service = AppiumService()
    driver: webdriver = None
    appium_env = {}
    logPath: str = "log/"
    logger: logger = logger

    def __init__(self, username: str, password: str, avd_name: str = None,
                 android_home: str = "~/Library/Android/sdk/",
                 java_home: str = "/Library/Java/JavaVirtualMachines/adoptopenjdk-14.jdk/Contents/Home",
                 node: str = "/usr/local/bin/node") -> None:
        self.logger.remove()
        self.logger.add("log/{}-{}.log".format(datetime.date.today(), username), backtrace=True, diagnose=True,
                        level="DEBUG")

        self.node_path = expanduser(node)
        self.appium_env = {"ANDROID_HOME": expanduser(android_home), "JAVA_HOME": expanduser(java_home)}

        self.username = username
        self.password = password

        self.desired_caps = {
            "appPackage": "com.instagram.android",
            "isHeadless": "false",
            "disableWindowAnimation": "true",
            "appActivity": ".activity.MainTabActivity",
            "noReset": "true",
            "platformName": "android",
            "automationName": "UiAutomator2",
            "autoGrantPermissions": "true",
            "newCommandTimeout": "600",
            "androidDeviceReadyTimeout": "30",
            "avd": avd_name
        }

        try:
            while not self.service.is_running:
                self.service.start(env=self.appium_env, node=self.node_path)

            self.driver = webdriver.Remote(
                command_executor="http://localhost:4723/wd/hub",
                desired_capabilities=self.desired_caps
            )

            self.driver.close_app()
            sleep(2)
            self.driver.launch_app()

            if self.check_element_exist(xpath="//*[@text='Please log back in.']"):
                self.driver.find_element_by_xpath(xpath="//*[@text='OK']").click()
                sleep(2)

            while len(self.driver.find_elements_by_xpath(xpath=elxpath.tab_bar_home)) != 1:
                self.try_login()

            self.driver.implicitly_wait(time_to_wait=10)
        except Exception as err:
            self.treat_exception(err)

    def check_element_exist(self, xpath: object) -> bool:
        try:
            return len(self.driver.find_elements_by_xpath(xpath)) != 0
        except (NoSuchElementException, TimeoutException):
            return False

    def try_login(self):
        try:
            if self.check_element_exist(xpath=elxpath.login_username) and \
                    self.check_element_exist(xpath=elxpath.login_password):
                self.driver.find_element_by_xpath(xpath=elxpath.login_username).send_keys(self.username)
                self.driver.find_element_by_xpath(xpath=elxpath.login_password).send_keys(self.password)
                self.driver.find_element_by_xpath(xpath=elxpath.btn_log_in).click()
                sleep(10)
            return self.check_element_exist(xpath=elxpath.tab_bar_home)
        except Exception as err:
            self.treat_exception(err)

    def treat_exception(self, err):
        self.logger.exception(err)
        pass
        self.driver.close_app()
        sleep(2)
        self.driver.launch_app()
        sleep(5)
        return False

    def open_media(self, media_code: str) -> bool:
        url = "https://www.instagram.com/p/{}/".format(media_code)
        self.driver.get(url=url)
        if self.driver.query_app_state('com.android.chrome') in [4]:
            self.driver.terminate_app('com.android.chrome')
            return False
        return self.check_element_exist(xpath=elxpath.post_media_area)

    def open_profile(self, username: str) -> bool:
        self.driver.get(url="https://www.instagram.com/{}/".format(username))
        if self.driver.query_app_state('com.android.chrome') in [4]:
            self.driver.terminate_app('com.android.chrome')
            return False
        if self.check_element_exist(xpath="//*[@text='User not found']"):
            return False
        return self.check_element_exist(xpath=elxpath.row_profile_header_imageview)

    def open_tag(self, tag: str) -> bool:
        self.driver.get(url="https://www.instagram.com/explore/tags/{}/".format(tag))
        if self.driver.query_app_state('com.android.chrome') in [4]:
            self.driver.terminate_app('com.android.chrome')
            return False
        if self.check_element_exist(xpath="//*[@text='User not found']"):
            return False
        return self.check_element_exist(xpath=elxpath.row_profile_header_imageview)

    def swipe_carousel(self) -> None:
        try:
            match = re.search(r"(\d+).*?(\d+)", self.driver.find_element_by_xpath(
                "//*[@resource-id='com.instagram.android:id/carousel_image']").tag_name)
            n = int(match.group(2))
        except NoSuchElementException:
            n = 2  # if don't find the number of pictures work with only 2
            pass

        for x in range(n - 1):
            self.driver.swipe(800, 600, 250, 600, random.randint(500, 1000))
        for x in range(n - 1):
            self.driver.swipe(300, 650, 800, 600, random.randint(500, 1000))

    @staticmethod
    def wait_random() -> None:
        t = random.randint(5, 15)
        sleep(t)

    @staticmethod
    def get_center_element(element) -> tuple:
        x = element.location['x'] + (element.size['width'] / 2)
        y = element.location['y'] + (element.size['height'] / 2)
        return x, y

    def get_type_media(self) -> int:
        row_feed_photo_imageview = "//*[@resource-id='com.instagram.android:id/row_feed_photo_imageview']"
        if self.check_element_exist(xpath="//*[@resource-id='com.instagram.android:id/carousel_media_group']"):
            return MediaType.CAROUSEL
        if self.driver.find_element_by_xpath(row_feed_photo_imageview).tag_name.startswith("Video by "):
            return MediaType.VIDEO
        return MediaType.PHOTO

    def post_double_tap(self) -> None:
        e = self.driver.find_element_by_xpath(xpath=elxpath.post_media_area)
        ex = e.location['x'] + (e.size['width'] / 2)
        ey = e.location['y'] + (e.size['height'] / 2)
        ta = TouchAction(self.driver)
        ta.tap(element=e, x=ex, y=ey, count=2)
        ta.perform()

    def mute_unmute_user(self, switch: bool) -> bool:
        try:
            post_mute = "//*[@resource-id='com.instagram.android:id/posts_mute_setting_row_switch']"
            stories_mute = "//*[@resource-id='com.instagram.android:id/stories_mute_setting_row_switch']"
            self.driver.find_element_by_xpath(xpath=elxpath.btn_Following).click()
            self.driver.find_element_by_xpath("//*[@text='Mute']").click()
            while not (self.driver.find_element_by_xpath(post_mute).get_attribute("checked") == "true") == switch:
                self.driver.find_element_by_xpath(post_mute).click()
            while not (self.driver.find_element_by_xpath(stories_mute).get_attribute("checked") == "true") == switch:
                self.driver.find_element_by_xpath(stories_mute).click()
            self.driver.back()
            self.driver.back()
            return True
        except Exception as err:
            self.treat_exception(err)
            return False

    def mute_user(self):
        return self.mute_unmute_user(switch=True)

    def unmute_user(self):
        return self.mute_unmute_user(switch=False)

    def follow(self, username: str, mute_user: bool = True) -> bool:
        try:
            if self.open_profile(username):
                if self.check_element_exist(xpath="//*[@resource-id='com.instagram.android:id/"
                                                  "profile_header_actions_top_row']//*[@text='Follow']"):
                    self.driver.find_element_by_xpath("//*[@resource-id='com.instagram.android:id/"
                                                      "profile_header_actions_top_row']//*[@text='Follow']").click()
                    if mute_user:
                        self.mute_user()
                    return True
            return False
        except Exception as err:
            self.treat_exception(err)

    def unfollow(self, username: str) -> bool:
        try:
            self.driver.close_app()
            sleep(2)
            self.driver.launch_app()
            self.driver.find_element_by_xpath(xpath=elxpath.tab_bar_profile).click()
            sleep(2)
            self.driver.find_element_by_xpath(xpath=elxpath.tab_bar_profile).click()
            sleep(2)
            self.driver.find_element_by_xpath(xpath=elxpath.row_profile_header_container_following).click()
            self.driver.find_element_by_xpath(
                xpath="//*[@resource-id='com.instagram.android:id/row_search_edit_text']").send_keys(username)
            if self.check_element_exist(xpath="//*[@text='No users found.']"):
                return True
            xpath_btn_following = "//*[@text='{}']/../../..//*[@text='Following']".format(username)
            self.driver.find_element_by_xpath(xpath=xpath_btn_following).click()
            sleep(2)
            self.driver.find_element_by_xpath("//*[@resource-id='com.instagram.android:id/button_positive']").click()
            sleep(2)
            return self.check_element_exist(xpath="//*[@text='{}']/../..//*[@text='Follow']".format(username))
        except Exception as err:
            self.treat_exception(err)

    def friendship(self) -> bool:
        try:
            return self.check_element_exist(xpath=elxpath.btn_Following)
        except Exception as err:
            self.treat_exception(err)
            return False

    def like(self, media_code: str) -> bool:
        try:
            if self.open_media(media_code):
                if self.driver.find_element_by_xpath(xpath=elxpath.row_feed_button_like).tag_name == 'Liked' or \
                        not self.check_element_exist(xpath=elxpath.row_feed_button_like):
                    return False
                else:
                    media_type = self.get_type_media()
                    if media_type == MediaType.VIDEO:
                        self.wait_random()
                        self.driver.find_element_by_xpath(elxpath.row_feed_button_like).click()
                    else:
                        if media_type == MediaType.CAROUSEL:
                            self.swipe_carousel()
                        self.post_double_tap()

                        if not self.driver.find_element_by_xpath(elxpath.row_feed_button_like).tag_name == 'Liked':
                            self.driver.find_element_by_xpath(elxpath.row_feed_button_like).click()
            else:
                return False
            return self.driver.find_element_by_xpath(elxpath.row_feed_button_like).tag_name == 'Liked'
        except Exception as err:
            self.treat_exception(err)

    def chimping_stories(self, amount: int = random.randint(2, 5)) -> bool:
        try:
            self.driver.close_app()
            sleep(3)
            self.driver.launch_app()
            count = 0

            stories_thumbnails = self.driver.find_elements_by_xpath("//*[@resource-id='com.instagram.android:id/"
                                                                    "outer_container']")
            stories_thumbnails[1].click()
            while count < amount:
                t = random.randint(2, 5)
                sleep(t)
                if self.check_element_exist("//*[@resource-id='com.instagram.android:id/reel_viewer_texture_view']"):
                    x1 = random.randint(750, 850)
                    y1 = random.randint(550, 650)
                    x2 = random.randint(200, 300)
                    y2 = random.randint(550, 650)
                    self.driver.swipe(x1, y1, x2, y2, random.randint(500, 1000))
                count += 1

            self.driver.close_app()
            sleep(3)
            self.driver.launch_app()

            return True
        except Exception as err:
            self.treat_exception(err)

    def chimping_timeline(self, amount: int = random.randint(5, 30)) -> bool:
        try:
            self.driver.close_app()
            sleep(3)
            self.driver.launch_app()
            sleep(1)

            el1 = self.driver.find_element_by_xpath(elxpath.layout_container_main)
            start_x = el1.rect["width"] / 2
            start_y = el1.rect["height"] * 0.9
            end_x = el1.rect["width"] / 2
            end_y = el1.rect["height"] * 0.1

            count = 0
            while count < amount:
                self.driver.swipe(start_x, start_y, end_x, end_y, duration=random.randint(2500, 4000))
                count += 1

            self.driver.close_app()
            sleep(3)
            self.driver.launch_app()
            return True
        except Exception as err:
            self.treat_exception(err)

    def take_coffee(self, t: int = random.randint(1, 3) * 60) -> bool:
        try:
            self.driver.close_app()
            sleep(t)
            self.driver.launch_app()
            return True
        except Exception as err:
            self.treat_exception(err)

    def get_followers(self) -> list:
        try:
            users = []
            self.driver.close_app()
            sleep(2)
            self.driver.launch_app()
            self.driver.find_element_by_xpath(xpath=elxpath.tab_bar_profile).click()
            sleep(2)
            self.driver.find_element_by_xpath(xpath=elxpath.tab_bar_profile).click()
            sleep(2)
            followers_count = int(self.driver.find_element_by_xpath(
                xpath="//*[@resource-id='com.instagram.android:id/row_profile_header_textview_followers_count']").text)
            self.driver.find_element_by_xpath(xpath="//*[@resource-id='com.instagram.android:id/"
                                                    "row_profile_header_container_followers']").click()
            follow_list_username = "//*[@resource-id='com.instagram.android:id/follow_list_username']"
            while len(users) < followers_count - 1:
                users = users + [i.text for i in self.driver.find_elements_by_xpath(xpath=follow_list_username)]
                users = list(dict.fromkeys(users))
                self.scrooll_up()
            return users
        except Exception as err:
            self.treat_exception(err)

    def get_following(self) -> list:
        try:
            users = []
            self.driver.close_app()
            sleep(2)
            self.driver.launch_app()
            self.driver.find_element_by_xpath(xpath=elxpath.tab_bar_profile).click()
            sleep(2)
            self.driver.find_element_by_xpath(xpath=elxpath.tab_bar_profile).click()
            sleep(2)
            following_count = int(self.driver.find_element_by_xpath(
                xpath="//*[@resource-id='com.instagram.android:id/row_profile_header_textview_following_count']").text)
            self.driver.find_element_by_xpath(xpath=elxpath.row_profile_header_container_following).click()
            self.driver.find_element_by_xpath(xpath="//*[@resource-id='com.instagram.android:id/"
                                                    "fixed_tabbar_tabs_container']//*[@text='PEOPLE']").click()
            follow_list_username = "//*[@resource-id='com.instagram.android:id/follow_list_username']"
            while len(users) < following_count - 1:
                users = users + [i.text for i in self.driver.find_elements_by_xpath(xpath=follow_list_username)]
                users = list(dict.fromkeys(users))
                self.scrooll_up()
            return users
        except Exception as err:
            self.treat_exception(err)

    def dont_follow_back(self) -> list:
        list_followers = self.get_followers()
        list_following = self.get_following()
        return [i for i in list_following if not list_followers]

    def open_collection(self, collection: str = "All Posts") -> bool:
        try:
            xp_collection = "//*[@text='{}']".format(collection)
            self.driver.close_app()
            sleep(1)
            self.driver.launch_app()
            self.driver.find_element_by_xpath(xpath=elxpath.tab_bar_profile).click()
            sleep(2)
            self.driver.find_element_by_xpath(xpath=elxpath.tab_bar_profile).click()
            sleep(2)
            self.driver.find_element_by_xpath(xpath="//*[@resource-id='com.instagram.android:id/action_bar']"
                                                    "//*[@content-desc='Options']").click()
            sleep(1)
            self.driver.find_element_by_xpath(xpath="//*[@text='Saved']").click()
            t = 0
            while not self.check_element_exist(xpath=xp_collection):
                last_item = self.driver.find_elements_by_xpath(xpath="//*[@resource-id='com.instagram.android:id/"
                                                                     "saved_collection_name']")[-1].text
                self.scrooll_up()
                if last_item == self.driver.find_elements_by_xpath(xpath="//*[@resource-id='com.instagram.android:id/"
                                                                         "saved_collection_name']")[-1].text:
                    t += 1
                if t >= 5:
                    self.logger.info("Collection {} not found.".format(collection))
                    return False

            self.driver.find_element_by_xpath(xpath=xp_collection).click()
            return True
        except Exception as err:
            self.treat_exception(err)
            return False

    def get_users_from_collection(self, collection: str = "All Posts") -> list:
        try:
            row_feed_photo_profile_name = "//*[@resource-id='com.instagram.android:id/row_feed_photo_profile_name']"
            users = []
            if self.open_collection(collection=collection):
                xp = "//*[@resource-id='com.instagram.android:id/recycler_view']" \
                     "//*[@resource-id='com.instagram.android:id/image_button']"
                self.driver.find_element_by_xpath(xpath=xp).click()
                t = 0

                while t < 3:
                    users = users + [i.text.split()[0] for i in
                                     self.driver.find_elements_by_xpath(row_feed_photo_profile_name)]
                    self.scrooll_up()
                    while not self.check_element_exist(row_feed_photo_profile_name):
                        self.scrooll_up()
                    if users[-1] == self.driver.find_elements_by_xpath(row_feed_photo_profile_name)[-1].text.split()[0]:
                        t += 1
                    else:
                        t = 0

            return list(dict.fromkeys(users))
        except Exception as err:
            self.treat_exception(err)

    def search_accounts(self, query: str, amount: int = 10):
        return self.__search(query, amount, tab="ACCOUNTS")

    def search_top(self, query: str, amount: int = 10):
        return self.__search(query, amount, tab="TOP")

    def search_tags(self, query: str, amount: int = 10):
        return self.__search(query, amount, tab="TAGS")

    def search_places(self, query: str, amount: int = 10):
        return self.__search(query, amount, tab="PLACES")

    def __search(self, query: str, amount: int = 10, tab: str = "ACCOUNTS") -> list:
        try:
            users = []
            self.driver.close_app()
            sleep(2)
            self.driver.launch_app()
            self.driver.find_element_by_xpath(xpath="//*[@content-desc='Search and Explore']").click()
            sleep(2)
            self.driver.find_element_by_xpath(xpath="//*[@resource-id='com.instagram.android:id/"
                                                    "action_bar_search_edit_text']").click()
            tab_btn_elem = "//*[@resource-id='com.instagram.android:id/fixed_tabbar_tabs_container']" \
                           "//*[@class='android.widget.FrameLayout']//*[@text='{}']".format(tab)
            self.driver.find_element_by_xpath(xpath=tab_btn_elem).click()
            self.driver.find_element_by_xpath(xpath="//*[@resource-id='com.instagram.android:id/"
                                                    "action_bar_search_edit_text']").send_keys(query)
            self.driver.back()
            row_result = "//*[@resource-id='com.instagram.android:id/row_search_user_username']"
            if tab == "TOP":
                row_result = "//*[@resource-id='com.instagram.android:id/row_search_user_username']"
            if tab == "TAGS":
                row_result = "//*[@resource-id='com.instagram.android:id/row_hashtag_textview_tag_name']"
            if tab == "PLACES":
                row_result = "//*[@resource-id='com.instagram.android:id/row_place_title']"

            while True:
                users = users + [i.text for i in self.driver.find_elements_by_xpath(xpath=row_result)]
                self.scrooll_up()
                users = list(dict.fromkeys(users))
                if len(users) >= amount:
                    return users[0:amount]
        except Exception as err:
            self.treat_exception(err)

    def like_last_medias(self, username: str, amount: int = 1) -> bool:
        try:
            profile_image_view = "(//*[@resource-id='android:id/list']//*[@class='android.widget.ImageView'])[{}]"
            liked = 0
            if self.open_profile(username=username):
                self.driver.find_element_by_xpath(
                    xpath="//*[@resource-id='com.instagram.android:id/row_profile_header_container_photos']").click()
                i = 1
                while liked < amount:
                    if self.check_element_exist(xpath=profile_image_view.format(i)):
                        self.driver.find_element_by_xpath(xpath=profile_image_view.format(i)).click()
                        if self.driver.find_element_by_xpath(
                                xpath=elxpath.row_feed_button_like).tag_name == 'Liked' or \
                                not self.check_element_exist(xpath=elxpath.row_feed_button_like):
                            self.logger.warning("Image already liked.")
                            self.driver.back()
                            i += 1
                            continue
                        else:
                            media_type = self.get_type_media()
                            if media_type == MediaType.VIDEO:
                                self.wait_random()
                                self.driver.find_element_by_xpath(elxpath.row_feed_button_like).click()
                            else:
                                if media_type == MediaType.CAROUSEL:
                                    self.swipe_carousel()
                                self.post_double_tap()

                                if not self.driver.find_element_by_xpath(
                                        elxpath.row_feed_button_like).tag_name == 'Liked':
                                    self.driver.find_element_by_xpath(elxpath.row_feed_button_like).click()

                        if self.driver.find_element_by_xpath(elxpath.row_feed_button_like).tag_name == 'Liked':
                            i += 1
                            liked += 1
                            self.driver.back()
            return True
        except Exception as err:
            self.treat_exception(err)

    def get_last_medias(self, username: str, amount: int = 25) -> list:
        try:
            medias = []
            self.driver.close_app()
            sleep(2)
            self.driver.launch_app()
            if self.open_profile(username=username):
                self.driver.find_element_by_xpath(xpath="//*[@resource-id='com.instagram.android:id/"
                                                        "row_profile_header_post_count_container']").click()
                i = 1
                while len(medias) < amount:
                    image_view = "(//*[@resource-id='android:id/list']" \
                                 "//*[@class='android.widget.ImageView'])[{}]".format(i)
                    if self.check_element_exist(xpath=image_view):
                        self.driver.find_element_by_xpath(xpath=image_view).click()
                        self.driver.find_element_by_xpath(xpath="//*[@resource-id='com.instagram.android:id"
                                                                "/feed_more_button_stub']").click()
                        sleep(1)
                        self.driver.find_element_by_xpath(xpath="//*[@text='Copy Link']").click()
                        medias.append(self.driver.get_clipboard_text().split("/")[4])
                        self.driver.back()
                        i += 1
                    else:
                        self.scrooll_up()
                        i = 1
                    medias = list(dict.fromkeys(medias))
            return medias[0:amount]
        except Exception as err:
            self.treat_exception(err)

    def scrooll_up(self) -> bool:
        try:
            el1 = self.driver.find_element_by_xpath(elxpath.layout_container_main)
            start_x = el1.rect["width"] / 2
            start_y = el1.rect["height"] * 0.9
            end_x = el1.rect["width"] / 2
            end_y = el1.rect["height"] * 0.1
            self.driver.swipe(start_x, start_y, end_x, end_y, duration=random.randint(2500, 4000))
            return True
        except Exception as err:
            self.treat_exception(err)

    def save_in_collection(self, media: str, collection: str = datetime.datetime.now().strftime("%Y%m%d")) -> bool:
        try:
            row_feed_button_save = "//*[@resource-id='com.instagram.android:id/row_feed_button_save']"
            if self.open_media(media_code=media):
                while not self.check_element_exist(xpath=row_feed_button_save):
                    self.scrooll_up()
                actions = TouchAction(self.driver)
                actions.long_press(self.driver.find_element_by_xpath(xpath=row_feed_button_save))
                actions.perform()
                xp = "//*[@resource-id='com.instagram.android:id/save_to_collections_recycler_view']" \
                     "//*[@text='{}']".format(collection)
                thumbnails = "//*[@resource-id='com.instagram.android:id/selectable_image']"
                t = 0
                while t < 2:
                    if not self.check_element_exist(xpath=xp):
                        last_elem = self.driver.find_element_by_xpath("(//*[@resource-id='com.instagram.android:id/"
                                                                      "collection_name'])[last()]").text
                        end_x, end_y = self.get_center_element(
                            self.driver.find_element_by_xpath("({})[1]".format(thumbnails)))
                        start_x, start_y = self.get_center_element(
                            self.driver.find_element_by_xpath("({})[last()]".format(thumbnails)))
                        self.driver.swipe(start_x, start_y, end_x, end_y, duration=random.randint(2500, 4000))
                        if last_elem == self.driver.find_element_by_xpath("(//*[@resource-id='com.instagram.android:id/"
                                                                          "collection_name'])[last()]").text:
                            t += 1
                        else:
                            t = 0
                    else:
                        self.driver.find_element_by_xpath(xp).click()
                        return True
                self.logger.info("Collection not found, creating now.")
                self.driver.find_element_by_xpath("//*[@resource-id='com.instagram.android:id/"
                                                  "save_to_collection_new_collection_button']").click()
                sleep(1)
                self.driver.find_element_by_xpath("//*[@resource-id='com.instagram.android:id/"
                                                  "create_collection_edit_text']").send_keys(collection)
                self.driver.find_element_by_xpath("//*[@resource-id='com.instagram.android:id/"
                                                  "save_to_collection_action_button']").click()
                sleep(2)
                return True
        except Exception as err:
            self.treat_exception(err)

    def delete_collection(self, collection: str) -> None:
        try:
            breakpoint()
            self.open_collection(collection)
        except Exception as err:
            self.treat_exception(err)
