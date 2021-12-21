import pandas as pd
from hazm import *
from collections import Counter
from collections import OrderedDict
import math


porseman = 'دانشگاه امیرکبیر'
records_per_page = 10

normalizer = Normalizer()
lemmatizer = Lemmatizer()
tagger = POSTagger(model='phase-1/resources/postagger.model')

list_of_stop_words = stopwords_list()
word_in_doc, docs_tfidf, result_doc, title_sentences = {}, {}, {}, {}

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

def get_sentence_from_dict(content, word):
    match_sentence = []
    text_to_read = sent_tokenize(normalizer.normalize(content))
    for i in text_to_read:
        text_as_list = [x for x in word_tokenize(remove_bad_chars(i)) if x not in list_of_stop_words]
        if word in text_as_list: match_sentence.append(i)
    return match_sentence

def calculate_tfidf(dictionary):
    for iterate in dictionary:
        new_value = (1 + math.log(dictionary[iterate])) * math.log(len(df) / len(word_in_doc[iterate]))
        if new_value == 0:
            del dictionary[iterate]
        else:
            dictionary[iterate] = new_value
    return dictionary

def list_power(my_list):
    return [x**2 for x in my_list]

def print_result(list_of_sorted_news, title_sentences):
    if len(list_of_sorted_news) > records_per_page:
        for i in list_of_sorted_news[:records_per_page]:
            print('--------------')
            print(title_sentences[i]['title'], end='\n\n')
            for j in list(title_sentences[i]['sentences']):
                print(j)
            print('--------------')


if __name__ == '__main__':

    df = pd.read_excel('phase-1/IR1_7k_news.xlsx')

    word_doc(df)

    for index, content in df['content'].iteritems():
        content_list = make_content_list(content)
        count_of_word = calculate_tfidf(dict(Counter(content_list)))
        docs_tfidf.update({index + 2: count_of_word})

    query_weight = calculate_tfidf(dict(Counter(make_content_list(porseman))))

    for i in docs_tfidf:
        matches_words = set(list(query_weight.keys())) & set(list(docs_tfidf[i].keys()))
        numerator = 0
        if matches_words:
            all_sentences = []
            title = df.iloc[[i - 2]]['title'].values[0]
            denominator = math.sqrt(sum(list_power(list(docs_tfidf[i].values())))) * math.sqrt(sum(list_power(list(query_weight.values()))))
            for dict_iteration in matches_words:
                match_sentence = get_sentence_from_dict(df.iloc[[i - 2]]['content'].values[0], dict_iteration)
                if match_sentence: all_sentences.extend(match_sentence)
                numerator += query_weight[dict_iteration] * docs_tfidf[i][dict_iteration]
            cosine = denominator / numerator
            result_doc.update({i: cosine}) 
            title_sentences.update({i: {'title': title, 'sentences': dict.fromkeys(all_sentences).keys()}})
    sorted_docs = OrderedDict(sorted(result_doc.items(), key=lambda x: x[1]))

    print_result(list(sorted_docs), title_sentences)
