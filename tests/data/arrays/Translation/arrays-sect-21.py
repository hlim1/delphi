from fortran_format import *
from for2py_arrays import *

def main():
    A = Array([(1,5),(-2,2)])

    fmt_obj_10 = Format(['5(I5)'])
    fmt_obj_11 = Format(['""'])

    A.set_elems(subscripts(A), -1)

    for i in range(1,5+1):
        sys.stdout.write(fmt_obj_10.write_line([A.get((i,-2)), A.get((i,-1)), \
                                                A.get((i,0)), A.get((i,1)), \
                                                A.get((i,2))]))
    sys.stdout.write(fmt_obj_11.write_line([]))

    start_P = A.lower_bd(1)
    stop_P = A.upper_bd(1)+1
    A_subs = idx2subs([values(3), range(start_P, stop_P, 2)])
    A.set_elems(A_subs, 555)

    for i in range(1,5+1):
        sys.stdout.write(fmt_obj_10.write_line([A.get((i,-2)), A.get((i,-1)), \
                                                A.get((i,0)), A.get((i,1)), \
                                                A.get((i,2))]))

main()
