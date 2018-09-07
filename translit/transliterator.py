# Все еще немного ломается - надо, дополнить, чтобы сначала заменялись более длинные слова в слое

import re


def latin():  # тут делается словарь
    with open('translit.csv', 'r') as csv:
        alph = csv.read()
        arr = [el.split(',') for el in alph.split('\n')][:-1]
        dict = {el[0]: el[1] for el in arr}
    return dict


def trans(phrase):  # тут транислитерация
    dict = latin()
    new_phrase = []
    for el in phrase.split(' '):
        word = ''
        kir_word = el.lower()
        while kir_word != '':
            if kir_word[-1] in '<>-.,?:;"!()=/':
                word = kir_word[-1] + word
                kir_word = kir_word[:-1]
            else:
                if len(kir_word) > 1:
                    comb = kir_word[-2] + kir_word[-1]
                    comb = comb.lower()
                    if comb in dict:
                        word = dict[comb] + word
                        kir_word = kir_word[:-2]
                    else:
                        word = dict[kir_word[-1]] + word
                        kir_word = kir_word[:-1]
                else:
                    word = dict[kir_word[-1]] + word
                    kir_word = kir_word[:-1]
        new_phrase.append(word)
    return ' '.join(new_phrase)


def text_proc():  # здесь делаются словари кириллица-латиница для каждого слоя
    with open ('kna_maisarat02.TextGrid', 'r', encoding='UTF-16') as file:  # заменить имя файла
        text = file.read()
        text = re.sub('\n', ' ', text)
        tran_layer = re.search('Transcription(.*?)Morph', text).group(1)
        tran_kir = set(re.findall('text = "(.*?)"', tran_layer))
        gloss_layer = re.search('Morph(.*?)Lemma', text).group(1)
        gloss_kir = set(re.findall('text = "(.*?)"', gloss_layer))
        lemma_layer = re.search('Lemma(.*?)Gloss', text).group(1)
        lemma_kir = set(re.findall('text = "(.*?)"', lemma_layer))
    tran_d = {el: trans(el) for el in tran_kir}
    gloss_d = {el: trans(el) for el in gloss_kir}
    lemma_d = {el: trans(el) for el in lemma_kir}
    return tran_d, gloss_d, lemma_d


def main():  # здесь кириллица заменяется на латиницу
    with open('kna_maisarat02.TextGrid', 'r', encoding='UTF-16') as file:  # заменить имя файла
        text = file.read()
        tran_d, gloss_d, lemma_d = text_proc()
        for el in tran_d:
            text = re.sub(el, tran_d[el], text)
        for el in gloss_d:
            text = re.sub(el, gloss_d[el], text)
        for el in lemma_d:
            text = re.sub(el, lemma_d[el], text)
        with open('kna_maisarat02_lat.TextGrid', 'w', encoding='UTF-16') as new_file:  # заменить имя файла
            new_text = new_file.write(text)
            new_file.close()


main()


