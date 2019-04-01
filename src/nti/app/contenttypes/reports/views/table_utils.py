#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from pyramid.path import AssetResolver

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts

from reportlab.lib.utils import simpleSplit


class TableCell(object):

    def __init__(self, text, colspan=1):
        self.text = text
        self.colspan = colspan


def get_top_header_options(data,
                           font_size=10,
                           font_name='OpenSans',
                           leading=20,
                           col_widths=[0.22, 0.78],
                           total_width=4.0*72,
                           minimum_header_height=110,
                           body_y1=0.5*72,
                           total_height=595):
    """
    Data should be an array of list or tuple, cell should be string or TableCell instance.
    """
    header_height = 0
    lines = {}
    widths = [x*total_width for x in col_widths]

    # left indent, like report_title
    widths[0] -= 2

    # TODO: dynamically compute the widths: from reportlab.pdfbase.pdfmetrics import stringWidth
    for row in data:
        _max = 0
        for index in range(0, len(row)):
            if isinstance(row[index], TableCell):
                val = row[index].text
                colspan = row[index].colspan
            else:
                val = row[index]
                colspan = 1

            width = widths[index]
            for x in range(0, colspan-1):
                width = width + widths[index]
                index = index + 1

            number_of_lines = len(simpleSplit(val, font_name, font_size, width))
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

    header_y1 = total_height - header_height - 0.2*72 # spaces above report_title
    body_height = header_y1 - body_y1

    return {'defaultHeaderHeight': header_height,
            'defaultHeaderY1': header_y1,
            'defaultBodyHeight': body_height,
            'defaultColWidths': ','.join([str(x*total_width) for x in col_widths]),
            'top_header_data': data}


# register fonts.
def register_fonts():
    pdfmetrics.registerFont(ttfonts.TTFont('OpenSans', AssetResolver().resolve('nti.app.contenttypes.reports:fonts/OpenSans-Regular.ttf').abspath()))
    pdfmetrics.registerFont(ttfonts.TTFont('OpenSansSemiBold', AssetResolver().resolve('nti.app.contenttypes.reports:fonts/OpenSans-Semibold.ttf').abspath()))
    pdfmetrics.registerFont(ttfonts.TTFont('OpenSansBold', AssetResolver().resolve('nti.app.contenttypes.reports:fonts/OpenSans-Bold.ttf').abspath()))
    pdfmetrics.registerFont(ttfonts.TTFont('OpenSansLight', AssetResolver().resolve('nti.app.contenttypes.reports:fonts/OpenSans-Light.ttf').abspath()))
register_fonts()
