# Copyright 2013-2018 Reahl Software Services (Pty) Ltd. All rights reserved.
#
#    This file is part of Reahl.
#
#    Reahl is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation; version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, unicode_literals, absolute_import, division

import pytest
from reahl.stubble import Impostor, stubclass


def test_impostor_pretends_to_be_stubbed():
    """an Impostor fakes being an instance the stubbed class"""

    class Stubbed(object):
        __slots__ = 'a'

    @stubclass(Stubbed)
    class Stub(Impostor):
        pass

    stub = Stub()
    #normal case
    assert isinstance(stub, Stubbed)
