#!/usr/bin/env python3

"""
    File: ftnfmt.py
    Purpose: Process a string (obtained from a data file) according to
             a Fortran FORMAT.

             Currently the only formats supported are I, F, and X.  This
             should be extended as necessary.

    Usage: Given a Fortran READ statement with a list of variables VARS
           that should be read according to a format list fmt_list
           (where fmt_list is a Python list of Fortran FORMAT descriptors),
           do the following:

           (1) Create a FtnFmt object as follows:

                   my_fmt_obj = FtnFmt(fmt_list)

           (2) To process a line of input inp_ln according to this format 
               and assign values to a tuple of variables var_list:

                   var_list = my_fmt_obj.match_line(inp_ln)

           There are some examples towards the end of this file.
"""

import re, sys

class FtnFmt:
    def __init__(self, format_list):
        regexp_str = ''.join(self.mk_re_list(format_list))
        self._re = re.compile(regexp_str)
        self._regexp_str = regexp_str

    def match_line(self, line):
        match = self._re.match(line)
        assert match != None, "Format mismatch (line = {})".format(line)

        # this code uses a very simple heuristic to decide whether to
        # compute an int or float value: if the string matched in the
        # input contains '.' it computes a float, otherwise an int.
        matched_values = []
        for i in range(self._re.groups):
            n = i+1
            match_str = match.group(n)
            if '.' in match_str:
                val = float(match_str)
            else:
                val = int(match_str)

            matched_values.append(val)

        return tuple(matched_values)            


    def __str__(self):
        return self._regexp_str
        
    # given a list of Fortran format specifiers, e.g., ['I5', '2X', 'F4.1'],
    # mk_re_list() constructs a regular expression for matching a string
    # against that sequence of format specifiers.  
    def mk_re_list(self, fmt_list):
        rexp_list = []
        for fmt in fmt_list:
            rexp_list.extend(self.mk_re(fmt))
    
        return rexp_list

    
    # given a single format specifier, e.g., '2X', 'I5', etc., mk_re() 
    # constructs a regular expression for matching a string against that 
    # specifier.  
    def mk_re(self, fmt):
        # first, remove any surrounding space 
        fmt = fmt.strip()
    
        # get any leading digits indicating repetition
        match = re.match('(\d+)(.+)', fmt)
        if match == None:
            reps = 1
        else:
            reps = int(match.group(1))
            fmt = match.group(2)
    
        if fmt[0] == '(':        # process parenthesized format list recursively
            fmt = fmt[1:-1]
            fmt_list = fmt.split(',')
            rexp = self.mk_re_list(fmt_list)
        else:
            if fmt[0] == 'I':                 # integer 
                sz = fmt[1:]
                rexp = ['(\d{' + sz + '})']
                rexp_pair = (rexp, 1)
            elif fmt[0] == 'X':               # skip
                sz = 1
                rexp = [' ']
            elif fmt[0] == 'F':               # floating point
                idx0 = fmt.find('.')
                sz = fmt[1:idx0]
                rexp = ['([0-9. ]{' + sz + '})']
            else:
                print('ERROR: Unrecognized format specifier ' + fmt)
                sys.exit(1)
    
        # replicate the regular expression by the repetition factor in the format
        rexp *= reps
    
        return rexp

################################################################################
#                                                                              #
#                                 EXAMPLE USAGE                                #
#                                                                              #
################################################################################

def main():

    ################################# EXAMPLE 1 ################################
    # Format from read statement in the file Weather.for
    # The relevant Fortran code is:
    #
    #         OPEN (4,FILE='WEATHER.INP',STATUS='UNKNOWN')  
    #         ...
    #         READ(4,20) DATE,SRAD,TMAX,TMIN,RAIN,PAR
    #   20   FORMAT(I5,2X,F4.1,2X,F4.1,2X,F4.1,F6.1,14X,F4.1)
    #
    # The line of data shown (input1) is taken from the file WEATHER.INP

    format1 = ['I5','2X','F4.1','2X','F4.1','2X','F4.1','F6.1','14X','F4.1']
    input1 = '87001   5.1  20.0   4.4  23.9              10.7 '

    rexp1 = FtnFmt(format1)
    (DATE, SRAD, TMAX, TMIN, RAIN, PAR) = rexp1.match_line(input1)

    print("FORMAT: {}".format(format1))
    print("regexp_str = \"{}\"".format(rexp1))

    vars1 = (DATE, SRAD, TMAX, TMIN, RAIN, PAR)
    print("vars1 = {}".format(vars1))
    print("")

    ################################# EXAMPLE 2 ################################
    # Format based on a read statement in the file Plant.for
    # The relevant Fortran code is:
    #        OPEN (2,FILE='PLANT.INP',STATUS='UNKNOWN')
    #        ...
    #        READ(2,10) Lfmax, EMP2,EMP1,PD,nb,rm,fc,tb,intot,n,lai,w,wr,wc
    #     &     ,p1,sla
    #   10   FORMAT(17(1X,F7.4))
    #
    # The line of data shown (input2) is taken from the file PLANT.INP

    format2 = ['3(1X,F7.4)']
    input2 = '    12.0    0.64   0.104'

    rexp2 = FtnFmt(format2)
    (Lfmax, EMP2, EMP1) = rexp2.match_line(input2)

    print("FORMAT: {}".format(format2))
    print("regexp_str = \"{}\"".format(rexp2))

    vars2 = (Lfmax, EMP2, EMP1)
    print("vars2 = {}".format(vars2))
    print("")


if __name__ == "__main__":
    main()

