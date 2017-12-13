#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
# Modified work Copyright (c) 2017 Science and Technology Facilities Council
#
# All rights reserved.
#
# Modifications made as part of the fparser project are distributed
# under the following license:
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
##############################################################################

import fparser.parsefortran
import fparser.readfortran
import logging
import pytest

@pytest.fixture
def log():
    logger = logging.getLogger('fparser')
    log = fparser.tests.logging_utils.CaptureLoggingHandler()
    logger.addHandler( log )
    yield log
    logger.removeHandler( log )


def test_logEmpty( log ):
    class EmptyReader(object):
      id = 'thingumy'

    unit_under_test = fparser.parsefortran.FortranParser( EmptyReader() )
    unit_under_test.analyze()
    assert log.messages == {'debug':    [],
                           'info':     ['Nothing to analyze.'],
                           'warning':  [],
                           'error':    [],
                           'critical': []}

def test_logCache( log ):
    class Readerlike(object):
        id = 'thisun'

        def next():
            yield 'NOT A THING'
            yield 'MODULE foo_mod'
            raise StopIteration

    # Expect everything to go okay, no log messages.
    log.reset()
    unit_under_test = fparser.parsefortran.FortranParser( Readerlike() )
    assert log.messages == {'debug':    [],
                            'info':     [],
                            'warning':  [],
                            'error':    [],
                            'critical': []}

    # This time we should use a cached log.
    unit_under_test = fparser.parsefortran.FortranParser( Readerlike() )
    assert log.messages == {'debug':    [],
                           'info':     ['using cached thisun'],
                           'warning':  [],
                           'error':    [],
                           'critical': []}

def test_logFailure( log ):
    class FailyReader(fparser.readfortran.FortranStringReader):
        def __init__(self):
          super(FailyReader,self).__init__( 'The end' )

        def next( self, ignore_comments = False ):
          raise Exception('That''s all folks!')

    unit_under_test = fparser.parsefortran.FortranParser( FailyReader() )
    with pytest.raises(Exception):
        unit_under_test.parse()
    assert log.messages['debug'][0].startswith( 'Traceback\n' )
    assert log.messages['info'] == []
    assert log.messages['warning'] == []
    assert log.messages['error'] == []
    assert log.messages['critical'][0].startswith('While processing')
    assert log.messages['critical'][1] == 'STOPPED PARSING'
