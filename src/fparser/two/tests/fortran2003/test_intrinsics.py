# -----------------------------------------------------------------------------
# BSD 3-Clause License
#
# Copyright (c) 2019, Science and Technology Facilities Council.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

'''Test that Fortran 2003 intrinsic functions are parsed correctly.'''

import pytest
from fparser.two.Fortran2003 import Program, Intrinsic_Function_Reference, \
    Intrinsic_Name
from fparser.two.utils import FortranSyntaxError, NoMatchError, \
    InternalSyntaxError, walk_ast
from fparser.api import get_reader

# class program


def test_intrinsic_recognised(f2003_create):
    '''Test that an intrinsic is picked up when used in a program.'''

    reader = get_reader("subroutine sub()\na = sin(b)\nend subroutine sub\n")
    ast = Program(reader)
    assert walk_ast([ast], [Intrinsic_Function_Reference])


def test_intrinsic_error(f2003_create):
    '''Test that Program raises the expected exception when there is an
    intrinsic syntax error.

    '''
    reader = get_reader("subroutine sub()\na = sin(b,c)\nend subroutine sub\n")
    with pytest.raises(FortranSyntaxError) as excinfo:
        _ = Program(reader)
    assert (
        "at line 2\n"
        ">>>a = sin(b,c)\n"
        "Intrinsic 'SIN' expects 1 arg(s) but found 2") in str(excinfo.value)

# class intrinsic_name


def test_intrinsic_name_generic(f2003_create):
    '''Test that class Intrinsic_Name correctly matches a generic name.'''
    result = Intrinsic_Name("COS")
    assert isinstance(result, Intrinsic_Name)
    assert str(result) == "COS"


def test_intrinsic_name_specific(f2003_create):
    '''Test that class Intrinsic_Name correctly matches a specific name.'''
    result = Intrinsic_Name("CCOS")
    assert isinstance(result, Intrinsic_Name)
    assert str(result) == "CCOS"


def test_intrinsic_name_invalid(f2003_create):
    '''Test that class Intrinsic_Name raises the expected exception if an
    invalid intrinsic name is provided.

    '''
    with pytest.raises(NoMatchError):
        _ = Intrinsic_Name("NOT_AN_INTRINSIC")


def test_intrinsic_name_case_insensitive(f2003_create):
    '''Test that class Intrinsic_Name is a case insensitive match which
    returns the name in upper case.

    '''
    result = Intrinsic_Name("CcoS")
    assert isinstance(result, Intrinsic_Name)
    assert str(result) == "CCOS"

# class intrinsic_function_reference


def test_intrinsic_function_reference_generic(f2003_create):
    '''Test that class Intrinsic_Function_Reference correctly matches a
    generic intrinsic with a valid number of arguments.

    '''
    result = Intrinsic_Function_Reference("SIN(A)")
    assert isinstance(result, Intrinsic_Function_Reference)
    assert str(result) == "SIN(A)"


def test_intrinsic_function_reference(f2003_create):
    '''Test that class Intrinsic_Function_Reference correctly matches a
    specific intrinsic with a valid number of arguments.

    '''
    result = Intrinsic_Function_Reference("DSIN(A)")
    assert isinstance(result, Intrinsic_Function_Reference)
    assert str(result) == "DSIN(A)"


def test_intrinsic_function_nomatch(f2003_create):
    '''Test that class Intrinsic_Function_Reference raises the expected
    exception if there is no match.

    '''
    with pytest.raises(NoMatchError):
        _ = Intrinsic_Function_Reference("NO_MATCH(A)")


def test_intrinsic_function_reference_multi_args(f2003_create):
    '''Test that class Intrinsic_Function_Reference correctly matches a
    generic intrinsic which accepts more than one argument (two in
    this case).

    '''
    result = Intrinsic_Function_Reference("MATMUL(A,B)")
    assert isinstance(result, Intrinsic_Function_Reference)
    assert str(result) == "MATMUL(A, B)"


