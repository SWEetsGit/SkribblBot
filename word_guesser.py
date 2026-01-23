import torch
import open_clip # must run 'pip install open_clip_torch'
from PIL import Image
from open_clip import tokenizer as openclip_tokenizer
from selenium.webdriver.common.by import By
from key_input import KeyInput
import random
import time

# Load CLIP
model, preprocess, tokenizer = open_clip.create_model_and_transforms(
    'ViT-B-32',
    pretrained='openai'
)
model.eval()

# Load the word list - https://gist.github.com/mvark/9e0682c62d75625441f6ded366245203
with open("words.txt") as f:
    word_list = [w.strip() for w in f]


# Should match the right pattern
def matches_pattern(word_element, pattern):
    # must be same length
    if len(word_element) != len(pattern):
        return False

    for wc, pc in zip(word_element, pattern):
        if pc == "_":
            character = ord(wc.lower())
            if ord('a') <= character <= ord('z'):  # word must have a letter in that spot
                continue
            else:
                return False
        if wc.lower() != pc.lower():
            return False

    return True


class WordGuesser:
    def __init__(self, driver, is_guessing, output_label, wpm):
        self.driver = driver

        self.is_guessing = is_guessing

        self.output_label = output_label

        self.wpm = wpm

        self.guessed_words = set()

        self.filtered_word_list = []

        self.word_typer = KeyInput(driver)

        # Random commentary lines to make the bot appear more human
        self.lines = [
            "idk what this is",
            "lol",
            "honestly not sure what I'm looking at",
            "kinda hard to figure out this word",
            "bruh what",
            "duuude",
            "how can anyone guess this...",
            "ugh",
            "6-7",
            "this sucks",
            "pretty hard word to guess"
        ]

        self.commentary_gap = 0


    def get_pattern(self):
        chars = self.driver.find_elements(By.CSS_SELECTOR, ".hint, .hint.uncover")
        parts = []
        for ch in chars:
            # If it's a space (class="hint uncover"), manually add a space
            class_name = ch.get_attribute("class")
            if "uncover" in class_name and ch.text == "":
                parts.append(" ")
                continue

            parts.append(ch.text)

        # Just a note that this isn't redundant... appending to a list first is more efficient (strings are immutable)
        return "".join(parts)


    def commentary(self):
        # number of guesses for the word before random commentary starts
        guesses_before_commentary = 6
        if len(self.guessed_words) > guesses_before_commentary:
            if self.commentary_gap <= 0:
                line = self.lines[random.randint(0, len(self.lines) - 1)]
                self.output_label.config(text=f'Commentary: {line}')
                self.word_typer.input_text(line, self.wpm[0])
                self.commentary_gap = random.randint(3, 6)
            else:
                self.commentary_gap -= 1


    def is_found(self, image_name):
        max_results = random.randint(2, 4)
        current_pattern = self.get_pattern()
        self.output_label.config(text=f'Word hint: {' '.join(current_pattern)}')

        if not self.filtered_word_list:
            self.filtered_word_list = [w for w in word_list if matches_pattern(w, current_pattern)]
        else:
            self.filtered_word_list = [w for w in self.filtered_word_list if matches_pattern(w, current_pattern)]

        image = preprocess(Image.open(image_name)).unsqueeze(0)
        with torch.no_grad():
            image_features = model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)

        filtered_words = openclip_tokenizer.tokenize(self.filtered_word_list)
        with torch.no_grad():
            text_features = model.encode_text(filtered_words)
            text_features /= text_features.norm(dim=-1, keepdim=True)

        similarity = (image_features @ text_features.T).squeeze(0)
        num_candidates = similarity.numel()
        top_k_num = min(num_candidates, max_results)
        scores, indices = similarity.topk(top_k_num)
        guesses = [(self.filtered_word_list[i], float(scores[j])) for j, i in enumerate(indices)]

        guessed_words = []
        for word, score in guesses:
            guessed_words.append(word)

        if num_candidates == top_k_num:
            idx = 0
            remaining_words = max_results - num_candidates
            while idx < remaining_words and idx < len(self.filtered_word_list):
                guessed_words.append(self.filtered_word_list[idx])
                idx += 1

        appendable_words = [] # the actual words that have been input/ guessed
        for word in set(guessed_words):
            # This section deals with pausing/ resuming of guessing words

            if self.is_guessing[0]:
                # This part deals with guessing the word
                new_pattern = self.get_pattern()
                if '_' not in new_pattern: # word was found
                    return True
                self.output_label.config(text=f'Guess: {' '.join(word)}')
                self.word_typer.input_text(word, self.wpm[0])
                appendable_words.append(word)
                if new_pattern != current_pattern: # reset, pattern has been updated
                    return False
                self.commentary()
                time.sleep(float(random.randint(50, 200)) / 100)

        self.filtered_word_list = list(set(self.filtered_word_list) - set(appendable_words))
        self.guessed_words = self.guessed_words.union(set(appendable_words))

        return False
