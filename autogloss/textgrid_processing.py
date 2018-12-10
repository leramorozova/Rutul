import os
from praatio import tgio
from csv_to_db import strip_line
from db_utils import Database

FLAG = 'FIRST'
SRCS = "srcs"
OUT = "out"
db = Database()


class ParseTextGrid:
    """
    :return [...
        Interval(start, end, label),
        ...]
    """
    def __init__(self, filename):
        self.filename = filename
        self.tg = tgio.openTextgrid(os.path.join(SRCS, filename))

    def morph(self):
        morph_tier = self.tg.tierDict["speakerid_Morph-txt-kna"]
        morph_list = [list(word) for word in morph_tier.entryList]
        return morph_list

    def lemma(self):
        lemma_tier = self.tg.tierDict["speakerid_Lemma-txt-kna"]
        lemma_list = [list(word) for word in lemma_tier.entryList]
        return lemma_list

    def gloss(self):
        gloss_tier = self.tg.tierDict["speakerid_Gloss-txt-en"]
        gloss_list = [list(word) for word in gloss_tier.entryList]
        return gloss_list

    def pos(self):
        pos_tier = self.tg.tierDict["speakerid_POS-txt-en"]
        pos_list = [list(word) for word in pos_tier.entryList]
        return pos_list

    def alternate_tier(self, entry_list, tier_name):
        entry_tuple = [tuple(word) for word in entry_list]
        alternation = tgio.IntervalTier(name=tier_name, entryList=entry_tuple)  # массив кортежей => объект praatio
        self.tg.replaceTier(tier_name, alternation)
        self.tg.save(os.path.join(OUT, self.filename))


class FirstGlossing(ParseTextGrid):

    def __init__(self, filename):
        super().__init__(filename=filename)

    def gloss_morph(self):
        morph_updated = self.morph()
        for word in morph_updated:
            res = db.execute("""
            SELECT id_correct_morph FROM stripped
            WHERE stripped_written_variants = %s
            """, (word[2]))
            try:
                inx = res[0][0]
                res = db.execute("""
                SELECT correct_morph FROM basic_info
                WHERE inx = %s
                """, inx)
                word[2] = res[0][0]
            except IndexError:
                pass
        return morph_updated

    def add_lemma(self):
        lemma_updated = self.morph()
        for word in lemma_updated:
            res = db.execute("""
                    SELECT id_correct_morph FROM stripped
                    WHERE stripped_written_variants = %s
                    """, (word[2]))
            try:
                inx = res[0][0]
                res = db.execute("""
                        SELECT lemma FROM basic_info
                        WHERE inx = %s
                        """, inx)
                word[2] = res[0][0]
            except IndexError:
                pass
        return lemma_updated

    def add_gloss(self):
        glosses = self.morph()
        for word in glosses:
            res = db.execute("""
                    SELECT id_correct_morph FROM stripped
                    WHERE stripped_written_variants = %s
                    """, (word[2]))
            try:
                inx = res[0][0]
                res = db.execute("""
                        SELECT gloss_variants FROM glosses
                        WHERE id_correct_morph = %s
                        """, inx)
                variants = [gloss[0] for gloss in res]
                word[2] = '/'.join(variants)
            except IndexError:
                pass
        return glosses

    def add_pos(self):
        pos = self.morph()
        for word in pos:
            res = db.execute("""
                    SELECT id_correct_morph FROM stripped
                    WHERE stripped_written_variants = %s
                    """, (word[2]))
            try:
                inx = res[0][0]
                res = db.execute("""
                        SELECT POS FROM basic_info
                        WHERE inx = %s
                        """, inx)
                word[2] = res[0][0]
            except IndexError:
                pass
        return pos

#ГДЕ-ТО ТУТ ГОНЕВО, ВОЗМОЖНО, НАДО ДЕЛАТЬ SAVE TG или перевызывать класс
    def total_annotation(self):
        self.alternate_tier(self.gloss_morph(), "speakerid_Morph-txt-kna")
        self.alternate_tier(self.add_lemma(), "speakerid_Lemma-txt-kna")
        self.alternate_tier(self.add_gloss(), "speakerid_Gloss-txt-en")
        self.alternate_tier(self.add_pos(), "speakerid_POS-txt-en")


class Regloss(ParseTextGrid):
    def __init__(self, filename):
        super().__init__(filename=filename)


def test_praatio():
    print(tg.tierNameList)

    tier = tg.tierDict["speakerid_Morph-txt-kna"]

    print(tier.entryList)

    for el in tier.entryList:
        print(str(el.start) + '\t' + str(el.end) + '\t' + el.label)

    newTG = tg.new()
    newTier = tier.new()

    # если всунуть массив с новыми данными, получится ли новый текстгрид? навряд ли
    emptiedTier = tier.new(entryList=[])

    #НЕТ, МОЖНО, только надо tulpe

    # We've already seen how to add a new tier to a TextGrid
    # Here we add a new tier, 'utterance', which has one entry that spans the length of the textgrid
    utteranceTier = tgio.IntervalTier(name='utterance', entryList=[('0', tg.maxTimestamp, 'mary rolled the barrel'), ],
                                  minT=0, maxT=tg.maxTimestamp)
    tg.addTier(utteranceTier)
    print(tg.tierNameList)


if __name__ == "__main__":
    if FLAG == 'FIRST':
        parse = FirstGlossing("test_firstgloss.TextGrid")
        print(parse.add_gloss())