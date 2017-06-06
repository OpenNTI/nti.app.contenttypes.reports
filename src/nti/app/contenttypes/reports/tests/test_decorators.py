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
from hamcrest import not_none
from hamcrest import assert_that

import functools

import json

from zope import component
from zope import interface

from zope.component.globalregistry import getGlobalSiteManager

from nti.contenttypes.reports.interfaces import IReport
from nti.contenttypes.reports.interfaces import IReportContext

from nti.contenttypes.reports.reports import BaseReport

from nti.contenttypes.reports.tests import ITestReportContext

from nti.contenttypes.reports.reports import evaluate_permission

from nti.dataserver.authorization import ACT_NTI_ADMIN

from nti.dataserver.contenttypes.note import Note

from nti.dataserver.users.users import User

from nti.externalization.oids import to_external_ntiid_oid

from nti.app.contenttypes.reports.tests import ReportsLayerTest

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.dataserver.tests import mock_dataserver


class ITestWrongReportContext(IReportContext):
    """
    Test context for a third report to be sure we
    aren't pulling extra reports
    """


@interface.implementer(ITestReportContext)
class TestReportContext(Note):
    """
    Concrete test class for ITestReportContext
    """


class TestReportDecoration(ApplicationLayerTest, ReportsLayerTest):
    """
    Test the decoration of report links for a report
    context
    """
    # Basic user with no permissions
    basic_user = u"pgreazy"

    # Admin user
    admin_user = u"sjohnson@nextthought.com"

    def _register_report(self, name, description,
                         interface_context, permission, supported_types):
        # Build a report factory
        report = functools.partial(BaseReport,
                                   name=name,
                                   description=description,
                                   interface_context=interface_context,
                                   permission=permission,
                                   supported_types=supported_types)

        # Register it as a subscriber
        getGlobalSiteManager().registerSubscriptionAdapter(report,
                                                           (interface_context,),
                                                           IReport)

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_report_decoration(self):
        # Register two reports: one we want to find and one
        # we don't
        self._register_report(u"TestReport",
                              u"TestDescription",
                              ITestReportContext,
                              ACT_NTI_ADMIN.id,
                              [u"csv"])
        self._register_report(u"AnotherTestReport",
                              u"AnotherTestDescription",
                              ITestWrongReportContext,
                              ACT_NTI_ADMIN.id,
                              [u"csv", u"pdf"])

        # Create the user and the context
        with mock_dataserver.mock_db_trans(self.ds):
            # Create the sample context
            _user = self._create_user(self.basic_user)
            test_context = TestReportContext()
            test_context.containerId = u"tag:nti:foo"
            test_context.creator = self.basic_user
            _user.addContainedObject(test_context)
            ntiid = to_external_ntiid_oid(test_context)

        # Ask for the context objects, hopefully
        # with the report links
        context_url = str('/dataserver2/Objects/' + ntiid)
        environ = self._make_extra_environ(self.basic_user)
        _response = self.testapp.get(context_url,
                                     extra_environ=environ)

        # Turn the response into something testable
        res_dict = json.loads(_response.body)

        # Be sure it has come out correctly
        assert_that(res_dict,
                    has_entry("Links",
                              has_item(has_entry(
                                  "rel", "report-TestReport"))))
        assert_that(res_dict,
                    has_entry("Links",
                              is_not(has_item(
                                  has_entry("rel", "report-AnotherTestReport")))))

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_user_permissions(self):

        with mock_dataserver.mock_db_trans(self.ds):
            # Create the basic user
            _user = self._create_user(self.basic_user)

            # Create the test report context, and
            # give the admin user access
            test_context = TestReportContext()
            test_context.creator = self.admin_user

            # A report with admin permissions
            # was already created above, so we don't need to
            # make another one.

            # Grab the report
            report = component.subscribers((test_context,), IReport)

            # Make sure we only got one
            assert_that(report, not_none())

            # Grab the first one
            report = report[0]

            # Test permissions for both users
            admin_access = evaluate_permission(report,
                                               test_context,
                                               User.get_user(self.admin_user))

            basic_access = evaluate_permission(report,
                                               test_context,
                                               User.get_user(self.basic_user))

        # Compare values
        assert_that(admin_access, equal_to(True))
        assert_that(basic_access, equal_to(False))
