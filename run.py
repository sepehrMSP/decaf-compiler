import os
import time
from cgen_attemp import cgen
from cgen_attemp import CodeGenerator
import symbol_table_creation_attemp
if __name__ == '__main__':
    acc = 0
    total = 0
    for file in os.listdir("phase3_tests/tests"):
        CodeGenerator.current_scope = 'root'

        symbol_table_creation_attemp.symbol_table_objects.clear()
        symbol_table_creation_attemp.class_type_objects.clear()
        symbol_table_creation_attemp.function_objects.clear()
        symbol_table_creation_attemp.symbol_table.clear()
        symbol_table_creation_attemp.class_table.clear()
        symbol_table_creation_attemp.function_table.clear()
        symbol_table_creation_attemp.stack.clear()
        symbol_table_creation_attemp.stack.append('root')
        symbol_table_creation_attemp.parent_classes.clear()
        symbol_table_creation_attemp.init()

        if file.endswith(".d"):
            test = file[:-2]

            # if 't00' in test:
            #     continue
            if 'sort' not in file:
                continue
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
