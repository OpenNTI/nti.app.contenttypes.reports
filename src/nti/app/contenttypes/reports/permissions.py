#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.contenttypes.reports.interfaces import IReportPredicate

from nti.dataserver.interfaces import IUser

from nti.dataserver.authorization_acl import has_permission

from nti.contenttypes.reports.interfaces import IReport


@interface.implementer(IReportPredicate)
@component.adapter(IReport, IUser)
class BaseReportPermission():
    """
    Concrete class that evaluates
    user permissions on a context
    for a base report
    """

    def __init__(self, *args, **kwargs):
        pass

    def evaluate(self, report, context, user):
        return True if report.permission is None or "" else has_permission(
            report.permission, context, user)
