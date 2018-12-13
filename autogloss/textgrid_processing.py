import os
import re
from praatio import tgio
from csv_to_db import strip_line
from db_utils import Database

SRCS = "srcs"
OUT = "out"
db = Database()


class ParseTextGrid:
    def __init__(self, srcs, out, filename):
        self.filename = filename
        self.srcs = srcs
        self.out = out

    def file_open(self):
        return tgio.openTextgrid(os.path.join(self.srcs, self.filename))

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

    def alternate_tier(self, entry_list, tier_name, tg):
        entry_tuple = [tuple(word) for word in entry_list]
        alternation = tgio.IntervalTier(name=tier_name, entryList=entry_tuple)  # массив кортежей => объект praatio
        tg.replaceTier(tier_name, alternation)
        tg.save(os.path.join(self.out, self.filename))


class FirstGlossing(ParseTextGrid):

    def __init__(self, filename, srcs, out):
        super().__init__(filename=filename, srcs=srcs, out=out)

    def gloss_bare_morph(self):
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

    def total_annotation(self):
        tg = self.file_open()
        self.alternate_tier(self.gloss_bare_morph(), "speakerid_Morph-txt-kna", tg)
        self.alternate_tier(self.add_lemma(), "speakerid_Lemma-txt-kna", tg)
        self.alternate_tier(self.add_gloss(), "speakerid_Gloss-txt-en", tg)
        self.alternate_tier(self.add_pos(), "speakerid_POS-txt-en", tg)
        print(self.filename + "has been glossed successfully!")


class Regloss(ParseTextGrid):
    def __init__(self, filename, srcs, out):
        super().__init__(filename=filename, srcs=srcs, out=out)

    def correct_morph(self):
        morph_updated = self.morph()
        for word in morph_updated:
            res = db.execute("""
            SELECT id_correct_morph FROM correction
            WHERE written_variants = %s
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

    @staticmethod
    def disambiguishing(word):
        class_marker = re.search("[1-4]", word.replace('\\', ''))
        if_be = re.search("aux|be|cop", word.replace('\\', '').lower())
        if class_marker is not None:
            class_marker = class_marker.group(0)
        if if_be is not None:
            if_be = "COP"
        else:
            if_be = "go"
        return class_marker, if_be

    def correct_gloss(self):
        glosses = self.gloss()
        morph = self.morph()
        for i in range(len(glosses)):
            class_marker, if_be = self.disambiguishing(glosses[i][2])
            res = db.execute("""
                     SELECT id_correct_morph FROM correction
                     WHERE written_variants = %s
                     """, (morph[i][2]))
            try:
                inx = res[0][0]
                res = db.execute("""
                        SELECT gloss_variants FROM glosses
                        WHERE id_correct_morph = %s
                        """, inx)
                variants = [gloss[0] for gloss in res]
                for var in variants:
                    if class_marker is not None:
                        if class_marker in var and if_be in var:
                            glosses[i][2] = var
                        elif class_marker in var and var.find("COP") == -1 \
                                and var.find("go") == -1:
                            glosses[i][2] = var
                    else:
                        glosses[i][2] = var
            except IndexError:
                pass
        return glosses

    def readd_lemma(self):
        lemma_updated = self.morph()
        for word in lemma_updated:
            res = db.execute("""
                    SELECT id_correct_morph FROM correction
                    WHERE written_variants = %s
                    """, (word[2]))
            try:
                inx = res[0][0]
                res = db.execute("""
                        SELECT lemma FROM basic_info
                        WHERE inx = %s
                        """, inx)
                word[2] = res[0][0]
            except IndexError:
                word[2] = ""
        return lemma_updated

    def readd_pos(self):
        pos = self.morph()
        for word in pos:
            res = db.execute("""
                    SELECT id_correct_morph FROM correction
                    WHERE written_variants = %s
                    """, (word[2]))
            try:
                inx = res[0][0]
                res = db.execute("""
                        SELECT POS FROM basic_info
                        WHERE inx = %s
                        """, inx)
                word[2] = res[0][0]
            except IndexError:
                word[2] = ""
        return pos

    def total_reglossing(self):
        tg = self.file_open()
        self.alternate_tier(self.correct_morph(), "speakerid_Morph-txt-kna", tg)
        self.alternate_tier(self.readd_lemma(), "speakerid_Lemma-txt-kna", tg)
        self.alternate_tier(self.correct_gloss(), "speakerid_Gloss-txt-en", tg)
        self.alternate_tier(self.readd_pos(), "speakerid_POS-txt-en", tg)
        print(self.filename + "has been reglossed successfully!")