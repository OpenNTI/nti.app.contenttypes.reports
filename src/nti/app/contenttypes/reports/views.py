#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from zope.container.contained import Contained

from zope.traversing.interfaces import IPathAdapter

from pyramid.view import view_config

from pyramid.interfaces import IRequest

from nti.dataserver.authorization import ACT_NTI_ADMIN

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.dataserver.interfaces import IDataserverFolder

from nti.contenttypes.reports.interfaces import IReport

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields

from nti.externalization.externalization import to_external_object

# Items for final result dictionary
ITEM_COUNT = StandardExternalFields.ITEM_COUNT
ITEMS = StandardExternalFields.ITEMS


@interface.implementer(IPathAdapter)
@component.adapter(IDataserverFolder, IRequest)
class ReportPathAdapter(Contained):

    __name__ = u"reporting"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context


@view_config(route_name='objects.generic.traversal',
             renderer='rest',
             name='reports',
             request_method='GET',
             permission=ACT_NTI_ADMIN,
             context=ReportPathAdapter)
class RegisteredReportsView(AbstractAuthenticatedView):
    """
    View to fetch all current IReport objects
    """

    def __call__(self):
        # Create result dictionary
        result = LocatedExternalDict()
        result[ITEM_COUNT] = 0
        result[ITEMS] = []

        # Get all IReport objects
        reports = component.getAllUtilitiesRegisteredFor(IReport)

        # Put all reports into the result
        for report in reports:
            result[ITEMS].append(to_external_object(report))
            result[ITEM_COUNT] += 1
        return result
