#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from pyramid.interfaces import IRequest

from nti.app.contenttypes.reports import MessageFactory as _

from nti.contenttypes.reports.reports import evaluate_permission

from nti.app.renderers.decorators import AbstractAuthenticatedRequestAwareDecorator

from nti.contenttypes.reports.interfaces import IReport, IReportContext

from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalMappingDecorator

from nti.links.links import Link

LINKS = StandardExternalFields.LINKS


@component.adapter(IReportContext, IRequest)
@interface.implementer(IExternalMappingDecorator)
class _ReportContextDecorator(AbstractAuthenticatedRequestAwareDecorator):
    """
    Decorate report contexts with their IReport links
    """

    def _predicate(self, context, result):
        return self._is_authenticated

    def _do_decorate_external(self, context, result_map):
        links = result_map.setdefault(LINKS, [])
        # Get all IReport objects subscribed to this report context
        reports = component.subscribers((context,), IReport)
        for report in reports:
            # Check user permission
            if evaluate_permission(report, context, self.remoteUser):
                # Add a link for each report
                links.append(Link(context,
                                  rel="report-%s" % report.name,
                                  elements=("@@" + report.name),
                                  title=_(report.name)))
