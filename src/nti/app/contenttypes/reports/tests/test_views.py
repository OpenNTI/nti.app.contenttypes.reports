#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.configuration import config
from zope.configuration import xmlconfig

from nti.app.testing.decorators import WithSharedApplicationMockDS

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
#@WithSharedApplicationMockDS(testapp=True, users=True)
#def funct():
#    context = config.ConfigurationMachine()
#        context.package = self.get_configuration_package()
#        xmlconfig.registerCommonDirectives(context)
#        xmlconfig.string(HEAD_ZCML_STRING, context)
#        
#    with mock_dataserver.mock_db_trans(self.ds):
#                username = 'pgreazy'
#                self._create_user(username)
#                environ = self._make_extra_environ(username)
#            
#    report = component.getUtility(IReport)
#    component.getGlobalSiteManager().registerUtility(report, IReport, "austin")
    #print(to_external_object(report))
 #   reports = self.testapp.get('/dataserver2/reporting/reports', None, status=200, extra_environ=environ)