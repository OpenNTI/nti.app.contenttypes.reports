#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from pyramid.interfaces import IRequest

from nti.app.contenttypes.reports.interfaces import IReportLinkProvider

from nti.app.renderers.decorators import AbstractAuthenticatedRequestAwareDecorator

from nti.contenttypes.reports.interfaces import IReport
from nti.contenttypes.reports.interfaces import IReportContext

from nti.contenttypes.reports.reports import evaluate_permission
from nti.contenttypes.reports.reports import evaluate_predicate

from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalMappingDecorator

LINKS = StandardExternalFields.LINKS


@component.adapter(IReportContext, IRequest)
@interface.implementer(IExternalMappingDecorator)
class _ReportContextDecorator(AbstractAuthenticatedRequestAwareDecorator):
    """
    Decorate report contexts with their IReport links
    """

    def _predicate(self, context, result):
        return self._is_authenticated

    def _query_provider(self, objects, name):
        return component.queryMultiAdapter(objects,
                                           IReportLinkProvider,
                                           name=name)

    def _get_link(self, report, context, request, name=''):
        provider = self._query_provider((report, request),
                                        name=report.name)
        provider = provider or self._query_provider((report,),
                                                     name='')

        if provider is not None:
            return provider.link(report, context, self.remoteUser)
        return None

    def _do_decorate_external(self, context, result_map):
        links = result_map.setdefault(LINKS, [])
        # Get all IReport objects subscribed to this report context
        for report in component.subscribers((context,), IReport):
            if not evaluate_predicate(report, context, self.remoteUser):
                continue
            if not evaluate_permission(report, context, self.remoteUser):
                continue
            # default and report name base providers
            link = self._get_link(report, context, self.request)
            if link is not None:
                links.append(link)
