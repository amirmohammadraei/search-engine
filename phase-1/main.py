import pandas as pd
from hazm import *
import pandas as pd


porseman = 'بین‌الملل'


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


df_index = 1


df = pd.read_excel('phase-1/IR1_7k_news.xlsx')
for i in df['content']:
    final_text = []
    text_to_read = sent_tokenize(normalizer.normalize(i))
    for inside in text_to_read:
        text_after_remove_and_clear = [x for x in word_tokenize(remove_bad_chars(inside)) if x not in list_of_stop_words]
        get_tag = tagger.tag(text_after_remove_and_clear)
        for iterate in get_tag:
                if iterate[1] == 'V':
                    if len(lemmatizer.lemmatize(iterate[0]).split('#')) == 2:
                        final_text.append(lemmatizer.lemmatize(iterate[0]).split('#')[1])
                    else:
                        final_text.append(iterate[0])
                else:
                        final_text.append(iterate[0])

    for index, elemnt in enumerate(final_text):
        try:
            main_dict[elemnt]['number_of_repetitions'] += 1
            if df_index not in main_dict[elemnt]['record_id']:
                main_dict[elemnt]['record_id'].append(df_index)
        except:
            main_dict[elemnt] = {
                'number_of_repetitions': 1,
                'record_id': [df_index],
                'id_index': {
                    df_index: []
                },
                'count_in_record': {
                    df_index: 0
                }
            }
        try:
            main_dict[elemnt]['id_index'][df_index].append(index)
        except:
            main_dict[elemnt]['id_index'][df_index] = [index]
        
        try:
            main_dict[elemnt]['count_in_record'][df_index] += 1
        except:
            main_dict[elemnt]['count_in_record'][df_index] = 1

    df_index += 1

manage_porseman = tagger.tag(word_tokenize(remove_bad_chars(normalizer.normalize(porseman))))

main_porseman = []
for iterate in manage_porseman:
    if iterate[1] == 'V':
        if len(lemmatizer.lemmatize(iterate[0]).split('#')) == 2:
            main_porseman.append(lemmatizer.lemmatize(iterate[0]).split('#')[1])
        else:
            main_porseman.append(iterate[0])
    else:
            main_porseman.append(iterate[0])
if len(main_porseman) == 1:
    id_of_news = main_dict[main_porseman[0]]['record_id']
    for i in id_of_news:
        print(df.iloc[[int(i) - 1]]['url'].values[0])