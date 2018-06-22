#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.contenttypes.reports.interfaces import IReportAvailablePredicate

from nti.externalization.interfaces import StandardExternalFields

LINKS = StandardExternalFields.LINKS

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IReportAvailablePredicate)
class UserTranscriptPredicate(object):

    def __init__(self, *args, **kwargs):
        pass

    def evaluate(self, report, context, unused_user):
        try:
            from nti.contenttypes.credit.interfaces import ICreditTranscript
            # Must have a transcript to get the transcript report
            return report.name != 'UserTranscriptReport' \
                or ICreditTranscript(context, None) is not None
        except ImportError:
            return False
