from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import time
import os
import threading

from urllib3.exceptions import NewConnectionError

from image_retriever import make_image
from word_guesser import WordGuesser

from tkinter import *


class BotGUI:
    def __init__(self):
        self.root = Tk()

        self.root.title("Skribbl.IO Bot")
        self.root.geometry("475x150")
        self.root.resizable(True, True)

        self.driver = None

        self.folder_name = f"folder_{time.time()}"

        self.is_guessing = [False]

        self.wpm = [180]

        self.website_label = Label(self.root, text="Website: ")

        self.website_text = StringVar()

        self.website_entry = Entry(self.root, textvariable=self.website_text)
        self.website_entry.insert(END, 'https://skribbl.io')

        self.wpm_label = Label(self.root, text="Typing Speed (wpm): ")

        self.wpm_text = StringVar()

        self.wpm_entry = Entry(self.root, textvariable=self.wpm_text)
        self.wpm_entry.insert(END, '180')

        self.website_go_button = Button(self.root, text='Go', command=self.website_go_submit)
        self.wpm_set_button = Button(self.root, text='Set', command=self.wpm_set_submit)
        self.pause_resume_button = Button(self.root, text='Pause', command=self.pause_resume_submit)
        self.start_round_button = Button(self.root, text='Start Guessing', command=self.start_round_submit)
        self.close_window_button = Button(self.root, text='Close Window', command=self.close_window_submit)
        self.output_label = Label(self.root)

        self.pause_resume_button.config(state="disabled")
        self.start_round_button.config(state="disabled")

        self.website_label.grid(row=0, column=0)
        self.website_entry.grid(row=0, column=1)
        self.website_go_button.grid(row=0, column=2)

        self.wpm_label.grid(row=1, column=0)
        self.wpm_entry.grid(row=1, column=1)
        self.wpm_set_button.grid(row=1, column=2)

        self.start_round_button.grid(row=2, column=0)
        self.pause_resume_button.grid(row=2, column=1)
        self.close_window_button.grid(row=2, column=2)

        self.output_label.grid(row=3, column=1)

        self.root.attributes('-topmost', True)

        self.root.mainloop()


    def website_go_submit(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.website_text.get())

        os.mkdir(self.folder_name)

        self.website_go_button.config(state="disabled")
        self.pause_resume_button.config(state="normal")
        self.start_round_button.config(state="normal")


    def pause_resume_submit(self):
        if self.is_guessing[0]: # pausing game
            self.pause_resume_button.config(text='Resume')
            self.is_guessing[0] = False
            self.output_label.config(text="PAUSED")
        else: # resuming game
            self.pause_resume_button.config(text='Pause')
            self.is_guessing[0] = True
            self.output_label.config(text="RESUMED")


    def guess_loop(self):
        try:
            word_guesser = WordGuesser(self.driver, self.is_guessing, self.output_label, self.wpm)

            word_is_found = False
            while not word_is_found:
                if self.is_guessing[0]:
                    image_name = f"{self.folder_name}/image_{time.time()}"
                    make_image(self.driver, image_name)
                    word_is_found = word_guesser.is_found(image_name + ".png")

        # WebDriver occurs if bot is in the middle of guessing words
        # StopIteration occurs if processing a new round (i.e. user typed 'y' input)
        except (WebDriverException, StopIteration, NewConnectionError):
            pass


    def start_round_submit(self):
        self.is_guessing[0] = True
        self.pause_resume_button.config(text='Pause')
        bot_thread = threading.Thread(target=self.guess_loop)
        bot_thread.daemon = True  # closes thread when main window closes
        bot_thread.start()


    def wpm_set_submit(self):
        self.wpm[0] = int(self.wpm_text.get())


    def close_window_submit(self):
        self.root.destroy()

BotGUI()
