#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface


class IReportPermission(interface.Interface):
    """
    Provides basic report permission checking
    """
    def evaluate(context, user):
        """
        Evaluate if the user has permissions
        in this context
        """
