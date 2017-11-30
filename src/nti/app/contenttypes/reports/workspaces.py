#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Implementation of an Atom/OData workspace and collection for courses.

.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface
from zope import component

from zope.cachedescriptors.property import Lazy

from zope.container.contained import Contained

from nti.app.authentication import get_remote_user

from nti.app.contenttypes.reports.interfaces import IReportLinkProvider
from nti.app.contenttypes.reports.interfaces import IGlobalReportCollection

from nti.app.contenttypes.reports.utils import get_visible_reports_for_context

from nti.dataserver.interfaces import IDataserver

from nti.externalization.externalization import to_external_object

from nti.links.externalization import render_link

from nti.property.property import alias

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IGlobalReportCollection)
class GlobalReportCollection(Contained):
    """
    A report collection that will return all reports configured on the
    """

    __name__ = u'Reports'

    accepts = ()
    links = ()

    name = alias('__name__', __name__)

    def __init__(self, container):
        self.__parent__ = container.__parent__

    @Lazy
    def ds_folder(self):
        return component.getUtility(IDataserver).dataserver_folder

    @Lazy
    def user(self):
        return get_remote_user()

    def _query_provider(self, objects, name=''):
        return component.queryMultiAdapter(objects,
                                           IReportLinkProvider,
                                           name=name)

    def _get_link(self, report, context, request):
        provider = self._query_provider((report, request), name=report.name)
        provider = provider or self._query_provider((report,))
        if provider is not None:
            return provider.link(report, context, self.remoteUser)
        return None

    @Lazy
    def reports(self):
        """
        Return externalized reports for the :class:`IDataserverFolder`.
        """
        if not self.user:
            return ()
        result = []
        context = self.ds_folder
        ds_reports = get_visible_reports_for_context(context, self.user)
        for report in ds_reports:
            report_ext = to_external_object(report)
            result.append(report_ext)
            link = self._get_link(report, context, self.request)
            if link is not None:
                link_ext = render_link(link)
                # Inline the link info
                report_ext['rel'] = link_ext['rel']
                report_ext['href'] = link_ext['href']
        return result

    @Lazy
    def container(self):
        return self.reports
