import csv
import db_utils as db

FILENAME = "test_concord.csv"


def get_info():
    with open(FILENAME, "r", encoding='UTF-8') as file:
        reader = list(csv.reader(file, delimiter='\t'))
        for row in reader[1:]:
            yield [row[1], row[2], row[3], row[4], row[5]]


if __name__ == "__main__":
    get_info()
