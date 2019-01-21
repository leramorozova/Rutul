from praatio import tgio


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

    def gloss(self):
        tg = self.file_open()
        gloss_tier = tg.tierDict["speakerid_Gloss-txt-en"]
        gloss_list = [list(word) for word in gloss_tier.entryList]
        return gloss_list

    def lemma(self):
        tg = self.file_open()
        lemma_tier = tg.tierDict["speakerid_Lemma-txt-kna"]
        lemma_list = [list(word) for word in lemma_tier.entryList]
        return lemma_list

    def translation(self):
        tg = self.file_open()
        translation_tier = tg.tierDict["ft@speakerid-txt-kna"]
        translation_list = [list(word) for word in translation_tier.entryList]
        return translation_list

    def sent_start_end(self, morph):
        idx_list = []
        for el in self.translation():
            start = el[0]
            end = el[1]
            for i in range(len(morph)):
                if morph[i][0] == start:
                    for j in range(len(morph)):
                        if i + j < len(morph) and morph[i + j][1] == end:
                            idx_list.append((i, i + j))
                        j += 1
        return idx_list


parse = ParseTextGrid("kna_muzafer06.TextGrid")

translation = parse.translation()
morph = parse.morph()
gloss = parse.gloss()
lemma = parse.lemma()
idxs = parse.sent_start_end(morph)
for i, sent in enumerate(idxs):
    start_idx = sent[0]
    end_idx = sent[1]
    while start_idx != end_idx + 1:
        print(lemma[start_idx][2] + '\t' + morph[start_idx][2] + '\t' + gloss[start_idx][2] + '\t' + translation[i][2])
        start_idx += 1
            #with open("concord.txt", 'a', encoding="UTF-8") as
                #print(word[2])
