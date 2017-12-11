#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from zope.security.interfaces import IPermission

from nti.contenttypes.reports.interfaces import IReport
from nti.contenttypes.reports.interfaces import IReportPredicate

from nti.dataserver.authorization_acl import has_permission

from nti.dataserver.interfaces import IUser

logger = __import__('logging').getLogger(__name__)


@component.adapter(IReport, IUser)
@interface.implementer(IReportPredicate)
class DefaultReportPermission(object):
    """
    Concrete class that evaluates user permissions on a context for a base
    report.
    """

    def __init__(self, *args, **kwargs):
        pass

    def evaluate(self, report, context, user):
        if not report.permission:
            return True
        permission = component.queryUtility(IPermission, name=report.permission)
        permission = permission or report.permission
        return has_permission(permission, context, user)
BaseReportPermission = DefaultReportPermission  # BWC
