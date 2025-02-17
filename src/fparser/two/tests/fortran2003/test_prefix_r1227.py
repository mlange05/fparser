# Copyright (c) 2019 Science and Technology Facilities Council

# All rights reserved.

# Modifications made as part of the fparser project are distributed
# under the following license:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

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

'''Test Fortran 2003 rule R1227 : prefix.'''
import pytest

import fparser.two.Fortran2003 as f2003
from fparser.two.utils import NoMatchError


def test_prefix(f2003_create):
    '''Test that valid Prefix strings are matched successfully.

    '''
    # single space
    result = f2003.Prefix("impure elemental module")
    assert result.tostr() == "IMPURE ELEMENTAL MODULE"
    assert (result.torepr() ==
            "Prefix(' ', (Prefix_Spec('IMPURE'), Prefix_Spec('ELEMENTAL'), "
            "Prefix_Spec('MODULE')))")

    # multiple spaces
    result = f2003.Prefix("  impure  elemental  module  ")
    assert result.tostr() == "IMPURE ELEMENTAL MODULE"
    assert (result.torepr() ==
            "Prefix(' ', (Prefix_Spec('IMPURE'), Prefix_Spec('ELEMENTAL'), "
            "Prefix_Spec('MODULE')))")


def test_single_prefix_spec(f2003_create):
    '''Test that a single prefix-spec is returned as a Prefix containing a
    Prefix_Spec.

    '''
    result = f2003.Prefix("impure")
    assert result.tostr() == "IMPURE"
    assert (result.torepr() ==
            "Prefix(' ', (Prefix_Spec('IMPURE'),))")


def test_prefix_nomatch(f2003_create):
    '''Test that invalid Prefix strings raise a NoMatchError exception.

    '''
    for string in ["invalid", "pure impure purile", "", " "]:
        with pytest.raises(NoMatchError):
            _ = f2003.Prefix(string)