def test_intrinsic_function_reference_zero_args(f2003_create):
    '''Test that class Intrinsic_Function_Reference correctly matches a
    generic intrinsic which accepts zero arguments.

    '''
    result = Intrinsic_Function_Reference("COMMAND_ARGUMENT_COUNT()")
    assert isinstance(result, Intrinsic_Function_Reference)
    assert str(result) == "COMMAND_ARGUMENT_COUNT()"


def test_intrinsic_function_reference_range_args(f2003_create):
    '''Test that class Intrinsic_Function_Reference correctly matches a
    generic intrinsic which accepts a range of number of arguments.

    '''
    for args in ["", "A", "A, B", "A, B, C"]:
        result = Intrinsic_Function_Reference("SYSTEM_CLOCK({0})".format(args))
        assert isinstance(result, Intrinsic_Function_Reference)
        assert str(result) == "SYSTEM_CLOCK({0})".format(args)


def test_intrinsic_function_reference_unlimited_args(f2003_create):
    '''Test that class Intrinsic_Function_Reference correctly matches a
    generic intrinsic which accepts an unlimitednumber of arguments.

    '''
    for args in ["A, B", "A, B, C", "A, B, C, D"]:
        result = Intrinsic_Function_Reference("MAX({0})".format(args))
        assert isinstance(result, Intrinsic_Function_Reference)
        assert str(result) == "MAX({0})".format(args)


def test_intrinsic_function_reference_error1(f2003_create):
    '''Test that class Intrinsic_Function_Reference raises the expected
    exception when the valid min and max args are equal (2 in this case)
    and the wrong number of arguments is supplied.

    '''
    with pytest.raises(InternalSyntaxError) as excinfo:
        _ = Intrinsic_Function_Reference("MATMUL(A)")
    assert ("Intrinsic 'MATMUL' expects 2 arg(s) but found 1."
            "" in str(excinfo.value))

    with pytest.raises(InternalSyntaxError) as excinfo:
        _ = Intrinsic_Function_Reference("MATMUL(A,B,C)")
    assert ("Intrinsic 'MATMUL' expects 2 arg(s) but found 3."
            "" in str(excinfo.value))


def test_intrinsic_function_reference_error2(f2003_create):
    '''Test that class Intrinsic_Function_Reference raises the expected
    exception when the valid min args is less than the valid max args
    and the wrong number of arguments is supplied.

    '''
    with pytest.raises(InternalSyntaxError) as excinfo:
        _ = Intrinsic_Function_Reference("PRODUCT()")
    assert ("Intrinsic 'PRODUCT' expects between 1 and 3 args but found 0."
            "" in str(excinfo.value))

    with pytest.raises(InternalSyntaxError) as excinfo:
        _ = Intrinsic_Function_Reference("PRODUCT(A,B,C,D)")
    assert ("Intrinsic 'PRODUCT' expects between 1 and 3 args but found 4."
            "" in str(excinfo.value))


def test_intrinsic_function_reference_error3(f2003_create):
    '''Test that class Intrinsic_Function_Reference raises the expected
    exception when the number of arguments is unlimited.

    '''
    with pytest.raises(InternalSyntaxError) as excinfo:
        _ = Intrinsic_Function_Reference("MIN(A)")
    assert ("Intrinsic 'MIN' expects at least 2 args but found 1."
            "" in str(excinfo.value))


def test_intrinsic_inside_intrinsic(f2003_create):
    '''Test that when an intrinsic is within another instrinsic then both
    are recognised as intrinsics.

    '''
    reader = get_reader("subroutine sub()\na = sin(cos(b))\nend "
                        "subroutine sub\n")
    ast = Program(reader)
    assert "Intrinsic_Name('SIN')" in repr(ast)
    assert "Intrinsic_Name('COS')" in repr(ast)
