import pandas as pd
from hazm import *
import pandas as pd
from collections import Counter
import math


porseman = ''


normalizer = Normalizer()
lemmatizer = Lemmatizer()
tagger = POSTagger(model='phase-1/resources/postagger.model')


list_of_stop_words = stopwords_list()
word_in_doc, docs_tfidf = {}, {}


def remove_bad_chars(text):
    to_replace_chars = [';', ':', '!', "*", '.', ',', '،', '\n', '?', '(', ')', '؛', '٪', '%', '/', '[', ']', '-', '_', '=', '&', '+']
    for i in to_replace_chars:
        text = text.replace(i, ' ')
    return text

def word_doc(df):
    for  index, content in df['content'].iteritems():
        content_list = make_content_list(content)
        for word in content_list:
            try:
                if index not in word_in_doc[word]: word_in_doc[word].append(index)
            except KeyError:
                word_in_doc[word] = [index]     

def make_content_list(content):
    final_text = []
    text_to_read = sent_tokenize(normalizer.normalize(content))
    for sentence in text_to_read:
        text_after_remove_and_clear = [x for x in word_tokenize(remove_bad_chars(sentence)) if x not in list_of_stop_words]
        get_tag = tagger.tag(text_after_remove_and_clear)
        for iterate in get_tag:
                if iterate[1] == 'V': 
                    final_text.append(lemmatizer.lemmatize(iterate[0]).split('#')[1]) if len(lemmatizer.lemmatize(iterate[0]).split('#')) == 2 else final_text.append(iterate[0])
                else: 
                    final_text.append(iterate[0])
    return final_text 

df = pd.read_excel('phase-1/IR1_7k_news.xlsx')

word_doc(df)

for index, content in df['content'].iteritems():
    content_list = make_content_list(content)
    count_of_word = dict(Counter(content_list))
    for iterate in count_of_word:
        new_value = (1 + math.log(count_of_word[iterate])) * math.log(len(df) / len(word_in_doc[iterate]))
        if new_value == 0:
            del count_of_word[iterate]
        else:
            count_of_word[iterate] = new_value
    docs_tfidf.update({index + 2: count_of_word})
docs_tfidf
