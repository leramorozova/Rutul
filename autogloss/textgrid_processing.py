import os
import re
from praatio import tgio
from csv_to_db import strip_line
from db_utils import Database

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
    def __init__(self, srcs, out, filename):
        super().__init__(srcs=srcs, out=out, filename=filename)

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
                word[2] = ""
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
                word[2] = ""
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
                word[2] = ""
        return pos

    def total_annotation(self):
        tg = self.file_open()
        self.alternate_tier(self.gloss_bare_morph(), "speakerid_Morph-txt-kna", tg)
        self.alternate_tier(self.add_lemma(), "speakerid_Lemma-txt-kna", tg)
        self.alternate_tier(self.add_gloss(), "speakerid_Gloss-txt-en", tg)
        self.alternate_tier(self.add_pos(), "speakerid_POS-txt-en", tg)
        print(self.filename + " has been glossed successfully!")


class Regloss(ParseTextGrid):
    def __init__(self, srcs, out, filename):
        super().__init__(srcs=srcs, out=out, filename=filename)

    @staticmethod
    def define_punctuation(morph):
        punct = None
        if_punct = re.search("(\.\.\.)|//|[(\.),?!/]", morph)
        if if_punct is not None:
            punct = if_punct.group(0)
            morph = morph[:-len(punct)]
        return morph, punct

    def correct_morph(self):
        morph_updated = self.morph()
        for word in morph_updated:
            word[2], punct = self.define_punctuation(word[2])
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
            if punct is not None:
                word[2] += punct
        return morph_updated

    @staticmethod
    def disambiguate(variants, old_gloss):
        """
        The function removes homonymy variants
        :param variants: array of glossing variants
               old_gloss: gloss from TG file
        :return: the only correct disambiguished variant
        """
        if len(variants) == 1:
            return variants[0]
        old_gloss = old_gloss.replace('\\', '').lower()
        class_marker = re.search("[1-4]|hpl|npl|apl", old_gloss)
        if_be = re.search("aux|be|cop1", old_gloss)
        if_go = re.search("go", old_gloss)
        if class_marker is not None:
            class_marker = class_marker.group(0)
        for var in variants:
            if class_marker is not None:
                if if_be is not None:
                    if_be = "COP"
                    if class_marker in var and if_be in var:
                        return var
                elif if_go is not None:
                    if_go = "go"
                    if class_marker in var and if_go in var:
                        return var
                elif "force" in old_gloss and "force" in var and class_marker in var:
                    return var
                elif "see" in old_gloss and "see" in var and class_marker in var:
                    return var
                else:
                    if class_marker in var:
                        return var
            elif "you" in old_gloss:
                if "sg" in old_gloss and "sg" in var:
                    return var
                elif "pl" in old_gloss and "pl" in var:
                    return var
            elif "name" in old_gloss and "name" in var:
                return var
            elif "spoon" in old_gloss and "spoon" in var:
                return var

        return variants

    def correct_gloss(self):
        glosses = self.gloss()
        morph = self.morph()
        for i in range(len(glosses)):
            morph[i][2], punct = self.define_punctuation(morph[i][2])
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
                #glosses[i][2] = disambiguate(variants)
                print(self.disambiguate(variants, glosses[i][2]))
            except IndexError:
                pass
        return glosses

    def readd_lemma(self):
        lemma_updated = self.morph()
        for word in lemma_updated:
            word[2], punct = self.define_punctuation(word[2])
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
            word[2], punct = self.define_punctuation(word[2])
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
        print(self.s + " has been reglossed successfully!")


reg = Regloss("srcs", "out", "test_regloss.TextGrid")
reg.correct_gloss()
