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

from nti.appserver.workspaces.interfaces import IContainerCollection


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
