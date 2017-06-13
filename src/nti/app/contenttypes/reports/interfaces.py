#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id: 
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface


class IReportLinkProvider(interface.Interface):
    """
    Provides the necessary link decoration logic
    for reports
    """

    def link(report, context, user):
        """
        Return the link to this report
        """
