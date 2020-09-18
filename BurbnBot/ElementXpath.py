class elxpath(object):
    tab_bar_home = "//*[@resource-id='com.instagram.android:id/tab_bar']//*[@content-desc='Home']"
    tab_bar_lupe = "//*[@resource-id='com.instagram.android:id/tab_bar']//*[@content-desc='Search and Explore']"
    login_username = "//*[@resource-id='com.instagram.android:id/login_username']"
    login_password = "//*[@resource-id='com.instagram.android:id/password']"
    btn_log_in = "//*[@resource-id='com.instagram.android:id/button_text']"

    post_media_area = "//*[@resource-id='android:id/list']//*[@class='android.widget.FrameLayout'][2]"
    row_profile_header_imageview = "//*[@resource-id='com.instagram.android:id/row_profile_header_imageview']"

    btn_Following = "//*[@resource-id='com.instagram.android:id/profile_header_actions_top_row']//*[@text='Following']"

    tab_bar_profile = "//*[@resource-id='com.instagram.android:id/profile_tab']"
    row_profile_following = "//*[@resource-id='com.instagram.android:id/row_profile_header_following_container']"
    row_feed_button_like = "//*[@resource-id='com.instagram.android:id/row_feed_button_like']"
    layout_container_main = "//*[@resource-id='com.instagram.android:id/layout_container_main']"