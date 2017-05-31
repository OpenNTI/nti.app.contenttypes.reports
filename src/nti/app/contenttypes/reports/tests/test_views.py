#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import json

from hamcrest import assert_that
from hamcrest import has_entry
from hamcrest import has_entries
from hamcrest import has_items

from zope.component import getGlobalSiteManager

from nti.contenttypes.reports.tests import ITestReportContext

from nti.app.contenttypes.reports.tests import ReportsLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.dataserver.tests import mock_dataserver

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.base._compat import text_

from nti.contenttypes.reports.reports import BaseReport

from nti.contenttypes.reports.interfaces import IReport


class TestReportViews(ApplicationLayerTest, ReportsLayerTest):
    """
    Test views for reports
    """

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_all_report_get(self):

        # Register three reports to pull
        # TODO: This should be run via zcml,
        # but a problem with contexts prevents us from
        # doing that at the moment
        self._register_report("TestReport",
                              "TestDescription",
                              ITestReportContext,
                              "TestPermission",
                              ["csv", "pdf"])

        self._register_report("AnotherTestReport",
                              "AnotherTestDescription",
                              ITestReportContext,
                              "AnotherTestPermission",
                              ["csv", "pdf"])

        self._register_report("ThirdTestReport",
                              "ThirdTestDescription",
                              ITestReportContext,
                              "ThirdTestPermission",
                              ["csv", "pdf"])

        # Make sample request
        report_url = '/dataserver2/reporting/reports'
        _response = self.testapp.get(
            report_url, extra_environ=self._make_extra_environ())

        # Turn the response body into a dictionary
        res_dict = json.loads(_response.body)

        # Be sure values exist correctly
        assert_that(res_dict,
                    has_entries("ItemCount", 3,
                                "Items", has_items(
                                    has_entry("name", "TestReport"),
                                    has_entry("name", "AnotherTestReport"),
                                    has_entry("name", "ThirdTestReport"))))

    def _register_report(self, name, description,
                         interface_context, permission, supported_types):
        """
        Manual and temporary registration of reports
        """

        supported_types = tuple(set(text_(s) for s in supported_types or ()))

        # Create the Report object to be used as a subscriber
        factory = BaseReport(name=text_(name),
                             description=text_(description),
                             interface_context=interface_context,
                             permission=text_(permission),
                             supported_types=supported_types)

        getGlobalSiteManager().registerUtility(factory, IReport, name)
