from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random

class KeyInput:
    def __init__(self, driver):
        self.driver = driver

        # gets the visible input box for autofocusing (for convenience purposes so user doesn't have to manually click input box)
        inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        self.input_box = next(
            inp for inp in inputs
            if inp.is_displayed() and inp.size['width'] > 0 and inp.size['height'] > 0
        )


    # Speed in words-per-minute (wpm)
    def input_text(self, word, speed):
        seconds_per_word = 60 / float(speed)

        # amount of time taken to type one character
        # 5 = the average length of an English word (actually more like 4.7 but whatever)
        char_time = seconds_per_word / 5

        actions = ActionChains(self.driver)
        actions.move_to_element(self.input_box)
        actions.click()
        for letter in word:
            actions.send_keys(letter).perform()
            rand_sleep = (float(random.randint(0, 6)) - 2) / 100
            time.sleep(max(0.01, char_time + rand_sleep))

        time.sleep(float(random.randint(5, 15)) / 100)
        actions.send_keys(Keys.ENTER).perform()