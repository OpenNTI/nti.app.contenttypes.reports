#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.app.contenttypes.reports.interfaces import IReportLinkProvider

from nti.app.contenttypes.reports import MessageFactory as _

from nti.links.links import Link

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IReportLinkProvider)
class DefaultReportLinkProvider(SchemaConfigured):
    """
    Class that will be inherited from by custom
    report link providers.
    """
    createDirectFieldProperties(IReportLinkProvider)

    # pylint: disable=super-init-not-called
    def __init__(self, *args, **kwargs):
        pass

    def link(self, report, context, unused_user=None):
        """
        Return default link elements
        """
        rel = report.rel if report.rel else "report-%s" % report.name
        return Link(context,
                    rel=rel,
                    elements=("@@" + report.name,),
                    title=_(report.title))
