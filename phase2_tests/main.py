import sys, getopt
from os import path


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

    with open("tests/" + inputfile, "r") as input_file:
        code = input_file.read()

    with open("out/" + outputfile, "w") as output_file:
        output_file.write(compile_error.syntax_error(code))


if __name__ == "__main__":
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import compile_error

    main(sys.argv[1:])
