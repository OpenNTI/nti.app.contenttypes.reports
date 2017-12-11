#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import has_entry
from hamcrest import has_items
from hamcrest import assert_that

import simplejson as json

from nti.app.contenttypes.reports.tests import ReportsLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS


class TestReportViews(ReportsLayerTest):
    """
    Test views for reports
    """

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_all_report_get(self):

        # Make sample request
        report_url = '/dataserver2/reporting/reports'
        _response = self.testapp.get(report_url,
                                     extra_environ=self._make_extra_environ())

        # Turn the response body into a dictionary
        res_dict = json.loads(_response.body)

        # Be sure values exist correctly
        assert_that(res_dict,
                    has_entry("Items",
                              has_items(has_entry("name", "TestReport"),
                                        has_entry("name", "AnotherTestReport"),
                                        has_entry("name", "ThirdTestReport"))))
