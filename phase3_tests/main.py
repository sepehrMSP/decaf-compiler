import sys, getopt
from cgen_attemp import cgen


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('main.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open("out/" + outputfile, "w") as output_file:
        with open("tests/" + inputfile, "r") as input_file:
            output_file.write(cgen(''.join(input_file.readlines())))


if __name__ == "__main__":
    main(sys.argv[1:])
