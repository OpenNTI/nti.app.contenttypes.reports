#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from pyramid.threadlocal import get_current_request

from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalMappingDecorator

from nti.externalization.singleton import SingletonDecorator

from nti.links.links import Link

from nti.contenttypes.reports.interfaces import IReport

from nti.app.contenttypes.reports import MessageFactory as _

LINKS = StandardExternalFields.LINKS


@interface.implementer(IExternalMappingDecorator)
class _ReportContextDecorator(object):
    """
    Decorate report contexts with their IReport links
    """
    __metaclass__ = SingletonDecorator

    def decorateExternalMapping(self, context, result_map):
        links = result_map.setdefault(LINKS, [])
        
        # Get all IReport objects subscribed to this report context
        reports = component.subscribers((context,), IReport)
        #print(reports)
        for report in reports:
            # Check user permission
            user = get_current_request().authenticated_userid or u''
            if report.predicate(context, user):
                
                # Add a link for each report
                links.append(Link(context,
                             rel="report-%s" % report.name,
                             elements=("@@" + report.name),
                             title=_(report.name)))
            else:
                # If the user doesn't have permission, skip this
                # report
                continue
