import getopt
import sys
import sys
from os import path


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        # print('main.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            # print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open("tests/" + inputfile, "r") as input_file:
        # do stuff with input file
        tokens = token_scanner.get_tokens(input_file.read())

    with open("out/" + outputfile, "w") as output_file:
        # write result to output file. 
        result_str = ""
        for token in tokens:
            if len(token) == 1:
                result_str += str(token[0])
            else:
                result_str += "{} {}".format(token[0], token[1])
            result_str += "\n"
        output_file.write(result_str)


if __name__ == "__main__":
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import token_scanner

    main(sys.argv[1:])
