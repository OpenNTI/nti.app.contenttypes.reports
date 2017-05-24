#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
from _pyio import __metaclass__
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from pyramid.interfaces import IRequest

from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import IExternalMappingDecorator

from nti.externalization.singleton import SingletonDecorator

from nti.links.links import Link

from nti.app.products.courseware_reports import MessageFactory as _

LINKS = StandardExternalFields.LINKS

@component.adapter(IReport, IRequest)
@interface.implementer(IExternalMappingDecorator)
class _ReportContextDecorator(object):
    
    __metaclass__ = SingletonDecorator
    
    def decorateExternalMapping(self, context, result_map):
        links = result_map.setdefault(LINKS, [])
        links.append(Link(context,
                    rel="report-%s"%context.name, 
                    elements=("@@"+context.name,),
                    title=_(context.name)))