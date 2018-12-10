import csv
import re
import os
from db_utils import Database

filename = "test_concord.csv"
db = Database()

"""
        Database contains:

        table "basic_info"
    inx | correct_morhp | POS | lemma

        table "correction"
    id_correct_morph | written_variants

        table "glosses"
    id_correct_morph | gloss_variants

        table "stripped"
    id_correct_morph | stripped_correct_forms | stripped_written_variants

"""


def resub_shortcats(line):
    line = re.sub(r'\\i-', 'ɨ', line)
    line = re.sub('\|', 'ˤ', line)
    return line


def strip_gloss_signs(line):
    for i in range(1, len(line) - 2):
        if i > 1:
            if line[i] == '-' and line[i - 2] != '\\':
                line = line[:i] + line[i + 1:]
        elif i == 1:
            if line[i] == '-' and line[i - 1] != 'i':
                line = line[:i] + line[i + 1:]
    line = re.sub('[<>=./,]', '', line)
    return line


def strip_line(line):
    line = resub_shortcats(line)
    line = strip_gloss_signs(line)
    return line


def info_generator(filename):
    """

    Collecting info from second to sixth columns
    from a csv concordance.
    generator[0] - POS
    generator[1] - lemma
    generator[2] - morph variants
    generator[3] - correct morph
    generator[4] - gloss

    :return generator:

    """
    with open(filename, "r", encoding='UTF-8') as file:
        reader = list(csv.reader(file, delimiter='\t'))
        for row in reader[1:]:
            yield [row[1], row[2], row[3], row[4], row[5]]



def fill_basic_info(filename):
    for row in info_generator(filename):
        db.execute('''
        INSERT INTO basic_info 
        (correct_morph, POS, lemma)
        VALUES (%s, %s, %s)
        ''', (row[3], row[0], row[1]))
        db.commit()


def fill_correction(filename):
    for row in info_generator(filename):
        for variant in row[2].split(';'):
            res = db.execute('''
            SELECT inx FROM basic_info
            WHERE correct_morph = %s
            ''', (row[3]))
            db.execute('''
            INSERT INTO correction 
            (id_correct_morph, written_variants)
            VALUES (%s, %s)
            ''', (res[0][0], variant))
            db.commit()


def fill_glosses(filename):
    for row in info_generator(filename):
        for variant in row[4].split('/'):
            res = db.execute('''
            SELECT inx FROM basic_info
            WHERE correct_morph = %s
            ''', (row[3]))
            db.execute('''
            INSERT INTO glosses 
            (id_correct_morph, gloss_variants)
            VALUES (%s, %s)
            ''', (res[0][0], variant))
            db.commit()


def fill_stripped(filename):
    for row in info_generator(filename):
        for variant in row[2].split(';'):
            res = db.execute('''
            SELECT inx FROM basic_info
            WHERE correct_morph = %s
            ''', (row[3]))
            db.execute('''
            INSERT INTO stripped
            (id_correct_morph, stripped_correct_forms, stripped_written_variants)
            VALUES (%s, %s, %s)
            ''', (res[0][0], strip_line(row[3]), strip_gloss_signs(variant)))
            db.commit()


def database_filling(filename):
    try:
        fill_basic_info(filename)
        fill_correction(filename)
        fill_glosses(filename)
        fill_stripped(filename)
        print("Database has been created successfully.\n")
        return 0
    except FileNotFoundError:
        print("\nThe file is not found or invalid. The process has been aborted.")
        return -1


if __name__ == "__main__":
    main()
