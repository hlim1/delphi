from fortran_format import *
from for2py_arrays import *

def main():
    arr = Array([(1,10)])

    arr_subs = subscripts(arr)
    arr.set_elems(arr_subs, [11,22,33,44,55,66,77,88,99,110])

    fmt_obj = Format(['I5'])

    for i in range(1,10+1):
        val = arr.get((i,))
        sys.stdout.write(fmt_obj.write_line([val]))

main()
