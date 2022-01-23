from hashlib import new
from itertools import count
from operator import le
import pandas as pd
from hazm import *
from collections import Counter
from collections import OrderedDict
import math
import json
from random import randrange


porseman = 'دانشگاه امیرکبیر'
records_per_page = 10

normalizer = Normalizer()
lemmatizer = Lemmatizer()
tagger = POSTagger(model='phase-1/resources/postagger.model')

list_of_stop_words = stopwords_list()
word_in_doc, docs_tfidf, result_doc, title_sentences = {}, {}, {}, {}
cluster = { i: [randrange(1, 50062)] for i in range(1, 101)}
new_cluster = { i: [] for i in range(1, 101)}
second_iter = { i: [] for i in range(1, 101)}

def remove_bad_chars(text):
    to_replace_chars = [';', ':', '!', "*", '.', ',', '،', '\n', '?', '(', ')', '؛', '٪', '%', '/', '[', ']', '-', '_', '=', '&', '+']
    for i in to_replace_chars:
        text = text.replace(i, ' ')
    return text

def word_doc(df):
    counter1 = 1
    for  index, content in df['content'].iteritems():
        content_list = make_content_list(content)
        for word in content_list:
            try:
                if counter1 not in word_in_doc[word]: word_in_doc[word].append(counter1)
            except KeyError:
                word_in_doc[word] = [counter1]
        counter1 += 1

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
        new_value = (1 + math.log10(dictionary[iterate])) * math.log10(len(df) / len(word_in_doc[iterate]))
        if new_value == 0:
            del dictionary[iterate]
        else:
            dictionary[iterate] = format(new_value, ".4f")
    return dictionary

def list_power(my_list):
    return [float(x)**2 for x in my_list]

def clustering_first_time(docs_tfidf):
    for i in range(1, 50062):
        doc_to_compare = docs_tfidf[str(i)]
        maximum_value = 0
        cluster_index = 0
        for key in cluster:
            centroid = docs_tfidf[str(cluster[key][0])]
            equal_words = list(centroid.keys() & doc_to_compare.keys())
            numerator = 0
            for word in equal_words: numerator += float(doc_to_compare[word]) * float(centroid[word])
            denominator = math.sqrt(sum(list_power(list(centroid.values())))) * math.sqrt(sum(list_power(list(doc_to_compare.values()))))
            cosine = numerator / denominator
            if cosine > maximum_value: 
                maximum_value = cosine
                cluster_index = key
        cluster[cluster_index].append(i)
    return cluster


if __name__ == '__main__':

    df1 = pd.read_excel('phase-3/IR00_dataset_ph3/IR00_3_11k News.xlsx')
    df2 = pd.read_excel('phase-3/IR00_dataset_ph3/IR00_3_17k News.xlsx')
    df3 = pd.read_excel('phase-3/IR00_dataset_ph3/IR00_3_20k News.xlsx')

    df2['id'] = df2['id'] + 11437
    df3['id'] = df3['id'] + 29401
    
    frames = [df1, df2, df3]
    df = pd.concat(frames)


    # !!!!!!!!! uncomment if it is your first time !!!!!!!!!
    # word_doc(df)
    # counter = 1
    # for index, content in df['content'].iteritems():
    #     content_list = make_content_list(content)
    #     count_of_word = calculate_tfidf(dict(Counter(content_list)))
    #     docs_tfidf.update({counter: count_of_word})
    #     counter += 1
    # json.dump(docs_tfidf, open("docs_tfidf.txt",'w'))
    # json.dump(word_in_doc, open("word_in_dpc.txt",'w'))

    docs_tfidf = json.load(open("docs_tfidf.txt"))
    word_in_doc = json.load(open("word_in_dpc.txt"))
    
    for sub in docs_tfidf:
        for i in docs_tfidf[sub]:
            docs_tfidf[sub][i] = float(docs_tfidf[sub][i])

    # query_weight = calculate_tfidf(dict(Counter(make_content_list(porseman))))

    # !!!!!!!!! uncomment if it is your first time !!!!!!!!!
    # cluster = clustering_first_time(docs_tfidf)
    # json.dump(cluster, open("cluster.txt",'w'))
    
    cluster = json.load(open("cluster.txt"))
    new_cluster_counter = 1
    for i in cluster:
        data_to_add = Counter()
        for j in cluster[str(i)]:
            data_to_add += docs_tfidf[str(j)]
        new_cluster[new_cluster_counter] = dict(data_to_add)
        for change in new_cluster[new_cluster_counter]:
            new_cluster[new_cluster_counter][change] = new_cluster[new_cluster_counter][change] / len(docs_tfidf[str(i)])
        new_cluster_counter += 1
    
    for i in range(1, 50062):
        doc_to_compare = docs_tfidf[str(i)]
        maximum_value = 0
        cluster_index = 0
        for key in new_cluster:
            centroid = new_cluster[key]
            equal_words = list(centroid.keys() & doc_to_compare.keys())
            numerator = 0
            for word in equal_words: numerator += float(doc_to_compare[word]) * float(centroid[word])
            denominator = math.sqrt(sum(list_power(list(centroid.values())))) * math.sqrt(sum(list_power(list(doc_to_compare.values()))))
            cosine = numerator / denominator
            if cosine > maximum_value: 
                maximum_value = cosine
                cluster_index = key
        second_iter[cluster_index].append(i)

    second_iter
            