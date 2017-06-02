#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from nti.dataserver.interfaces import IUser

from nti.dataserver.authorization_acl import has_permission

from nti.contenttypes.reports.interfaces import IReport

from nti.app.contenttypes.reports.interfaces import IReportPermission

@interface.implementer(IReportPermission)
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


def evaluate_permission(report, context, user):
    """
    Evaluate whether a user has permissions on this report.
    Aggregate all permissions from all permissions
    providers. All must be true to grant permission
    """

    # Grab the permission providers
    predicates = component.subscribers((report, user), IReportPermission)

    # If there are none, don't grant permission
    if not predicates:
        return False

    # Make sure all eval to true, grant if true
    predicates = list(predicates)

    return all((p.evaluate(report, context, user) for p in predicates))
