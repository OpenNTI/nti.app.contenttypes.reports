#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_not
from hamcrest import not_none
from hamcrest import equal_to
from hamcrest import has_item
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import greater_than
does_not = is_not

import simplejson as json

from zope import component

from nti.app.contenttypes.reports.tests import ReportsLayerTest
from nti.app.contenttypes.reports.tests import TestReportContext
from nti.app.contenttypes.reports.tests import SecondReportContext

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.contenttypes.reports.interfaces import IReport

from nti.contenttypes.reports.reports import evaluate_permission

from nti.dataserver.tests import mock_dataserver

from nti.dataserver.users.users import User

from nti.ntiids.oids import to_external_ntiid_oid


class TestReportDecoration(ReportsLayerTest):
    """
    Test the decoration of report links for a report
    context
    """
    # Basic user with no permissions
    basic_user = u"pgreazy"

    # Admin user
    admin_user = u"sjohnson@nextthought.com"

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_report_decoration(self):
        """
        Test that report links are decorated on contexts
        only as necessary (correct permissions and correct
        predicate result)
        """

        with mock_dataserver.mock_db_trans(self.ds):
            _user = self._create_user(self.basic_user)
            test_context = TestReportContext()
            test_context.containerId = u"tag:nti:foo"
            test_context.creator = self.basic_user
            _user.addContainedObject(test_context)
            ntiid = to_external_ntiid_oid(test_context)

            second_context = TestReportContext()
            second_context.containerId = u"not:tag:nti:foo"
            second_context.creator = self.basic_user
            _user.addContainedObject(second_context)
            second_ntiid = to_external_ntiid_oid(second_context)

            third_context = SecondReportContext()
            third_context.containerId = u"tag:nti:foo"
            third_context.creator = self.basic_user
            _user.addContainedObject(third_context)
            third_ntiid = to_external_ntiid_oid(third_context)

        context_url = str('/dataserver2/Objects/' + ntiid)
        environ = self._make_extra_environ(self.basic_user)
        _response = self.testapp.get(context_url,
                                     extra_environ=environ)
        res_dict = json.loads(_response.body)

        assert_that(res_dict,
                    has_entry("Links",
                              has_item(has_entry("rel", "report-TestReport"))))
        assert_that(res_dict,
                    has_entry("Links",
                              (has_item(
                                  has_entry("rel", "report-AnotherTestReport")))))
        reports_exts = res_dict['Reports']
        assert_that(reports_exts, has_length(3))
        for report_ext in reports_exts:
            assert_that(report_ext['href'], not_none())
            assert_that(report_ext['rel'], not_none())

        context_url = str('/dataserver2/Objects/' + second_ntiid)
        _response = self.testapp.get(context_url,
                                     extra_environ=environ)
        res_dict = json.loads(_response.body)

        assert_that(res_dict,
                    has_entry("Links",
                              does_not(has_item(has_entry("rel", "report-TestReport")))))
        reports_exts = res_dict['Reports']
        assert_that(reports_exts, has_length(0))

        context_url = str('/dataserver2/Objects/' + third_ntiid)
        _response = self.testapp.get(context_url,
                                     extra_environ=environ)
        res_dict = json.loads(_response.body)

        assert_that(res_dict,
                    has_entry("Links",
                              (has_item(has_entry("rel", "report-AnotherTestReport")))))
        reports_exts = res_dict['Reports']
        assert_that(reports_exts, has_length(1))
        for report_ext in reports_exts:
            assert_that(report_ext['href'], not_none())
            assert_that(report_ext['rel'], not_none())

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_user_permissions(self):
        """
        Test that users receive links to reports
        only when allowed.
        """

        with mock_dataserver.mock_db_trans(self.ds):
            _user = self._create_user(self.basic_user)

            test_context = TestReportContext()
            test_context.creator = self.admin_user

            report = component.subscribers((test_context,), IReport)
            assert_that(report, has_length(greater_than(0)))

            report = report[0]
            admin_access = evaluate_permission(report,
                                               test_context,
                                               User.get_user(self.admin_user))

            basic_access = evaluate_permission(report,
                                               test_context,
                                               User.get_user(self.basic_user))

        assert_that(admin_access, equal_to(True))
        assert_that(basic_access, equal_to(False))
