"""
    Script converting csv concordance into a mysql database
"""

import csv
import re
import os
from db_utils import Database

csv_name = "concord.csv"
db = Database()


def make_sqlite_db():
    db.execute("DROP TABLE IF EXISTS basic_info;", 0)
    db.execute("""CREATE TABLE basic_info
                (inx INTEGER PRIMARY KEY AUTOINCREMENT,
                correct_morph TEXT, 
                POS TEXT,
                lemma TEXT);
                """, 0)
    db.execute("DROP TABLE IF EXISTS correction;", 0)
    db.execute("""CREATE TABLE correction
                (id_correct_morph INTEGER,
                written_variants TEXT);
                """, 0)
    db.execute("DROP TABLE IF EXISTS glosses;", 0)
    db.execute("""CREATE TABLE glosses
                (id_correct_morph INTEGER,
                gloss_variants TEXT);
                    """, 0)
    db.execute("DROP TABLE IF EXISTS stripped;", 0)
    db.execute("""CREATE TABLE stripped
                (id_correct_morph INTEGER,
                stripped_correct_forms TEXT,
                stripped_written_variants TEXT);
                """, 0)


def strip_gloss_signs(line):
    for i in range(1, len(line) - 2):
        if 1 < i < len(line):
            if line[i] == '-' and line[i - 2] != '\\':
                line = line[:i] + line[(i + 1):]
        elif i == 1:
            if line[i] == '-' and line[i - 1] != 'i':
                line = line[:i] + line[i + 1:]
    line = re.sub('[0-9<>=./,-]', '', line)
    return line


def strip_line(line):
    line = strip_gloss_signs(line)
    return line


def info_generator(filename):
    """

    Collecting info from second to sixth columns
    of a csv concordance
    generator[0] - POS
    generator[1] - lemma
    generator[2] - morph variants
    generator[3] - correct morph
    generator[4] - gloss

    :return generator:

    """
    with open(filename, "r", encoding='UTF-8') as file:
        reader = list(csv.reader(file, delimiter=','))
        for row in reader[1:]:
            yield [row[1], row[2], row[3], row[4], row[5]]


def fill_basic_info(filename):
    print("EXECUTING BASE INFO FILLING")
    for row in info_generator(filename):
        #print(row)
        db.execute('''
        INSERT INTO basic_info
        (correct_morph, POS, lemma)
        VALUES (?, ?, ?)
        ''', [row[3], row[0], row[1]])
        db.commit()


def fill_correction(filename):
    print("FILLING CORRECTION TABLE")
    for row in info_generator(filename):
        #print(row)
        for variant in row[2].split(';'):
            res = db.execute('''
            SELECT inx FROM basic_info
            WHERE correct_morph = ?
            ''', [row[3]])
            db.execute('''
            INSERT INTO correction
            (id_correct_morph, written_variants)
            VALUES (?, ?)
            ''', [res[0][0], variant])
            db.commit()


def fill_glosses(filename):
    print("INSERTING GLOSSES")
    for row in info_generator(filename):
        #print(row)
        for variant in row[4].split('/'):
            res = db.execute('''
            SELECT inx FROM basic_info
            WHERE correct_morph = ?
            ''', [row[3]])
            db.execute('''
            INSERT INTO glosses
            (id_correct_morph, gloss_variants)
            VALUES (?, ?)
            ''', [res[0][0], variant])
            db.commit()


def fill_stripped(filename):
    print("STRIPPING VARIANTS")
    for row in info_generator(filename):
        #print(row)
        for variant in row[2].split(';'):
            res = db.execute('''
            SELECT inx FROM basic_info
            WHERE correct_morph = ?
            ''', [row[3]])
            deduplicate_check = db.execute('''
            SELECT * FROM stripped
            WHERE stripped_written_variants = ?
            ''', [strip_gloss_signs(variant)])
            if len(deduplicate_check) != 0:
                pass
            else:
                db.execute('''
                INSERT INTO stripped
                (id_correct_morph, stripped_correct_forms, stripped_written_variants)
                VALUES (?, ?, ?)
                ''', [res[0][0], strip_line(row[3]), strip_gloss_signs(variant)])
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


make_sqlite_db()
database_filling("concord.csv")


