from praatio import tgio
from functools import wraps
import re
import os

"""
В поле лосс не должно быть пустых мест.
Границы крайних форм должны совпадать с границами предложений.

"""

LEXEMES = 0


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

    @staticmethod
    def remove_tags(morph_line, gloss_line):
        morph_line = re.sub("<b>", "&lt;b&gt;", morph_line)
        morph_line = re.sub("<w>", "&lt;w&gt;", morph_line)
        morph_line = re.sub("<r>", "&lt;r&gt;", morph_line)
        morph_line = re.sub("<d>", "&lt;d&gt;", morph_line)
        morph_line = re.sub("<t>", "&lt;t&gt;", morph_line)
        gloss_line = re.sub("<HPL>", "&lt;HPL&gt;", gloss_line)
        gloss_line = re.sub("<APL>", "&lt;APL&gt;", gloss_line)
        return morph_line, gloss_line

    def make_line(self):
        lines = []
        morph = self.morph()
        gloss = self.gloss()
        idxs = self.sent_start_end(morph)
        max = 9
        for i, sentence in enumerate(idxs):
            morph_line = "<tr>"
            gloss_line = "<tr>"
            morph_line += "<td>(" + str(i + 1) + ") </td>"
            gloss_line += "<td>" + ' ' * len(str(i + 2)) + "</td>"
            start_idx = sentence[0]
            end_idx = sentence[1]
            while max > 0 and start_idx != end_idx + 1:
                global LEXEMES
                LEXEMES += 1
                morph_line += "<td>" + morph[start_idx][2] + "   </td>"
                gloss_line += "<td>" + gloss[start_idx][2] + "   </td>"
                start_idx += 1
                max -= 1
                if max == 0:
                    morph_line, gloss_line = self.remove_tags(morph_line, gloss_line)
                    morph_line += "</tr>"
                    gloss_line += "</tr>"
                    lines.append((morph_line, gloss_line))
                    morph_line = "<tr>"
                    gloss_line = "<tr>"
                    max = 9
            morph_line, gloss_line = self.remove_tags(morph_line, gloss_line)
            morph_line += "</tr>"
            gloss_line += "</tr>"
            lines.append((morph_line, gloss_line))
            max = 9
        return lines

    def translation_block(self):
        block = ''
        morph = self.morph()
        translation = self.translation()
        idxs = self.sent_start_end(morph)
        i = 1
        for el in idxs:
            start = morph[el[0]][0]
            for sent in translation:
                if sent[0] == start:
                    block += '(' + str(i) + ') '
                    block += sent[2].capitalize()
                    if sent[2][-1] in ',.?!/:':
                        pass
                    else:
                        block += '.'
                    block += '<br> '
                    i += 1
        return block

"""
Starting html construction

"""


def write_html_header(func):
    @wraps(func)
    def wrapper(filename):
        header = """ <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8" />
        <title>Свалка рутульских текстов</title>
        <style type="text/css">
        body {
            padding: 40px;
            line-height: 1.5;
        }
        .example {
            padding: 1px; /* Поля */
            white-space: pre;
            }
        p {
            width: 80%;
            border: 1px solid black;
            padding: 10px;
        }
        </style>
        </head>
        <body>
        """
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write(header)
        html.close()
        func(filename)
        bottom = """
        </body>
        </html>
        """
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write(bottom)
        html.close()
    return wrapper


@write_html_header
def put_texts(filename):
    with open("text_heap.html", 'a', encoding="UTF-8") as html:
        html.write("<center><b><caption><font size=\"5\"> \n" + filename.split('.')[0])
        html.write("\n</font></center></b></caption><br>")
        html.close()
    print(filename)
    parser = MakeGlossLine(os.path.join("srcs", filename))
    for el in parser.make_line():
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write("<table class=\"example\">\n" + el[0] + '\n' + el[1] + '\n' + "</table>")
        html.close()
    with open("text_heap.html", 'a', encoding="UTF-8") as html:
        html.write("<p>\n" + parser.translation_block() + "</p><br><br>")
        html.close()


def main():
    try:
        os.remove("text_heap.html")
    except Exception:
        pass
    for tg in os.listdir("srcs"):
        put_texts(tg)
    print("\nКолчество лексем в копрусе: " + str(LEXEMES))


if __name__ == "__main__":
    main()
