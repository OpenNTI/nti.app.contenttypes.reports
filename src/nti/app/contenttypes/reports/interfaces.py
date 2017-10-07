#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id: 
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

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
