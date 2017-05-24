#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import not_none
from hamcrest import has_entry
from hamcrest import contains

import unittest

from zope import component

from nti.contenttypes.reports.reports import BaseReport

from nti.contenttypes.reports.tests import ITestReportContext


from nti.app.contenttypes.reports.decorators import _ReportContextDecorator

class TestReportDecoration(unittest.TestCase):
    
    def test_report_decoration(self):
        report = BaseReport(name=u"TestReport",
                            description=u"TestDescription",
                            interface_context=ITestReportContext,
                            permission=u"TestPermission",
                            supported_types=[u"csv", u"pdf"])
        
        dec = _ReportContextDecorator(object())
        result = {}
        dec.decorateExternalMapping(report, result)
        
        assert_that(result, not_none())
        assert_that(result, has_entry("Links", contains(has_property("rel", "report-TestReport"))))
