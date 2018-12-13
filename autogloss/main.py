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
    action = input('''\nEnter the number of operation:
    1. Make full reannotations in given textgrids (preferable if they hasn't been annotated before)
    2. Regloss annotated textgrids (that will allow to disambigiuate annotation
    3. Finish the process''')
    if action == '1':
        print(''' Please, make sure, that your textgrigs are splitted by words properly.\n 
    Enter the root to a dir, where your textrigs are: \n''')
        try:
            srcs = input()
            print("Enter the root to an output dir (it should be another one, otherwise your files will be rewrited.")
            out = input()
            print("\nSource directory is " + os.path.abspath(srcs))
            print("Output directory is " + os.path.abspath(out))
            files = os.listdir(srcs)
            for file in files:
                parse = FirstGlossing(file, srcs, out)
                parse.total_annotation()
            return print("\nFinish!")
        except FileNotFoundError:
            print("\nIncorrect input. The process has been aborted.")
        return 0
    elif action == '2':
        print(''' Please, make sure, that your textgrigs are splitted by words properly.\n 
            Enter the root to a dir, where your textrigs are: \n''')
        try:
            srcs = input()
            print("Enter the root to an output dir (it should be another one, otherwise your files will be rewrited.")
            out = input()
            print("\nSource directory is " + os.path.abspath(srcs))
            print("Output directory is " + os.path.abspath(out) + '\n')
            files = os.listdir(srcs)
            for file in files:
                parse = Regloss(file, srcs, out)
                parse.total_reglossing()
            return print("\nFinish!")
        except FileNotFoundError:
            print("\nIncorrect input. The process has been aborted.")
        return 0
    elif action == '3':
        print("\nThe process has been finished!")
    else:
        print("\nIncorrect input. The process has been aborted.")
        return 0


if __name__ == "__main__":
    main()
