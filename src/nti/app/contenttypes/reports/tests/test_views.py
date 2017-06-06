#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import has_items
from hamcrest import assert_that

import json

from zope.component import getGlobalSiteManager

from nti.base._compat import text_

from nti.contenttypes.reports.reports import BaseReport

from nti.contenttypes.reports.interfaces import IReport

from nti.app.contenttypes.reports.tests import ReportsLayerTest

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.contenttypes.reports.tests import ITestReportContext


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
        self._register_report(u"TestReport",
                              u"TestDescription",
                              ITestReportContext,
                              u"TestPermission",
                              [u"csv", u"pdf"])

        self._register_report(u"AnotherTestReport",
                              u"AnotherTestDescription",
                              ITestReportContext,
                              u"AnotherTestPermission",
                              [u"csv", u"pdf"])

        self._register_report(u"ThirdTestReport",
                              u"ThirdTestDescription",
                              ITestReportContext,
                              u"ThirdTestPermission",
                              [u"csv", u"pdf"])

        # Make sample request
        report_url = '/dataserver2/reporting/reports'
        _response = self.testapp.get(
            report_url, extra_environ=self._make_extra_environ())

        # Turn the response body into a dictionary
        res_dict = json.loads(_response.body)

        # Be sure values exist correctly
        assert_that(res_dict,
                    has_entry("Items", has_items(
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
