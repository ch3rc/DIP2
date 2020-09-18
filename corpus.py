import getopt
import sys
import os


def help():
    print("\t\t-----HELP-----\n\n")
    print("-g, --gray, convert the images to gray scale\n")
    print("-r, --rows, change the number of rows (default: 480)\n")
    print("-c, --columns, change the number of columns (default: 640)\n")
    print("-t, --type, save the picture as this new type\n")
    print("provide a directory to get photos from\n")
    print("specify the name of the directory you would like it to go to\n")
    print("default output directory is indir.corpus\n")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hgr:c:t:", ["help", "gray", "rows", "columns", "type"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(1)

    indir = os.getcwd()
    outdir = "indir.corpus"
    type_file = None
    rows = 480
    columns = 640
    gray_scale = 0
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit(1)
        elif o in ("-g", "--gray"):
            gray_scale = 1
        elif o in ("-r", "--rows"):
            rows = a
        elif o in ("-c", "--columns"):
            columns = a
        elif o in ("-t", "--type"):
            type_file = a
        else:
            assert False, "unhandled option"

    for i, arg in enumerate(args):
        if i == 0:
            indir = arg
        if i == 1:
            outdir = arg


if __name__ == "__main__":
    main()