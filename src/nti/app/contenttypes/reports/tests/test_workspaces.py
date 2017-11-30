#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_not
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries
does_not = is_not

from nti.app.contenttypes.reports.tests import ReportsLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS


class TestWorkspaces(ReportsLayerTest):
    """
    Test the global workspace Reports collection.
    """

    basic_user = u"pgreazy"
    admin_user = u"sjohnson@nextthought.com"

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_workspace(self):
        """
        Test the global workspace has a Reports collection. There is
        one registered admin report on the dataserver folder.
        """

        service_url = '/dataserver2/service/'

        def _get_report_collection(environ=None):
            service_res = self.testapp.get(service_url,
                                           extra_environ=environ)
            service_res = service_res.json_body
            workspaces = service_res['Items']
            global_ws = report_collection = None
            try:
                global_ws = next(x for x in workspaces if x['Title'] == 'Global')
            except StopIteration:
                pass
            assert_that(global_ws, not_none())
            try:
                report_collection = next(x for x in global_ws['Items']
                                         if x['Title'] == 'Reports')
            except StopIteration:
                pass
            assert_that(report_collection, not_none())
            return report_collection

        # User
        environ = self._make_extra_environ(self.basic_user)
        report_collection = _get_report_collection(environ)
        report_res = self.testapp.get(report_collection['href'],
                                      extra_environ=environ)
        report_res = report_res.json_body
        assert_that(report_res['Items'], has_length(0))

        # Admin
        report_collection = _get_report_collection()
        report_res = self.testapp.get(report_collection['href'])
        report_res = report_res.json_body
        report_items = report_res.get('Items')
        assert_that(report_items, has_length(1))
        report = report_items[0]
        assert_that(report, has_entries('name', 'GlobalReport',
                                        'href', not_none(),
                                        'rel', 'report-GlobalReport',
                                        'title', 'Global Report'))
