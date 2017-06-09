#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_not
from hamcrest import equal_to
from hamcrest import has_item
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import greater_than
does_not = is_not
 
import json

from zope import component
from zope import interface

from nti.contenttypes.reports.interfaces import IReport

from nti.contenttypes.reports.tests import ITestReportContext
from nti.contenttypes.reports.tests import ITestSecondReportContext

from nti.contenttypes.reports.reports import evaluate_permission

from nti.dataserver.contenttypes.note import Note

from nti.dataserver.users.users import User

from nti.dataserver.tests import mock_dataserver

from nti.externalization.oids import to_external_ntiid_oid

from nti.app.contenttypes.reports.tests import ReportsLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS


@interface.implementer(ITestReportContext)
class TestReportContext(Note):
    """
    Concrete test class for ITestReportContext
    """


@interface.implementer(ITestSecondReportContext)
class SecondReportContext(Note):
    """
    Concrete test class for ITestSecondReportContext
    """


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

        context_url = str('/dataserver2/Objects/' + second_ntiid)
        _response = self.testapp.get(context_url,
                                     extra_environ=environ)

        res_dict = json.loads(_response.body)

        assert_that(res_dict,
                    has_entry("Links",
                              does_not(has_item(has_entry("rel", "report-TestReport")))))

        context_url = str('/dataserver2/Objects/' + third_ntiid)
        _response = self.testapp.get(context_url,
                                     extra_environ=environ)

        res_dict = json.loads(_response.body)

        assert_that(res_dict,
                    has_entry("Links",
                              (has_item(has_entry("rel", "report-AnotherTestReport")))))

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
