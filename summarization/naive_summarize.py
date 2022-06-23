import pandas as pd
from ArticutAPI import Articut
from collections import Counter
from pprint import pprint
import re
# 這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
username = "loveyoosic4ever@gmail.com"
# 這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey = "=Zs6wI!L_KRO&_Ff3H5VQx3Fx145A%v"
articut = Articut(username, apikey)


def naive_summarize(sentences, word_limit=200):
    result = [sentences[0]]
    sentences.pop(0)
    word_limit -= len(result[0])
    tokenized_sentences = []
    for sentence in sentences:
        try:
            tokens = str(articut.parse(sentence).get(
                "result_segmentation")).split("/")
        except:
            tokens = ['']
        tokenized_sentences.append(tokens)
    full_text = [word for sentence in tokenized_sentences for word in sentence]
    freq_table = dict(Counter(full_text))

    # value sentence score
    sentence_value = {}

    for idx, sentence in enumerate(sentences):
        word_count_in_sentence = len(tokenized_sentences[idx])

        for valueWord in freq_table:
            if valueWord in sentence:
                if sentence in sentence_value:
                    sentence_value[sentence] += freq_table[valueWord]
                else:
                    sentence_value[sentence] = freq_table[valueWord]
        sentence_value[sentence] = sentence_value[sentence] // word_count_in_sentence if sentence in sentence_value else 0

    # threshold
    sum_values = 0

    for entry in sentence_value:
        sum_values += sentence_value[entry]

    average = int(sum_values/len(sentence_value))

    threshold = average*1.0
    sentence_count = 0

    summary = ''

    for sentence in sentences:
        if sentence in sentence_value and sentence_value[sentence] > threshold:
            summary += " " + sentence
            sentence_count += 1

    summary = re.sub('\n', '', summary)
    result += summary.split(' ')
    word_count = 0
    sentence_count = len(result)
    for idx, res in enumerate(result):
        word_count += len(res)
        if word_count >= word_limit:
            sentence_count = idx + 1 if idx < sentence_count else idx
            break
    return ''.join(result[:sentence_count])
