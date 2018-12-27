from praatio import tgio
from functools import wraps
import os


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

    def translation(self):
        tg = self.file_open()
        translation_tier = tg.tierDict["ft@speakerid-txt-kna"]
        translation_list = [list(word) for word in translation_tier.entryList]
        return translation_list


class MakeGlossLine(ParseTextGrid):
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

    def make_line(self):
        morph = self.morph()
        gloss = self.gloss()
        idxs = self.sent_start_end(morph)
        for i, sentence in enumerate(idxs):
            morph_line = ''
            gloss_line = ''
            len_gloss_line = 0
            len_morph_line = 0
            morph_line += str(i + 1) + ') '
            gloss_line += ' ' * (2 + len(str(i + 1)))
            len_gloss_line += 2 + len(str(i + 1))
            len_morph_line += 2 + len(str(i + 1))
            start_idx = sentence[0]
            end_idx = sentence[1]
            while start_idx != end_idx + 1:
                morph_line += morph[start_idx][2]
                gloss_line += gloss[start_idx][2]
                len_morph_line += len(morph[start_idx][2])
                len_gloss_line += len(gloss[start_idx][2])
                if len_morph_line > len_gloss_line:
                    morph_line += '\t'
                    if len(morph[start_idx][2]) % 4 != 0:
                        flag = 4 - len(morph[start_idx][2]) % 4
                    else:
                        flag = 4
                    len_morph_line += flag
                    while len_morph_line > len_gloss_line:
                        gloss_line += '\t'
                        if gloss_line[-2] != '\t':
                            len_gloss_line += (4 - len_gloss_line % 4)
                        else:
                            len_gloss_line += 4
                else:
                    gloss_line += '\t'
                    if len(gloss[start_idx][2]) % 4 != 0:
                        flag = 4 - len(gloss[start_idx][2]) % 4
                    else:
                        flag = 4
                    len_gloss_line += flag
                    while len_gloss_line > len_morph_line:
                        morph_line += '\t'
                        if morph_line[-2] != '\t':
                            len_morph_line += (4 - len_morph_line % 4)
                        else:
                            len_morph_line += 4
                start_idx += 1
            yield (morph_line, gloss_line)

    def translation_block(self):
        pass


def write_html_header(func):
    @wraps(func)
    def wrapper():
        header = """ <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8" />
        <title>Свалка рутульских текстов</title>
        <style type="text/css">
        div {
            width: 100%; /* Ширина */
            background: #fc0; /* Цвет фона */
            padding: 20px; /* Поля */
            -moz-box-sizing: border-box; /* Для Firefox */
            -webkit-box-sizing: border-box; /* Для Safari и Chrome */
            box-sizing: border-box; /* Для IE и Opera */
            }
        </style>
        </head>
        <body>
        """
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write(header)
        html.close()
        func()
        bottom = """</body>
        </html>
        """
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write(bottom)
        html.close()
    return wrapper


@write_html_header
def fuck():
    header = "FUUUUUUUUCK"
    with open("text_heap.html", 'a', encoding="UTF-8") as html:
        html.write(header)
    html.close()




parser = MakeGlossLine(os.path.join("srcs", "180722_0090.TextGrid"))
parser.translation_block()