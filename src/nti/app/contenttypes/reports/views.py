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

from zope.cachedescriptors.property import Lazy

from zope.location.interfaces import IContained

from zope.traversing.interfaces import IPathAdapter

from pyramid import httpexceptions as hexc

from pyramid.view import view_config

from pyramid.interfaces import IRequest

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.contenttypes.reports.interfaces import IReportLinkProvider

from nti.app.contenttypes.reports.utils import get_visible_reports_for_context

from nti.contenttypes.reports.interfaces import IReport

from nti.dataserver.authorization import is_admin_or_site_admin

from nti.dataserver.interfaces import IDataserverFolder

from nti.externalization.externalization import to_external_object

from nti.externalization.interfaces import LocatedExternalDict
from nti.externalization.interfaces import StandardExternalFields

from nti.links.externalization import render_link

ITEMS = StandardExternalFields.ITEMS
TOTAL = StandardExternalFields.TOTAL
ITEM_COUNT = StandardExternalFields.ITEM_COUNT

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IPathAdapter, IContained)
@component.adapter(IDataserverFolder, IRequest)
class ReportPathAdapter(object):

    __parent__ = None
    __name__ = "reporting"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context


@view_config(route_name='objects.generic.traversal',
             renderer='rest',
             name='reports',
             request_method='GET',
             context=ReportPathAdapter)
class RegisteredReportsView(AbstractAuthenticatedView):
    """
    View to fetch all current IReport objects
    """

    def _predicate(self):
        # XXX: Should we gatekeep this at all? We do not for global reports
        # below.
        if not is_admin_or_site_admin(self.remoteUser):
            raise hexc.HTTPForbidden()

    def __call__(self):
        self._predicate()
        result = LocatedExternalDict()
        result[ITEMS] = items = []
        for report in component.getAllUtilitiesRegisteredFor(IReport):
            items.append(to_external_object(report))
        result[ITEM_COUNT] = result[TOTAL] = len(items)
        return result


@view_config(route_name='objects.generic.traversal',
             renderer='rest',
             name='Reports',
             request_method='GET',
             context=IDataserverFolder)
class GlobalReportsView(AbstractAuthenticatedView):
    """
    A view/collection to fetch all `global` reports, defined as reports on the
    :class:`IDataserverFolder`.
    """

    def _query_provider(self, objects, name=''):
        return component.queryMultiAdapter(objects,
                                           IReportLinkProvider,
                                           name=name)

    def _get_link(self, report, context, request):
        provider = self._query_provider((report, request), name=report.name)
        provider = provider or self._query_provider((report,))
        if provider is not None:
            return provider.link(report, context, self.remoteUser)
        return None

    @Lazy
    def reports(self):
        """
        Return externalized reports for the :class:`IDataserverFolder`.
        """
        result = []
        ds_reports = get_visible_reports_for_context(self.context, self.remoteUser)
        for report in ds_reports:
            report_ext = to_external_object(report)
            result.append(report_ext)
            link = self._get_link(report, self.context, self.request)
            if link is not None:
                link_ext = render_link(link)
                # Inline the link info
                report_ext['rel'] = link_ext['rel']
                report_ext['href'] = link_ext['href']
        return result

    def __call__(self):
        result = LocatedExternalDict()
        result[ITEMS] = items = self.reports
        result[ITEM_COUNT] = result[TOTAL] = len(items)
        return result
