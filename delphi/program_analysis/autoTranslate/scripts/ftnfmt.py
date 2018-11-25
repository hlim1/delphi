#!/usr/bin/env python3

"""
    File: ftnfmt.py
    Purpose: Process a string (obtained from a data file) according to
             a Fortran FORMAT.

             Currently the only formats supported are I, F, and X.  This
             should be extended as necessary.

    Usage: Given a Fortran READ or WRITE statement that should be processed 
           according to a format list fmt_list (where fmt_list is a Python
           list of Fortran FORMAT descriptors), do the following:

           (1) Create a Format object as follows:

                   my_fmt_obj = Format(fmt_list)

           (2) INPUT: To process a line of input inp_ln according to this 
               format and assign values to a tuple of variables var_list:

                   var_list = my_fmt_obj.read_line(inp_ln)

               OUTPUT: To construct a line to be printed out given a set 
               of values val1, ..., valN:

                   out_string = my_fmt_obj.write_line([val1, ..., valN])

           There are some examples towards the end of this file.
"""

import re, sys

class Format:
    def __init__(self, format_list):
        self._format_list = format_list.copy()
        self._read_line_init = False
        self._write_line_init = False

        self._re_cvt =     None
        self._regexp_str = None
        self._re =         None
        self._match_exps = None
        self._divisors =   None
        self._in_cvt_fns = None

        self._output_fmt = None
        # self._out_gen_fmt = None
        self._out_cvt_fns = None


    def init_read_line(self):
        format_list = self._format_list
        self._re_cvt = self.match_input_fmt(format_list)
        regexp0_str = ''.join([subs[0] for subs in self._re_cvt])
        self._regexp_str = regexp0_str
        self._re = re.compile(regexp0_str)
        self._match_exps = [subs[1] for subs in self._re_cvt if subs[1] != None]
        self._divisors = [subs[2] for subs in self._re_cvt if subs[2] != None]
        self._in_cvt_fns = [subs[3] for subs in self._re_cvt if subs[3] != None]
        self._read_line_init = True


    def init_write_line(self):
        format_list = self._format_list
        output_info = self.gen_output_fmt(format_list)
        self._output_fmt = ''.join([sub[0] for sub in output_info])
        # self._out_gen_fmt = [sub[1] for sub in output_info if sub[1] != None]
        self._out_widths  = [sub[2] for sub in output_info if sub[2] != None]
        self._out_cvt_fns = [sub[3] for sub in output_info if sub[3] != None]


    def read_line(self, line):
        if not self._read_line_init:
            self.init_read_line()

        match = self._re.match(line)
        assert match != None, "Format mismatch (line = {})".format(line)

        matched_values = []
        for i in range(self._re.groups):
            cvt_re = self._match_exps[i]
            cvt_div = self._divisors[i]
            cvt_fn = self._in_cvt_fns[i]
            match_str = match.group(i+1)

            match0 = re.match(cvt_re, match_str)
            if match0 != None:
                if cvt_fn == 'float':
                    if '.' in match_str:
                        val = float(match_str)
                    else:
                        val = int(match_str)/cvt_div
                elif cvt_fn == 'int':
                    val = int(match_str)
                else:
                    sys.stderr.write('unrecognized conversion function: {}\n'.format(cvt_fn))
            else:
                sys.stderr.write('format conversion failed: {}\n'.format(match_str))

            matched_values.append(val)

        return tuple(matched_values)            


    def write_line(self, values):
        if not self._write_line_init:
            self.init_write_line()
    
        out_strs = []
        for i in range(len(self._out_widths)):
            # out_fmt = self._out_gen_fmt[i]
            out_cvt_fn = self._out_cvt_fns[i]
            if out_cvt_fn == 'int':
                out_val = self.cvt_I(self._out_widths[i], values[i])
            elif out_cvt_fn == 'float':
                out_val = self.cvt_F(self._out_widths[i], values[i])
            else:
                sys.stderr.write('unrecognized conversion function: {}\n'.format(out_cvt_fn))
                out_val = "????"

            out_strs.append(out_val)
    
        out_str_exp = '"' + self._output_fmt + '".format' + str(tuple(out_strs))
        return eval(out_str_exp) 
        
            

    def cvt_I(self, width, value):
        if len(str(value)) > width:
            return '*' * width
    
        fmt = '{:' + str(width) + 'd}'
        return fmt.format(value)
    
    
    def cvt_F(self, width_prec, value):
        (width,prec) = width_prec
        if len(str(value)) > width:
            return '*' * width
    
        fmt = '{:' + str(width) + '.' + str(prec) + 'f}'
        return fmt.format(value)


    def __str__(self):
        return self._regexp_str


    ###########################################################################
    #                                                                         #
    #                              INPUT MATCHING                             #
    #                                                                         #
    ###########################################################################

    # given a list of Fortran format specifiers, e.g., ['I5', '2X', 'F4.1'],
    # match_input_fmt() constructs a list of regular expressions for matching 
    # successive non-space format specifiers.
    def match_fmt(self, fmt_list):
        rexp_list = []
        for fmt in fmt_list:
            rexp_list.extend(self.match_fmt_1(fmt))
    
        return rexp_list

    
    # given a single format specifier, e.g., '2X', 'I5', etc., match_input_fmt_1() 
    # constructs a list of tuples for matching against that  specifier.  
    # Each element of this list is a tuple 
    #
    #        (xtract_re, cvt_re, divisor, cvt_fn)
    #
    # where:
    #
    #    xtract_re is a regular expression that extracts an input field of
    #            the requisite width;
    #    cvt_re is a regular expression that matches the character sequence
    #            extracted by xtract_re against the specified format; 
    #    divisor is the value to divide by in order to get the appropriate
    #            number of decimal places if a decimal point is not given
    #            in the input value (meaningful only for floats); and
    #    cvt_fn is a string denoting the function to be used to convert the
    #            matched string to a value.
    def match_fmt_1(self, fmt):
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
            rexp = self.match_fmt(fmt_list)
        else:
            if fmt[0] in 'iI':                 # integer 
                sz = fmt[1:]
                xtract_rexp = '(.{' + sz + '})'           # r.e. for extraction
                leading_sp = ' *'
                optional_sign = '-?'
                rexp0 = '\d+'
                rexp1 = leading_sp + optional_sign + rexp0   # r.e. for matching
                divisor = 1
                rexp = [(xtract_rexp, rexp1, divisor, 'int')]

            elif fmt[0] in 'xX':               # skip
                xtract_rexp = '.'              # r.e. for extraction
                rexp = [(xtract_rexp, None, None, None)]

            elif fmt[0] in 'fF':               # floating point
                idx0 = fmt.find('.')
                sz = fmt[1:idx0]
                divisor = 10**(int(fmt[idx0+1:]))
                xtract_rexp = '(.{' + sz + '})'            # r.e. for extraction
                leading_sp = ' *'
                optional_sign = '-?'
                rexp0 = '\d+(\.\d+)?'
                rexp1 = leading_sp + optional_sign + rexp0   # r.e. for matching
                rexp = [(xtract_rexp, rexp1, divisor, 'float')]
            else:
                print('ERROR: Unrecognized format specifier ' + fmt)
                sys.exit(1)
    
        # replicate the regular expression by the repetition factor in the format
        rexp *= reps
    
        return rexp

    ###########################################################################
    #                                                                         #
    #                             OUTPUT GENERATION                           #
    #                                                                         #
    ###########################################################################

    def gen_output_fmt(self, fmt_list):
        rexp_list = []
        for fmt in fmt_list:
            rexp_list.extend(self.gen_output_fmt_1(fmt))
    
        return rexp_list


    def gen_output_fmt_1(self, fmt):
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
            rexp = self.gen_output_fmt(fmt_list)
        else:
            if fmt[0] in 'iI':                 # integer 
                sz = fmt[1:]
                gen_fmt = '{}'
                cvt_fmt = '{:' + str(sz) + 'd}'
                gen_fn = 'int'
                rexp = [(gen_fmt, cvt_fmt, int(sz), gen_fn)]

            elif fmt[0] in 'xX':
                gen_fmt = ' '              
                rexp = [(gen_fmt, None, None, None)]

            elif fmt[0] in 'fF':               # floating point
                idx0 = fmt.find('.')
                sz = fmt[1:idx0]
                prec = fmt[idx0+1:]
                gen_fmt = '{}'
                cvt_fmt = '{:' + sz + '.' + prec + 'f}'
                gen_fn = 'float'
                rexp = [(gen_fmt, cvt_fmt, (int(sz), int(prec)), gen_fn)]
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

def example_1():
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
    input1 = '87001  -5.1  20.0   4.4 -23.9              10.7 '

    rexp1 = Format(format1)
    (DATE, SRAD, TMAX, TMIN, RAIN, PAR) = rexp1.read_line(input1)

    print("FORMAT: {}".format(format1))
    print("regexp_str = \"{}\"".format(rexp1))

    vars1 = (DATE, SRAD, TMAX, TMIN, RAIN, PAR)
    print("vars1 = {}".format(vars1))
    print("")


def example_2():
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

    rexp2 = Format(format2)
    (Lfmax, EMP2, EMP1) = rexp2.read_line(input2)

    print("FORMAT: {}".format(format2))
    print("regexp_str = \"{}\"".format(rexp2))

    vars2 = (Lfmax, EMP2, EMP1)
    print("vars2 = {}".format(vars2))
    print("")


if __name__ == "__main__":
    example_1()
    example_2()

