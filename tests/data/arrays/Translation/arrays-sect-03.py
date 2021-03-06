from fortran_format import *
from for2py_arrays import *

def main():
    A = Array([(1,5)])

    for i in range(1,5+1):
        A.set(i, i*i)

    fmt_obj = Format(['5(I5)'])

    sys.stdout.write(fmt_obj.write_line([A.get(1), A.get(2), A.get(3), A.get(4), A.get(5)]))

    A_subs = implied_loop_expr((lambda x:x), 2, 4, 1)
    A.set_elems(A_subs, 17)

    sys.stdout.write(fmt_obj.write_line([A.get(1), A.get(2), A.get(3), A.get(4), A.get(5)]))


main()
