# not entirely sure what this was for, ignore i guess

import os
import sys

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# extract all unique items from the text file, don't split the words
def extract(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Use a set to store unique phrases
        unique_phrases = set(file.readlines())
        unique_phrases = {phrase.strip() for phrase in unique_phrases if phrase.strip()}

        for phrase in sorted(unique_phrases):
            print(phrase)

file_path = "projects.txt"
extract(file_path)
# for word in words:
    # print(word)