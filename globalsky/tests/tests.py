from datetime import datetime
from django.test import TestCase
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.test import TestCase, Client

from unittest import skipIf
import os
from mock import patch
import unittest.mock as mock

from .mocks import mock_lco_authenticate, mock_api_auth, mock_get_profile, mock_get_proposals
from .base import FunctionalTest
from partners.models import Partner

class TestAccess(FunctionalTest):
    def setUp(self):
        super(TestAccess, self).setUp()
        self.add_user()
        self.add_cohort_semester()
        self.add_partner()

    @patch('globalsky.auth_backend.lco_authenticate', mock_lco_authenticate)
    def test_user_login(self):
        self.assertTrue(self.client.login(username='bart', password='simpson'))

    @patch('globalsky.auth_backend.api_auth', mock_api_auth)
    @patch('globalsky.auth_backend.get_profile', mock_get_profile)
    @patch('globalsky.auth_backend.get_proposals', mock_get_proposals)
    def test_login_proposals(self):
        # When Bart logs in, he gets 1 partner membership
        self.client.login(username='bart', password='simpson')
        partners = User.objects.get(username='bart').partner_set.all()
        # Check the same proposals go in as come out
        self.assertEqual(set([self.partner]), set(partners))

    @patch('globalsky.auth_backend.lco_authenticate', mock_lco_authenticate)
    def user_login(self):
        self.browser.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.browser.find_element_by_id("username")
        username_input.send_keys(self.username)
        password_input = self.browser.find_element_by_id("password")
        password_input.send_keys(self.password)
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_id("login-btn").click()

    def test_login(self):
        self.browser.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.browser.find_element_by_id("username")
        username_input.send_keys(self.username)
        password_input = self.browser.find_element_by_id("password")
        password_input.send_keys(self.password)
        with self.wait_for_page_load(timeout=10):
            self.browser.find_element_by_id("login-btn").click()
        # Wait until response is recieved
        self.wait_for_element_with_id('home')

    @patch('globalsky.auth_backend.lco_authenticate')
    def test_create_proposal(self, mock_login):
        self.user_login()
        link = self.browser.find_element_by_partial_link_text('Apply')
        with self.wait_for_page_load(timeout=20):
            link.click()
        actual_url = self.browser.current_url
        target_url = "{0}{1}".format(self.live_server_url, '/partners/apply/')
        self.assertEqual(actual_url, target_url)
