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

    def comment(self):
        tg = self.file_open()
        comment_tier = tg.tierDict["com@speakerid"]
        comment_list = [list(word) for word in comment_tier.entryList]
        return comment_list


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
        morph_line = re.sub("<l>", "&lt;l&gt;", morph_line)
        morph_line = re.sub("<p>", "&lt;p&gt;", morph_line)
        gloss_line = re.sub("<HPL>", "&lt;HPL&gt;", gloss_line)
        gloss_line = re.sub("<APL>", "&lt;APL&gt;", gloss_line)
        gloss_line = re.sub("<PFV>", "&lt;PFV&gt;", gloss_line)
        gloss_line = re.sub("<IPFV>", "&lt;IPFV&gt;", gloss_line)
        return morph_line, gloss_line

    def make_line(self):
        lines = []
        morph = self.morph()
        gloss = self.gloss()
        translation = self.translation()
        comments = self.comment()
        idxs = self.sent_start_end(morph)
        max = 9
        for i, sentence in enumerate(idxs):
            morph_line = "<tr>"
            gloss_line = "<tr>"
            try:
                comment = comments[i][2]
            except IndexError:
                comment = "No comments (yet?)"
            morph_line += "<td><button title=\"" + comment + "\">" + str(i + 1) + "</button>&nbsp;&nbsp;</td>"
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
                    lines.append((morph_line, gloss_line, None))
                    morph_line = "<tr>"
                    gloss_line = "<tr>"
                    max = 9
            trans_line = translation[i][2]
            morph_line, gloss_line = self.remove_tags(morph_line, gloss_line)
            morph_line += "</tr>"
            gloss_line += "</tr>"
            lines.append((morph_line, gloss_line, trans_line))
            max = 9
        return lines

"""
Starting html construction

"""


def write_html_header(func):
    @wraps(func)
    def wrapper():
        header = """ <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        <!-- Bootstrap CSS -->
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
            margin-top: 1em; /* Отступ сверху */
            margin-bottom: 1em; /* Отступ снизу */
        }
        button {
        background: #f2f6f8; /* Цвет фона */
        border: 1px solid #7a7b7e; /* Параметры рамки */
        width: 30px; /* Ширина кнопки */
        height: 30px; /* Высота */
        border-radius: 30px;
        }
        </style>
        </head>
        <body>
        <header>
        <nav class="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
        <a class="navbar-brand" href="#">TextHeap</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse">
            <ul class="navbar-nav mr-auto">
                <li class="nav-item active">
            <a class="nav-link" href="https://docs.google.com/document/d/1e6h5VuzIcmOReMrymZkL0fXUplUVBJjh7MiPk6-SHbM/edit#">Glosses <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item active">
            <a class="nav-link" href="https://docs.google.com/spreadsheets/d/1kv4-pqEpxgJKTkUa6OS2GKGBHvmfkWOpEgAlDDelOKE/edit#gid=13644142">Dicts</a>
            </li>
            <li class="nav-item active">
            <a class="nav-link" href="https://drive.google.com/open?id=1z2tRkpzAinz31FfOb3ROwC1vfTDn3s7L" tabindex="-1" aria-disabled="true">TextGrids</a>
            </li>
            <li class="nav-item">
            <a class="nav-link disabled" href="#" tabindex="-1" aria-disabled="true">Audio</a>
            </li>
        </ul>
        </div>
        </nav>
        </header>
        <br>
        <br>
        """
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write(header)
        html.close()
        func()
        bottom = """
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
        </body>
        </html>
        """
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write(bottom)
        html.close()
    return wrapper


@write_html_header
def put_texts():
    for filename in os.listdir("srcs"):
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write("""<nav class="navbar navbar-expand-lg navbar-light bg-light rounded"><div class="collapse navbar-collapse justify-content-md-center" id="navbarsExample10">
      <ul class="navbar-nav"><li class="nav-item active"><a class="nav-link" href="#"><h2><b>"""
                       + filename.split('.')[0])
            html.write("""\n</b></h2><span class="sr-only">(current)</span></a></li></ul></div></nav>""")
            html.close()
        print(filename)
        parser = MakeGlossLine(os.path.join("srcs", filename))
        for el in parser.make_line():
            with open("text_heap.html", 'a', encoding="UTF-8") as html:
                html.write("<table class=\"example\">\n" + el[0] + '\n' + el[1] + '\n' + "</table>")
                if el[2] is not None:
                    html.write("\n\n<i><p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\' " + el[2] + " \'</p></i><hr>\n\n")
            html.close()
        with open("text_heap.html", 'a', encoding="UTF-8") as html:
            html.write("""<br><br><br>""")
            html.close()


def main():
    try:
        os.remove("text_heap.html")
    except Exception:
        pass
    put_texts()
    print("\nКолчество лексем в копрусе: " + str(LEXEMES))


if __name__ == "__main__":
    main()
