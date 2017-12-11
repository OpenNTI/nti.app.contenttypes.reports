#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

import functools

from zope import component
from zope import interface

from zope.component import getGlobalSiteManager

from nti.app.contenttypes.reports.interfaces import IReportLinkProvider

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.contenttypes.reports._compat import text_

from nti.contenttypes.reports.interfaces import IReport
from nti.contenttypes.reports.interfaces import IReportContext
from nti.contenttypes.reports.interfaces import IReportAvailablePredicate

from nti.contenttypes.reports.reports import BaseReport

from nti.dataserver.authorization import ACT_NTI_ADMIN

from nti.dataserver.contenttypes.note import Note

from nti.dataserver.interfaces import IDataserverFolder

from nti.contenttypes.reports.tests import ITestReportContext
from nti.contenttypes.reports.tests import ITestSecondReportContext

from nti.testing.base import AbstractTestBase


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


@interface.implementer(IReportAvailablePredicate)
class TestPredicate(object):
    """
    Test predicate
    """

    def __init__(self, *args, **kwargs):
        pass

    def evaluate(self, unused_report, context, unused_user):
        return context.containerId == u"tag:nti:foo"


class ReportsLayerTest(ApplicationLayerTest):

    get_configuration_package = AbstractTestBase.get_configuration_package.__func__

    set_up_packages = ('nti.app.contenttypes.reports',)

    utils = []
    factory = None
    predicate = None
    link_provider = None

    @classmethod
    def setUp(self):
        """
        Set up environment for app layer report testing
        """
        def _register_report(name, title, description,
                             contexts, permission, supported_types):
            """
            Manual and temporary registration of reports
            """
            supported_types = [text_(x) for x in supported_types]
            # Build a report factory
            report = functools.partial(BaseReport,
                                       name=text_(name),
                                       title=text_(title),
                                       description=text_(description),
                                       contexts=contexts,
                                       permission=permission,
                                       supported_types=supported_types)
            self.factory = report
            report_obj = report()
            # Register as a utility
            getGlobalSiteManager().registerUtility(report_obj, IReport, name)

            for provided in contexts:
                # Register it as a subscriber
                getGlobalSiteManager().registerSubscriptionAdapter(report,
                                                                   (provided,),
                                                                   IReport)

            return report_obj

        # Register three reports to test with
        self.utils.append(_register_report("TestReport",
                                           "Test Report",
                                           "TestDescription",
                                           (ITestReportContext,),
                                           ACT_NTI_ADMIN.id,
                                           ["csv", "pdf"]))

        self.utils.append(_register_report("AnotherTestReport",
                                           "Another Test Report",
                                           "AnotherTestDescription",
                                           (ITestReportContext,
                                            ITestSecondReportContext),
                                           ACT_NTI_ADMIN.id,
                                           ["csv", "pdf"]))

        self.utils.append(_register_report("ThirdTestReport",
                                           "Third Test Report",
                                           "ThirdTestDescription",
                                           (ITestReportContext,),
                                           ACT_NTI_ADMIN.id,
                                           ["csv", "pdf"]))

        # This should be somewhere else probably
        IDataserverFolder.__bases__ = IDataserverFolder.__bases__ + (IReportContext, )
        self.utils.append(_register_report("GlobalReport",
                                           "Global Report",
                                           "GlobalDescription",
                                           (IDataserverFolder,),
                                           ACT_NTI_ADMIN.id,
                                           ["csv", "pdf"]))

        self.predicate = functools.partial(TestPredicate)

        gsm = getGlobalSiteManager()
        gsm.registerSubscriptionAdapter(self.predicate,
                                        (TestReportContext,),
                                        IReportAvailablePredicate)

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

        sm.unregisterSubscriptionAdapter(factory=self.factory,
                                         required=(IDataserverFolder,),
                                         provided=IReport)

        sm.unregisterSubscriptionAdapter(factory=self.predicate,
                                         required=(TestReportContext,),
                                         provided=IReportAvailablePredicate)

        sm.unregisterSubscriptionAdapter(factory=self.link_provider,
                                         required=(BaseReport,),
                                         provided=IReportLinkProvider)
