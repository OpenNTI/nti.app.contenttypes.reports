#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six
import textwrap

from datetime import datetime

from zope import component
from zope import interface

from pyramid.path import AssetResolver

from pyramid.view import view_defaults

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts

from reportlab.lib.utils import simpleSplit

from z3c.pagelet.browser import BrowserPagelet

from zope.cachedescriptors.property import Lazy

from zope.intid.interfaces import IIntIds

import BTrees

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.app.contenttypes.reports.interfaces import IPDFReportView

from nti.app.contenttypes.reports.utils import UserInfo

from nti.appserver.interfaces import IDisplayableTimeProvider

from nti.dataserver.interfaces import IDeletedObjectPlaceholder
from nti.dataserver.interfaces import IUsernameSubstitutionPolicy

from nti.dataserver.metadata.index import CATALOG_NAME

from nti.dataserver.users.users import User

from nti.zope_catalog.interfaces import IDeferredCatalog

logger = __import__('logging').getLogger(__name__)


@view_defaults(route_name='objects.generic.traversal',
               renderer="nti.app.contenttypes.reports:templates/std_report_layout.rml",
               request_method='GET')
@interface.implementer(IPDFReportView)
class AbstractReportView(AbstractAuthenticatedView,
                         BrowserPagelet):
    """
    An abstract report view that provides basic data.
    """

    family = BTrees.family64

    def __init__(self, context, request):
        self.options = {}
        # Our two parents take different arguments
        AbstractAuthenticatedView.__init__(self, request)
        BrowserPagelet.__init__(self, context, request)

    @property
    def filename(self):
        return self.request.view_name

    @Lazy
    def timezone_util(self):
        return component.queryMultiAdapter((self.remoteUser, self.request),
                                           IDisplayableTimeProvider)

    def _adjust_date(self, date):
        """
        Takes a date and returns a timezoned datetime.
        """
        return self.timezone_util.adjust_date(date)

    def _adjust_timestamp(self, timestamp):
        """
        Takes a timestamp and returns a timezoned datetime
        """
        date = datetime.utcfromtimestamp(timestamp)
        return self._adjust_date(date)

    def _format_datetime(self, local_date):
        """
        Returns a string formatted datetime object
        """
        return local_date.strftime(u"%Y-%m-%d %H:%M")

    @Lazy
    def report_date_str(self):
        date = self._adjust_date(datetime.utcnow())
        return date.strftime('%b %d, %Y %I:%M %p')

    @Lazy
    def timezone_displayname(self):
        return self.timezone_util.get_timezone_display_name()

    @Lazy
    def timezone_info_str(self):
        return '(Times in %s)' % self.timezone_displayname

    def generate_footer(self):
        title = self.report_title
        return "%s %s %s" % (title, self.report_date_str, self.timezone_info_str)

    @Lazy
    def md_catalog(self):
        return component.getUtility(IDeferredCatalog, CATALOG_NAME)

    @Lazy
    def uidutil(self):
        return component.getUtility(IIntIds)

    def _replace_username(self, username):
        policy = component.queryUtility(IUsernameSubstitutionPolicy)
        result = policy.replace(username) if policy else username
        return result

    def build_user_info(self, user, **kwargs):
        if isinstance(user, six.string_types):
            username = user
            user = User.get_user(user)
        else:
            username = user.username
        username = self._replace_username(username)
        return UserInfo(user, username=username, **kwargs)

    def user_as_affix(self, user, user_info=None):
        # replace all blank spaces with empty space
        if user_info is None:
            user_info = self.build_user_info(user)
        return user_info.display.replace(' ', '')

    def filter_objects(self, objects):
        """
        Returns a set of filtered objects
        """
        return [
            x for x in objects if not IDeletedObjectPlaceholder.providedBy(x)
        ]

    def wrap_text(self, text, size):
        return textwrap.fill(text, size)


def get_header_options(input_data,
                       font_size=10,
                       font_name='OpenSans',
                       leading=20,
                       total_width=4.0*72,
                       col_widths=[0.22, 0.78],
                       minimum_header_height=110,
                       body_y1=0.5*72,
                       total_height=595):
    """
    input_data should be an array of tuple.
    """
    header_height = 0
    lines = {}
    widths = [x*total_width for x in col_widths]

    # left indent, like report_title
    widths[0] -= 0.07*72

    # TODO: dynamically compute the widths: from reportlab.pdfbase.pdfmetrics import stringWidth
    for row in input_data:
        _max = 0
        for index in range(0, len(row)):
            number_of_lines = len(simpleSplit(row[index], font_name, font_size, widths[index]))
            if _max < number_of_lines:
                _max = number_of_lines

        header_height += _max*leading

    # report_title:40
    header_height = header_height + 40
    if header_height > total_height:
        raise ValueError("There is too much data for the header.")

    # The LOGO image starts from 7in.
    # If no minimum height, the body would overlap the LOGO image.
    if header_height < minimum_header_height:
        header_height = minimum_header_height

    header_y1 = total_height - header_height
    body_height = header_y1 - body_y1

    return {'defaultHeaderHeight': header_height,
            'defaultHeaderY1': header_y1,
            'defaultBodyHeight': body_height,
            'defaultColWiths': ','.join([str(x*total_width) for x in col_widths])}


# register fonts.
def register_fonts():
    pdfmetrics.registerFont(ttfonts.TTFont('OpenSans', AssetResolver().resolve('nti.app.contenttypes.reports:fonts/OpenSans-Regular.ttf').abspath()))
    pdfmetrics.registerFont(ttfonts.TTFont('OpenSansSemiBold', AssetResolver().resolve('nti.app.contenttypes.reports:fonts/OpenSans-Semibold.ttf').abspath()))
    pdfmetrics.registerFont(ttfonts.TTFont('OpenSansBold', AssetResolver().resolve('nti.app.contenttypes.reports:fonts/OpenSans-Bold.ttf').abspath()))
    pdfmetrics.registerFont(ttfonts.TTFont('OpenSansLight', AssetResolver().resolve('nti.app.contenttypes.reports:fonts/OpenSans-Light.ttf').abspath()))
register_fonts()
