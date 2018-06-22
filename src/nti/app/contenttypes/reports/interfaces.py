#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id:
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface

from zope.viewlet.interfaces import IViewletManager

from nti.appserver.workspaces.interfaces import IContainerCollection

from nti.schema.field import TextLine


class IPDFReportView(interface.Interface):
    """
    An interface that all the reporting views
    that generate PDFs and work from the same set
    of PDF templates are expected to implement.

    In this way, we have a distinct way of registering :mod:`z3c.macro``
    definitions.
    """

    filename = TextLine(title=u"The final portion of the file name, usually the view name",
                        required=False,
                        default=u"")

    report_title = TextLine(title=u"The title of the report.")


class IPDFReportHeaderManager(IViewletManager):
    """
    Viewlet manager for the headers of pdf reports.
    """


class IReportLinkProvider(interface.Interface):
    """
    Provides the necessary link decoration logic
    for reports
    """

    def link(report, context, user):
        """
        Return the link to this report
        """


class IGlobalReportCollection(IContainerCollection):
    """
    A report collection contained within the global workspace.
    """
