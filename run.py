import os
import time

from cgen_attemp import cgen

if __name__ == '__main__':
    acc = 0
    total = 0
    for file in os.listdir("phase3_tests/tests"):
        if file.endswith(".d"):
            test = file[:-2]
            if 'expr' not in test:
                continue
            # if 'hard' not in test:
            #     continue
            total += 1
            print('Test_{}: {}'.format(total, file))
            with open("phase3_tests/tests/" + file, "r") as f:
                decaf = ''.join(f.readlines())
            with open("phase3_tests/out/" + test + ".asm", "w") as f:
                f.write(cgen(decaf))
            asm = "phase3_tests/out/" + test + ".asm"
            inp = 'phase3_tests/tests/' + test + '.in'
            out = 'phase3_tests/tests/' + test + '.out'
            os.system('spim -a -f "{}" < {} > "tmp"'.format(asm, inp))
            with open ("tmp", "r") as f:
                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()
                res = ''.join(f.readlines())
            with open(out) as f:
                cor = ''.join(f.readlines())
            # print(res)
            # print()
            # print(cor)
            if res == cor:
                print('Accepted')
                acc += 1
            else:
                print(res)
                print()
                print(cor)
                print('Wrong')
        # exit(0)
        # time.sleep(1)
    print('Passed {} from {} tests'.format(acc, total))
