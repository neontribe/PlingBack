##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for the schema package's documentation files
"""
import doctest
import re
import unittest

from zope.testing import renormalizing

def test_suite():
    checker = renormalizing.RENormalizing([
        (re.compile(r"\[\(None, Invalid\('8<=10',\)\)\]"),
                    r"[(None, <zope.interface.exceptions.Invalid instance at 0x...>)]",)
      ])
    return unittest.TestSuite((
        doctest.DocFileSuite('../sources.txt', optionflags=doctest.ELLIPSIS),
        doctest.DocFileSuite('../fields.txt'),
        doctest.DocFileSuite('../README.txt'),
        doctest.DocFileSuite(
            '../validation.txt', checker=checker,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
