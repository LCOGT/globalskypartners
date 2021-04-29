"""
NEO exchange: NEO observing portal for Las Cumbres Observatory
Copyright (C) 2015-2019 LCO

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

from subprocess import check_output, CalledProcessError
from datetime import datetime, timedelta
from glob import glob
import tempfile
import os
import shutil
import pytz

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.utils import timezone
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from django.contrib.auth.models import User


from partners.models import Cohort, Semester, Partner, Proposal

class FunctionalTest(StaticLiveServerTestCase):
    def __init__(self, *args, **kwargs):
        super(FunctionalTest, self).__init__(*args, **kwargs)
        if settings.DEBUG is False:
            settings.DEBUG = True

    @contextmanager
    def wait_for_page_load(self, timeout=30):
        old_page = self.browser.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.browser, timeout).until(
            staleness_of(old_page)
        )

    def setUp(self):

        if settings.USE_FIREFOXDRIVER:
            fp = webdriver.FirefoxProfile()
            fp.set_preference("browser.startup.homepage", "about:blank")
            fp.set_preference("startup.homepage_welcome_url", "about:blank")
            fp.set_preference("startup.homepage_welcome_url.additional", "about:blank")
            # Don't ask where to save downloaded files
            fp.set_preference("browser.download.folderList", 2);
            fp.set_preference("browser.download.manager.showWhenStarting", False);
            fp.set_preference("browser.download.dir", self.test_dir);
            fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain");

            if not hasattr(self, 'browser'):
                firefox_capabilities = DesiredCapabilities.FIREFOX
                # Marionette does not work on Firefox ~< 57. Try and determine the
                # version and check it. Hopefully this code is robust and platform-
                # independent...
                try:
                    version = check_output(["firefox", "--version"], universal_newlines=True)
                except (OSError, CalledProcessError):
                    version = None
                if version and 'Firefox' in version:
                    version_num = version.rstrip().split(' ')[-1]
                    major_version = version_num.split('.')[0]
                    firefox_capabilities['marionette'] = True
                    if major_version.isdigit() and int(major_version) <= 52:
                        firefox_capabilities['marionette'] = False
                options = webdriver.firefox.options.Options()
                options.add_argument('--headless')
                self.browser = webdriver.Firefox(capabilities=firefox_capabilities, firefox_profile=fp, options=options)
        else:
            options = webdriver.chrome.options.Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            self.browser = webdriver.Chrome(chrome_options=options)
        self.browser.implicitly_wait(5)

    def add_user(self):
        self.username = 'bart'
        self.password = 'simpson'
        self.email = 'bart@simpson.org'
        self.bart = User.objects.create_user(username=self.username, email=self.email)
        self.bart.set_password(self.password)
        self.bart.first_name= 'Bart'
        self.bart.last_name = 'Simpson'
        self.bart.is_active=1
        self.bart.save()

    def add_cohort_semester(self):
        params = { 'year': '2021',
                     'active_call': True,
                     'deadline': datetime(2021, 6, 13, 0, 0, tzinfo=pytz.utc),
                     'call': 'https://lco.global/'
                     }
        self.cohort, created = Cohort.objects.get_or_create(pk=1, **params)
        params ={
                 'start': datetime(2021, 8, 1, 0, 0, tzinfo=pytz.utc),
                 'end': datetime(2022, 1, 31, 0, 0, tzinfo=pytz.utc),
                 'code': '2021B',
                }
        s1, created = Semester.objects.get_or_create(cohort=self.cohort, **params)
        params = {
                 'start': datetime(2022, 2, 1, 0, 0, tzinfo=pytz.utc),
                 'end': datetime(2022, 7, 31, 0, 0, tzinfo=pytz.utc),
                 'code': '2022A',
                }
        s2, created = Semester.objects.get_or_create(cohort=self.cohort, **params)
        params ={
                 'start': timezone.now() - timedelta(weeks=2),
                 'end': timezone.now() + timedelta(weeks=2),
                 'code': '20XXX',
                }
        s_now, created = Semester.objects.get_or_create(cohort=self.cohort, **params)

    def add_partner(self):
        params = {
                 'name': 'AstroAwesome',
                 'proposal_code': 'LCOEPO-001',
                 'summary': 'AstroAwesome is awesome',
                 'active': True
                }
        self.partner, created = Partner.objects.get_or_create(**params)

    def add_user_as_pi(self):
        self.partner.pi.add(self.bart)
        self.partner.save()


    def wait_for_element_with_id(self, element_id):
        WebDriverWait(self.browser, timeout=10).until(
            lambda b: b.find_element_by_id(element_id),
            'Could not find element with id {}. Page text was:\n{}'.format(
                element_id, self.browser.find_element_by_tag_name('body').text
            )
        )
