#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from nti.contenttypes.reports.interfaces import IReport

from nti.contenttypes.reports.reports import evaluate_permission
from nti.contenttypes.reports.reports import evaluate_predicate

from nti.externalization.interfaces import StandardExternalFields

LINKS = StandardExternalFields.LINKS

logger = __import__('logging').getLogger(__name__)


def get_visible_reports_for_context(context, user):
    """
    Return the :class:`IReport` objects for the give context and user.
    """
    result = []
    for report in component.subscribers((context,), IReport):
        if      evaluate_predicate(report, context, user) \
            and evaluate_permission(report, context, user):
            result.append(report)
    return result
