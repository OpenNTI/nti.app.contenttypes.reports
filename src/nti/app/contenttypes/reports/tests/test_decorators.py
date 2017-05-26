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
from hamcrest import has_entry
from hamcrest import contains
from hamcrest import contains_inanyorder
from hamcrest import is_not
from hamcrest import not_none

import time

from zope import interface
from zope import component

from zope.configuration import config
from zope.configuration import xmlconfig

from nti.contenttypes.reports.tests import ITestReportContext

from nti.app.contenttypes.reports.decorators import _ReportContextDecorator

from nti.contenttypes.reports.interfaces import IReport
from nti.contenttypes.reports.interfaces import IReportContext

from nti.app.contenttypes.reports.tests import ReportsLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.dataserver.tests import mock_dataserver

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.zodb.containers import time_to_64bit_int

from nti.ntiids.ntiids import make_ntiid
from nti.ntiids.ntiids import get_provider
from nti.ntiids.ntiids import get_specific
from nti.ntiids.ntiids import make_specific_safe

from nti.coremetadata.interfaces import SYSTEM_USER_NAME

from nti.contentlibrary import HTML

from nti.ntiids import ntiids

from nti.coremetadata.interfaces import IContained

from nti.externalization.oids import to_external_ntiid_oid

from nti.dataserver.contenttypes import Note

# ZCML string to register three reports in a context
HEAD_ZCML_STRING = u"""
<configure  xmlns="http://namespaces.zope.org/zope"
            xmlns:i18n="http://namespaces.zope.org/i18n"
            xmlns:zcml="http://namespaces.zope.org/zcml"
            xmlns:rep="http://nextthought.com/reports">

    <include package="zope.component" file="meta.zcml" />
    <include package="zope.security" file="meta.zcml" />
    <include package="zope.component" />
    <include package="nti.contenttypes.reports" file="meta.zcml"/>
    <include package="nti.contenttypes.reports" />

    <!-- Externalization -->
    <include package="nti.externalization" file="meta.zcml" />
    <include package="nti.externalization" />

    <configure>
        <rep:registerReport
            name="TestReport"
            description="TestDescription"
            interface_context="nti.contenttypes.reports.tests.ITestReportContext"
            permission="TestPermission"
            supported_types="csv pdf" />
        <rep:registerReport
            name="AnotherTestReport"
            description="AnotherTestDescription"
            interface_context="nti.contenttypes.reports.tests.ITestReportContext"
            permission="TestPermission"
            supported_types="pdf" />
        <rep:registerReport
            name="ThirdTestReport"
            description="IrrelevantContextDescription"
            interface_context=".tests.test_decorators.ITestWrongReportContext"
            permission="AnotherPermission"
            supported_types="csv" />
    </configure>
</configure>

"""


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
    
    username = "pgreazy"

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_report_decoration(self):
        # Create a context for the sample ZCML and run
        # the sample string
        context = config.ConfigurationMachine()
        context.package = self.get_configuration_package()
        xmlconfig.registerCommonDirectives(context)
        xmlconfig.string(HEAD_ZCML_STRING, context)
        
        print("")
        print("In test: ", component.subscribers((TestReportContext(),), IReport))
        
        with mock_dataserver.mock_db_trans(self.ds):
            user = self._create_user(self.username)
            test_context = TestReportContext()
            test_context.containerId = "samplenote"
            user.addContainedObject(test_context)
            ntiid = to_external_ntiid_oid(test_context)

        assert_that(ntiid, not_none())

        accept_type = b'application/json'

        context_url = str('/dataserver2/Objects/' + ntiid)
        _response = self.testapp.get(context_url,
                                     headers={b"Accept": accept_type},
                                     extra_environ=self._make_extra_environ(self.username))
        
        print("In test: ", component.subscribers((TestReportContext(),), IReport))
        
        assert_that(_response, not_none())

        #assert_that(_response,
        #            has_entry("Links",
        #                     contains_inanyorder(
        #                          has_property("rel", "report-TestReport"),
        #                          has_property("rel", "report-AnotherTestReport"))))
        #assert_that(_response,
        #            has_entry("Links",
        #                      is_not(contains(
        #                          has_property("rel", "report-ThirdTestReport")))))

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_all_report_get(self):
        
        with mock_dataserver.mock_db_trans(self.ds):
            user = self._create_user(self.username)
        
        report_url = '/dataserver2/reporting/reports'
        _response = self.testapp.get(
            report_url, extra_environ=self._make_extra_environ(self.username))

        print(_response.body)
