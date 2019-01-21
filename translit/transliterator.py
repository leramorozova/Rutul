from praatio import tgio
import re


class ParseTextGrid:
    def __init__(self, filename):
        self.filename = filename

    def file_open(self):
        return tgio.openTextgrid(self.filename)

    def morph(self):
        tg = self.file_open()
        morph_tier = tg.tierDict["speakerid_Morph-txt-kna"]
        morph_list = [list(word) for word in morph_tier.entryList]
        return morph_list

    def lemma(self):
        tg = self.file_open()
        lemma_tier = tg.tierDict["speakerid_Lemma-txt-kna"]
        lemma_list = [list(word) for word in lemma_tier.entryList]
        return lemma_list

    def transcription(self):
        tg = self.file_open()
        transcription_tier = tg.tierDict["speakerid_Transcription-txt-kna"]
        transcription_list = [list(word) for word in transcription_tier.entryList]
        return transcription_list

    def alternate_tier(self, entry_list, tier_name, tg, outname):
        entry_tuple = [tuple(word) for word in entry_list]
        alternation = tgio.IntervalTier(name=tier_name, entryList=entry_tuple)  # массив кортежей => объект praatio
        tg.replaceTier(tier_name, alternation)
        tg.save(outname)

    def latin(self):  # тут делается словарь
        with open('translit.csv', 'r') as csv:
            alph = csv.read()
            arr = [el.split(',') for el in alph.split('\n')][:-1]
            dict = {el[0]: el[1] for el in arr}
        return dict

    def trans(self, phrase):  # тут транислитерация
        dict = self.latin()
        new_phrase = []
        for el in phrase.split(' '):
            word = ''
            kir_word = el.lower()
            while kir_word != '':
                if kir_word[-1] in '<>-.,?:;"!()=/*':
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
            if word[0] == 'ʲ':
                word = re.sub('ʲ', 'j', word)
            new_phrase.append(word)
        return ' '.join(new_phrase)

    def latinize_trans_morph(self):
        tg = self.file_open()
        morph = self.morph()
        for el in morph:
            el[2] = self.trans(el[2])
        transcript = self.transcription()
        for el in transcript:
            el[2] = self.trans(el[2])
        lemma = self.lemma()
        for el in lemma:
            print(el[2])
            el[2] = self.trans(el[2])
        self.alternate_tier(morph, "speakerid_Morph-txt-kna", tg, "kna_muzafer06.TextGrid")
        self.alternate_tier(lemma, "speakerid_Lemma-txt-kna", tg, "kna_muzafer06.TextGrid")
        self.alternate_tier(transcript, "speakerid_Transcription-txt-kna", tg, "kna_muzafer06.TextGrid")


def main():  # здесь кириллица заменяется на латиницу
    parser = ParseTextGrid("kna_muzafer06.TextGrid")
    parser.latinize_trans_morph()
    return 0


if __name__ == "__main__":
    main()
