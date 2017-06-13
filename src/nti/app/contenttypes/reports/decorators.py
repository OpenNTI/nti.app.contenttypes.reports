#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    def _set_link(self, report, context, links, objects, name=''):
        provider = component.queryMultiAdapter(objects,
                                               IReportLinkProvider,
                                               name=name)
        if provider is not None:
            links.append(provider.link(report, context, self.remoteUser))

    def _do_decorate_external(self, context, result_map):
        links = result_map.setdefault(LINKS, [])
        # Get all IReport objects subscribed to this report context
        for report in component.subscribers((context,), IReport):
            if not evaluate_predicate(report, context, self.remoteUser):
                continue
            if not evaluate_permission(report, context, self.remoteUser):
                continue
            # default and report name base providers
            for name in (report.name, ''):
                for objects in ((report, self.request), (report,)):
                    self._set_link(report, context, links, objects, name)
