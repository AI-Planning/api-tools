import os, sys

if __name__ == "__main__":
    os.system("python ../planning.domains.py find domains {}".format(str(sys.argv[1])))