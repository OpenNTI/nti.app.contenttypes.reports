#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from webob import multidict

from hamcrest import is_
from hamcrest import not_none
from hamcrest import has_items
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import has_properties

import simplejson as json

from nti.app.contenttypes.credit import USER_TRANSCRIPT_VIEW_NAME
from nti.app.contenttypes.credit import CREDIT_DEFINITIONS_VIEW_NAME

from nti.app.contenttypes.credit.credit import UserAwardedCredit

from nti.app.contenttypes.credit.tests import CreditLayerTest

from nti.app.contenttypes.reports.views.transcript_views import UserTranscriptReportPdf

from nti.app.testing.decorators import WithSharedApplicationMockDS

from nti.app.testing.request_response import DummyRequest

from nti.contenttypes.credit.credit import CreditDefinition

from nti.dataserver.tests import mock_dataserver

from nti.dataserver.users import User

from nti.app.contenttypes.reports.tests import ReportsLayerTest

class TestReportViews(ReportsLayerTest):
    """
    Test views for reports
    """

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_all_report_get(self):

        # Make sample request
        report_url = '/dataserver2/reporting/reports'
        _response = self.testapp.get(report_url,
                                     extra_environ=self._make_extra_environ())

        # Turn the response body into a dictionary
        res_dict = json.loads(_response.body)

        # Be sure values exist correctly
        assert_that(res_dict,
                    has_entry("Items",
                              has_items(has_entry("name", "TestReport"),
                                        has_entry("name", "AnotherTestReport"),
                                        has_entry("name", "ThirdTestReport"))))


class TestUserTranscriptReportViews(ReportsLayerTest, CreditLayerTest):
    
    def _create_credit_def(self, precision=None, credit_type=None, credit_units=None):
        service_url = '/dataserver2/service/'

        def _get_credit_collection(environ=None):
            service_res = self.testapp.get(service_url,
                                           extra_environ=environ)
            service_res = service_res.json_body
            workspaces = service_res['Items']
            global_ws = report_collection = None
            try:
                global_ws = next(x for x in workspaces if x['Title'] == 'Global')
            except StopIteration:
                pass
            assert_that(global_ws, not_none())
            try:
                report_collection = next(x for x in global_ws['Items']
                                         if x['Title'] == CREDIT_DEFINITIONS_VIEW_NAME)
            except StopIteration:
                pass
            assert_that(report_collection, not_none())
            return report_collection

        credit_collection = _get_credit_collection()
        credit_def_url = credit_collection['href']

        credit_def = {'MimeType': CreditDefinition.mime_type,
                          'credit_type': 'new_types',
                          'credit_units': 'new_units'}
        
        if credit_type is not None:
            credit_def['credit_type'] = credit_type
            
        if credit_units is not None:
            credit_def['credit_units'] = credit_units
        
        if precision is not None:
            credit_def['credit_precision'] = precision

        res = self.testapp.put_json(credit_def_url, credit_def)
        return res.json_body

    @WithSharedApplicationMockDS(testapp=True, users=True)
    def test_aggregate_credit(self):
        """
        Test aggregating credit in a transcript report with and without reduced
        credit value precision
        """
        self.install_credit_definition_container()
        try:
            non_admin_username = 'ikorarey'
            with mock_dataserver.mock_db_trans(self.ds):
                self._create_user(non_admin_username)

            user_environ = self._make_extra_environ(user=non_admin_username)

            resolve_href = '/dataserver2/ResolveUser/%s?filter_by_site_community=False' % non_admin_username
            user_ext = self.testapp.get(resolve_href).json_body
            user_ext = user_ext['Items'][0]
            user_transcript_url = self.require_link_href_with_rel(user_ext,
                                                                  USER_TRANSCRIPT_VIEW_NAME)

            # Get transcript and verify empty
            user_credits = self.testapp.get(user_transcript_url, extra_environ=user_environ).json_body
            assert_that(user_credits, has_entries('Total', is_(0),
                                                  'Items', has_length(0),
                                                  'ItemCount', is_(0)))

            # Create the credits to award
            credit_definition_default_precision = self._create_credit_def()
            title = u'awarded credit (default precision) title'
            desc = u'awarded (default precision) credit desc'
            awarded_credit_default_precision_1 = {'MimeType': UserAwardedCredit.mime_type,
                                                  'title': title,
                                                  'description': desc,
                                                  'credit_definition': credit_definition_default_precision['NTIID'],
                                                  'awarded_date': "2013-08-13T06:00:00+00:00",
                                                  'amount': 1.44}
            
            awarded_credit_default_precision_2 = {'MimeType': UserAwardedCredit.mime_type,
                                                  'title': title,
                                                  'description': desc,
                                                  'credit_definition': credit_definition_default_precision['NTIID'],
                                                  'awarded_date': "2013-08-13T06:00:00+00:00",
                                                  'amount': 1.82}
            
            credit_definition_reduced_precision = self._create_credit_def(precision=1, 
                                                                          credit_type='precision_type', 
                                                                          credit_units='precision_units')
            title = u'awarded credit (reduced precision) title'
            desc = u'awarded credit (reduced precision) desc'
            awarded_credit_reduced_precision_1 = {'MimeType': UserAwardedCredit.mime_type,
                                                  'title': title,
                                                  'description': desc,
                                                  'credit_definition': credit_definition_reduced_precision['NTIID'],
                                                  'awarded_date': "2013-08-13T06:00:00+00:00",
                                                  'amount': 1.4}
            
            awarded_credit_reduced_precision_2 = {'MimeType': UserAwardedCredit.mime_type,
                                                  'title': title,
                                                  'description': desc,
                                                  'credit_definition': credit_definition_reduced_precision['NTIID'],
                                                  'awarded_date': "2013-08-13T06:00:00+00:00",
                                                  'amount': 3.4}

            # Award credits to user
            self.testapp.put_json(user_transcript_url, 
                                  awarded_credit_default_precision_1)
            self.testapp.put_json(user_transcript_url, 
                                  awarded_credit_default_precision_2)
            self.testapp.put_json(user_transcript_url, 
                                  awarded_credit_reduced_precision_1)
            self.testapp.put_json(user_transcript_url, 
                                  awarded_credit_reduced_precision_2)

            user_credits = self.testapp.get(user_transcript_url).json_body
            assert_that(user_credits, has_entries('Total', is_(4),
                                                  'Items', has_length(4),
                                                  'ItemCount', is_(4)))
            
            # Now reduce precision
            self.testapp.put_json(credit_definition_default_precision['href'], 
                                  {'credit_precision': "1"})
            
            self.testapp.put_json(credit_definition_reduced_precision['href'], 
                                  {'credit_precision': "0"})
            
            with mock_dataserver.mock_db_trans(self.ds):
                context = User.get_user(non_admin_username)
                request = DummyRequest(params=multidict.NestedMultiDict(multidict.MultiDict({'remoteUser': User.get_user('sjohnson@nextthought.com')})))
                
                user_transcript_report = UserTranscriptReportPdf(
                    context, request)
                options = user_transcript_report()
                
            assert_that(options, has_entry('awarded_credits', has_items(has_entry('amount', u'1.4 new_units'),
                                                                        has_entry('amount', u'1.8 new_units'),
                                                                        has_entry('amount', u'1 precision_units'),
                                                                        has_entry('amount', u'3 precision_units'))))     
            assert_that(options, has_entry('aggregate_credit', has_items(has_properties({'type': u'new_types', 'amount': u'3.2 new_units'}),
                                                                         has_properties({'type': u'precision_type', 'amount': u'4 precision_units'}))))   
                      
        finally:
            self.uninstall_credit_definition_container()