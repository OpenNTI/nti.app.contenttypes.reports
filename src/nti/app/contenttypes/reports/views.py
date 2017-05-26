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
from nti.dataserver.authorization import ACT_READ

from nti.app.base.abstract_views import AbstractAuthenticatedView
from nti.app.base.abstract_views import AbstractView

from nti.dataserver.interfaces import IDataserverFolder

from nti.contenttypes.reports.interfaces import IReport
from nti.contenttypes.reports.interfaces import IReportContext

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.externalization import to_external_object

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
             permission=ACT_READ,
             context=ReportPathAdapter)
class RegisteredReportsView(AbstractAuthenticatedView):
    
    def __call__(self):
        result = LocatedExternalDict()
        result[ITEM_COUNT] = 0
        result[ITEMS] = []
        reports = component.getAllUtilitiesRegisteredFor(IReport)
        for report in reports:
            result[ITEMS].append(to_external_object(report))
            result[ITEM_COUNT] += 1
        return result