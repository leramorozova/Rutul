from textgrid_processing import FirstGlossing, Regloss
from csv_to_db import database_filling
import os


def main():
    print("\n\tRutul Autogloss is running...\n\tPress ctrl+z to leave the process\n")
    db_update = input("Do you need to create new database? [yes/no] ")
    if db_update == "yes":
        print("\nThe current directory is: " + os.getcwd())
        filename = input("Enter the path to your csv... ")
        ret = database_filling(filename)
        if ret < 0:
            return 0
    elif db_update == "no":
        pass
    else:
        print("\nIncorrect input. The process has been aborted.")
        return 0
    action = input(''' Enter the number of operation:\n"
                   "1. Make full reannotations in given textgrids (preferable if they hasn't been annotated before)\n
                    2. Regloss annotated textgrids (that will allow to disambigiuate annotation\n
                    3. Finish the process\n''')
    if action == '1':
        pass
    elif action == '2':
        pass
    elif action == '3':
        print("\nThe process has been finished!")
    else:
        print("\nIncorrect input. The process has been aborted.")
        return 0


if __name__ == "__main__":
    main()
