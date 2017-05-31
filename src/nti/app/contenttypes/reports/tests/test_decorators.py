#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_not
from hamcrest import contains
from hamcrest import has_entry
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import contains_inanyorder

from zope import interface

from zope.configuration import config
from zope.configuration import xmlconfig

from nti.app.contenttypes.reports.decorators import _ReportContextDecorator

from nti.contenttypes.reports.interfaces import IReportContext

from nti.contenttypes.reports.tests import ITestReportContext

from nti.app.contenttypes.reports.tests import ReportsLayerTest


# ZCML string to register three reports in a context
HEAD_ZCML_STRING = u"""
<configure  xmlns="http://namespaces.zope.org/zope"
            xmlns:zcml="http://namespaces.zope.org/zcml"
            xmlns:rep="http://nextthought.com/reports">

    <include package="zope.component" file="meta.zcml" />
    <include package="zope.security" file="meta.zcml" />
    <include package="zope.component" />
    <include package="nti.contenttypes.reports" file="meta.zcml"/>
    <include package="nti.contenttypes.reports" />

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
class TestReportContext():
    """
    Concrete test class for ITestReportContext
    """
    pass


class TestReportDecoration(ReportsLayerTest):
    """
    Test the decoration of report links for a report
    context
    """

    def test_report_decoration(self):
        # Create a context for the sample ZCML and run
        # the sample string
        context = config.ConfigurationMachine()
        context.package = self.get_configuration_package()
        xmlconfig.registerCommonDirectives(context)
        xmlconfig.string(HEAD_ZCML_STRING, context)

        # Create the sample context
        test_context = TestReportContext()

        # Create the decorator with dummy arguments
        dec = _ReportContextDecorator(None, None)
        result = {}

        # Run the decorator on the context
        dec._do_decorate_external(test_context, result)

        # Be sure it has come out correctly
        assert_that(result,
                    has_entry("Links",
                              contains_inanyorder(
                                  has_property("rel", "report-TestReport"),
                                  has_property("rel", "report-AnotherTestReport"))))
        assert_that(result,
                    has_entry("Links",
                              is_not(contains(
                                  has_property("rel", "report-ThirdTestReport")))))
