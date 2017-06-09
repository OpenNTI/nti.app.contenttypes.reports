#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import functools

import zope

import zope.testing

from zope import component

from zope.component import getGlobalSiteManager

from nti.contenttypes.reports.reports import BaseReport

from nti.contenttypes.reports.interfaces import IReport

from nti.contenttypes.reports.tests import ITestReportContext
from nti.contenttypes.reports.tests import ITestSecondReportContext

from nti.contenttypes.reports.reports import BaseReportAvailablePredicate

from nti.dataserver.authorization import ACT_NTI_ADMIN

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.testing.base import AbstractTestBase


class TestPredicate(BaseReportAvailablePredicate):
    """
    Test predicate
    """

    def evaluate(self, report, context, user):
        return context.containerId == u"tag:nti:foo"


class ReportsLayerTest(ApplicationLayerTest):

    get_configuration_package = AbstractTestBase.get_configuration_package.__func__

    set_up_packages = ('nti.app.contenttypes.reports',)

    utils = []
    factory = None

    @classmethod
    def setUp(self):
        """
        Set up environment for app layer report testing
        """
        def _register_report(name, title, description,
                             contexts, permission, supported_types, condition):
            """
            Manual and temporary registration of reports
            """

            # Build a report factory
            report = functools.partial(BaseReport,
                                       name=name,
                                       title=title,
                                       description=description,
                                       contexts=contexts,
                                       permission=permission,
                                       supported_types=supported_types,
                                       condition=condition)
            self.factory = report

            report_obj = report()
            # Register as a utility
            getGlobalSiteManager().registerUtility(report_obj, IReport, name)

            for interface in contexts:
                # Register it as a subscriber
                getGlobalSiteManager().registerSubscriptionAdapter(report,
                                                                   (interface,),
                                                                   IReport)

            return report_obj

        # Register three reports to test with
        self.utils.append(_register_report(u"TestReport",
                                           u"Test Report",
                                           u"TestDescription",
                                           (ITestReportContext,),
                                           ACT_NTI_ADMIN.id,
                                           [u"csv", u"pdf"],
                                           TestPredicate))

        self.utils.append(_register_report(u"AnotherTestReport",
                                           u"Another Test Report",
                                           u"AnotherTestDescription",
                                           (ITestReportContext,
                                            ITestSecondReportContext),
                                           ACT_NTI_ADMIN.id,
                                           [u"csv", u"pdf"],
                                           TestPredicate))

        self.utils.append(_register_report(u"ThirdTestReport",
                                           u"Third Test Report",
                                           u"ThirdTestDescription",
                                           (ITestReportContext,),
                                           ACT_NTI_ADMIN.id,
                                           [u"csv", u"pdf"],
                                           TestPredicate))

    @classmethod
    def tearDown(self):
        """
        Unregister all test utilities and
        subscribers
        """
        sm = component.getGlobalSiteManager()
        for util in self.utils:
            sm.unregisterUtility(component=util,
                                 provided=IReport,
                                 name=util.name)

        sm.unregisterSubscriptionAdapter(factory=self.factory,
                                         required=(ITestReportContext,),
                                         provided=IReport)

        sm.unregisterSubscriptionAdapter(factory=self.factory,
                                         required=(ITestSecondReportContext,),
                                         provided=IReport)
