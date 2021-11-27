import pandas as pd
from hazm import *
import pandas as pd


porseman = 'دانشگاه امیرکبیر'


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
        print('****')
        text_to_read = sent_tokenize(normalizer.normalize(df.iloc[[int(i) - 1]]['content'].values[0]))
        for j in text_to_read:
            word_tokenized_list = [x for x in word_tokenize(remove_bad_chars(j)) if x not in list_of_stop_words]
            if main_porseman[0] in word_tokenized_list:
                print('------')
                print(j)
                print('------')
        print(df.iloc[[int(i) - 1]]['url'].values[0])
        print('****')
        print('\n\n')
else:

    list_of_pages = []
    for i in main_porseman:
        try:
            list_of_pages.append(main_dict[i]['record_id'])
        except:
            pass
    common_pages = list(set(list_of_pages[0]).intersection(*list_of_pages))
    
    result = []
    main_text = []
    while not result and len(common_pages) > 1:
        for i in common_pages:
            sus_page = df.iloc[[int(i) - 1]]['content'].values[0]
            final_text = []
            text_to_read = sent_tokenize(normalizer.normalize(sus_page))
            for confli in text_to_read:
                text_after_remove_and_clear = [x for x in word_tokenize(remove_bad_chars(confli)) if x not in list_of_stop_words]
                get_tag = tagger.tag(text_after_remove_and_clear)
                for iterate in get_tag:
                        if iterate[1] == 'V':
                            if len(lemmatizer.lemmatize(iterate[0]).split('#')) == 2:
                                final_text.append(lemmatizer.lemmatize(iterate[0]).split('#')[1])
                            else:
                                final_text.append(iterate[0])
                        else:
                                final_text.append(iterate[0])
                index_result = []
                for z in main_porseman:
                    try:
                        index_result.append(final_text.index(z))
                        flag = True
                    except:
                        flag = False
                        break
                if i not in result and len(index_result) > 1 and flag:
                    flag_sample = True
                    for index, value in enumerate(index_result):
                        if index != 0:
                            if value - index_result[index - 1] != 1:
                                flag_sample = False
                                break
                    if flag_sample:
                        result.append(i)
                        main_text.append(confli)
        del main_porseman[-1]      
    
    for i in range(len(main_text)):
        print('***')
        print('------')
        print(main_text[i])
        print('------')
        print(df.iloc[[result[i] - 1]]['title'].values[0])
        print('***')
        print('\n\n')