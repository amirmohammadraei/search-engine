import pandas as pd
from hazm import *
import pandas as pd


porseman = ''


normalizer = Normalizer()
lemmatizer = Lemmatizer()
tagger = POSTagger(model='phase-1/resources/postagger.model')


list_of_stop_words = stopwords_list()
main_dict = {}


def remove_bad_chars(text):
    to_replace_chars = [';', ':', '!', "*", '.', ',', '،', '\n', '?', '(', ')', '؛', '٪', '%', '/', '[', ']', '-', '_', '=', '&', '+']
    for i in to_replace_chars:
        text = text.replace(i, ' ')
    return text