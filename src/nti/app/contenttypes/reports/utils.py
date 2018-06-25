#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six
import nameparser

from functools import total_ordering

from zope import component

from zope.cachedescriptors.property import Lazy

from nti.contenttypes.reports.interfaces import IReport
from nti.contenttypes.reports.interfaces import IReportFilter

from nti.contenttypes.reports.reports import evaluate_permission
from nti.contenttypes.reports.reports import evaluate_predicate

from nti.coremetadata.interfaces import IUser

from nti.dataserver.users.interfaces import IFriendlyNamed

from nti.dataserver.users import User

from nti.externalization.interfaces import StandardExternalFields

from nti.mailer.interfaces import IEmailAddressable

from nti.schema.eqhash import EqHash

LINKS = StandardExternalFields.LINKS

logger = __import__('logging').getLogger(__name__)


def get_visible_reports_for_context(context, user):
    """
    Return the :class:`IReport` objects for the give context and user.
    """
    result = []
    report_filter = IReportFilter(context, None)
    for report in component.subscribers((context,), IReport):
        if      report_filter is not None \
            and report_filter.should_exclude_report(report):
            continue
        if      evaluate_predicate(report, context, user) \
            and evaluate_permission(report, context, user):
            result.append(report)
    return result


def _get_name_values( user, username ):
    if isinstance(user, six.string_types):
        user = User.get_user(user)

    if user and IUser.providedBy( user ):
        named_user = IFriendlyNamed(user)
        display = named_user.realname or named_user.alias or named_user.username
        # We may be given a username to override the actual username; use it.
        username = username or user.username

        if named_user.realname and '@' not in named_user.realname:
            human_name = nameparser.HumanName(named_user.realname)
            last = human_name.last or ''
            first = human_name.first or ''
        else:
            first = last = ''
    else:
        # IF a community/sharing scope, show generic.
        return u'System', u'System', u'', u''
    return username, display, first, last


@total_ordering
@EqHash("sorting_key")
class UserInfo(object):
    """
    Holds general student info. 'count' and 'perc' are optional values.
    """

    def __init__(self, user=None, username=None, display=None, count=None, perc=None):
        self._user = user
        if username and display:
            self.username = username
            self.display = display
            self.last_name = ''
            self.first_name = ''
        else:
            self.username, self.display, self.first_name, self.last_name = _get_name_values( user, username )

        self.count = count
        self.perc = perc

    def __lt__(self, other):
        return self.sorting_key.lower() < other.sorting_key.lower()

    @Lazy
    def sorting_key(self):
        if self.last_name and self.first_name:
            return self.last_name + ', ' + self.first_name
        return self.last_name or self.username

    @Lazy
    def email(self):
        email_addressable = IEmailAddressable(self._user, None)
        return email_addressable.email if email_addressable else None
