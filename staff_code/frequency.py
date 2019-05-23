from praatio import tgio
from collections import Counter
import re


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


class CountingTG(ParseTextGrid):
    def count_nouns(self):
        nouns = Counter()
        morph_layer = self.morph()
        gloss_layer = self.gloss()
        pos_layer = self.pos()
        for i in range(len(morph_layer)):
            if pos_layer[i] == 'n':
                noun = re.sub("[,.!\"/]", "", morph_layer[i])
                nouns.update([(noun, gloss_layer[i])])
        return dict(nouns)

    def count_verbs(self):
        verbs = Counter()
        morph_layer = self.morph()
        gloss_layer = self.gloss()
        pos_layer = self.pos()
        for i in range(len(morph_layer)):
            if pos_layer[i] == "vb":
                print(morph_layer[i])
                print(pos_layer[i], pos_layer[i + 1])
        #    if pos_layer[i] == 'n':
        #        noun = re.sub("[,.!\"/]", "", morph_layer[i])
        #        nouns.update([(noun, gloss_layer[i])])
        #return dict(nouns)


CT = CountingTG("srcs/Magomedshapi_Nina_glossed_23_07latin.TextGrid")
CT.count_verbs()

