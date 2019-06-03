from praatio import tgio
from collections import Counter
import re
import os

verbs = Counter()
nouns = Counter()
adjs = Counter()


class ParseTextGrid:
    def __init__(self, filename):
        self.filename = filename

    def file_open(self):
        return tgio.openTextgrid(self.filename)

    def morph(self):
        tg = self.file_open()
        morph_tier = tg.tierDict["speakerid_Morph-txt-kna"]
        morph_list = [word[2] for word in morph_tier.entryList]
        return morph_list

    def gloss(self):
        tg = self.file_open()
        gloss_tier = tg.tierDict["speakerid_Gloss-txt-en"]
        gloss_list = [word[2] for word in gloss_tier.entryList]
        return gloss_list

    def pos(self):
        tg = self.file_open()
        pos_tier = tg.tierDict["speakerid_POS-txt-kna"]
        pos_list = [word[2] for word in pos_tier.entryList]
        return pos_list

    def lemma(self):
        tg = self.file_open()
        lemma_tier = tg.tierDict["speakerid_Lemma-txt-kna"]
        lemma_list = [word[2] for word in lemma_tier.entryList]
        return lemma_list


class CountingTG(ParseTextGrid):
    def count_nouns(self):
        global nouns
        morph_layer = self.morph()
        gloss_layer = self.gloss()
        pos_layer = self.pos()
        lemma_layer = self.lemma()
        for i in range(len(pos_layer)):
            if pos_layer[i] == 'n':
                noun = re.sub("[,.!\"/]", "", morph_layer[i])
                nouns.update([(noun, gloss_layer[i], lemma_layer[i])])
        return dict(nouns)

    def count_verbs(self):
        global verbs
        morph_layer = self.morph()
        gloss_layer = self.gloss()
        pos_layer = self.pos()
        lemma_layer = self.lemma()
        for i in range(len(pos_layer)):
            if pos_layer[i] == "vb":
                complex = morph_layer[i] + " " + morph_layer[i + 1]
                glosses = gloss_layer[i] + " " + gloss_layer[i + 1]
                lemmas = lemma_layer[i] + " " + lemma_layer[i + 1]
                complex = re.sub("[,.!\"/]", "", complex)
                verbs.update([(complex, glosses, lemmas)])
                i += 1
            elif pos_layer[i] == "v":
                verb = re.sub("[,.!\"/]", "", morph_layer[i])
                verbs.update([(verb, gloss_layer[i], lemma_layer[i])])
            elif pos_layer[i] == "stat":
                stat = re.sub("[,.!\"/]", "", morph_layer[i])
                verbs.update([(stat, gloss_layer[i], lemma_layer[i])])
        return dict(verbs)

    def count_adj(self):
        global adjs
        morph_layer = self.morph()
        gloss_layer = self.gloss()
        pos_layer = self.pos()
        lemma_layer = self.lemma()
        for i in range(len(pos_layer)):
            if pos_layer[i] == 'adj':
                adj = re.sub("[,.!\"/]", "", morph_layer[i])
                adjs.update([(adj, gloss_layer[i], lemma_layer[i])])
        return dict(adjs)


def doc_write(fd, dict):
    for key in dict:
        row = ','.join([str(dict[key]), key[0], key[1]]) + '\n'
        print(row)
        fd.write(row)


for file in os.listdir("srcs"):
    print(file)
    CT = CountingTG(os.path.join("srcs", file))
    verb_dict = CT.count_verbs()
    noun_dict = CT.count_nouns()
    adj_dict = CT.count_adj()


with open("verb_list.csv", "a", encoding="UTF-8") as verb_fd:
    for key in verb_dict:
        row = ','.join([str(verb_dict[key]), key[0], key[1]]) + '\n'
        verb_fd.write(row)

with open("noun_list.csv", "a", encoding="UTF-8") as noun_fd:
    for key in noun_dict:
        row = ','.join([str(noun_dict[key]), key[0], key[1]]) + '\n'
        noun_fd.write(row)

with open("adj_list.csv", "a", encoding="UTF-8") as adj_fd:
    for key in adj_dict:
        row = ','.join([str(adj_dict[key]), key[0], key[1]]) + '\n'
        adj_fd.write(row)
