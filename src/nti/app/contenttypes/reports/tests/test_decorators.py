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
from hamcrest import not_none
from hamcrest import contains_inanyorder

from zope import component

from zope.configuration import config
from zope.configuration import xmlconfig

from nti.app.testing.application_webtest import ApplicationLayerTest

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.app.contenttypes.reports.tests import ReportsLayerTest

from nti.contenttypes.reports.interfaces import IReport

HEAD_ZCML_STRING = u"""
<configure  xmlns="http://namespaces.zope.org/zope"
            xmlns:i18n="http://namespaces.zope.org/i18n"
            xmlns:zcml="http://namespaces.zope.org/zcml"
            xmlns:rep="http://nextthought.com/reports">

    <include package="zope.component" file="meta.zcml" />
    <include package="zope.security" file="meta.zcml" />
    <include package="zope.component" />
    <include package="nti.contenttypes.reports" file="meta.zcml"/>

    <configure>
        <rep:registerReport name="TestReport"
                            description="TestDescription"
                            interface_context="nti.contenttypes.reports.tests.ITestReportContext"
                            permission="TestPermission"
                            supported_types="csv pdf" />
    </configure>
</configure>

"""

class TestReportDecoration(ApplicationLayerTest, ReportsLayerTest):
    
    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_report_decoration(self):
        context = config.ConfigurationMachine()
        context.package = self.get_configuration_package()
        xmlconfig.registerCommonDirectives(context)
        xmlconfig.string(HEAD_ZCML_STRING, context)
        
        