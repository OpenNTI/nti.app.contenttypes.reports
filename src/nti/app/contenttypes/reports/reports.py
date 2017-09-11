#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.app.contenttypes.reports.interfaces import IReportLinkProvider

from nti.app.contenttypes.reports import MessageFactory as _

from nti.links.links import Link

from nti.schema.schema import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties


@interface.implementer(IReportLinkProvider)
class DefaultReportLinkProvider(SchemaConfigured):
    """
    Class that will be inherited from by custom
    report link providers.
    """
    createDirectFieldProperties(IReportLinkProvider)

    def __init__(self, *args, **kwargs):
        pass

    def link(self, report, context, unused_user=None):
        """
        Return default link elements
        """
        return Link(context,
                    rel="report-%s" % report.name,
                    elements=("@@" + report.name,),
                    title=_(report.title))
