
from time import sleep
from unittest import mock

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from test.selenium import SeleniumTest
from terrareg.models import ModuleVersion, Namespace, Module, ModuleProvider

class TestInitialSetup(SeleniumTest):
    """Test initial setup page."""

    # Disable test data
    _TEST_DATA = {}

    @classmethod
    def setup_class(cls):
        """Setup required mocks."""
        cls._config_upload_api_keys_mock = mock.patch('terrareg.config.Config.UPLOAD_API_KEYS', [])
        cls._config_allow_module_uploads_mock = mock.patch('terrareg.config.Config.ALLOW_MODULE_HOSTING', True)
        cls._config_publish_api_keys_mock = mock.patch('terrareg.config.Config.PUBLISH_API_KEYS', [])
        cls._config_admin_authentication_key_mock = mock.patch('terrareg.config.Config.ADMIN_AUTHENTICATION_TOKEN', '')
        cls._config_secret_key_mock = mock.patch('terrareg.config.Config.SECRET_KEY', '')

        cls.register_patch(cls._config_upload_api_keys_mock)
        cls.register_patch(cls._config_allow_module_uploads_mock)
        cls.register_patch(cls._config_publish_api_keys_mock)
        cls.register_patch(cls._config_admin_authentication_key_mock)
        cls.register_patch(cls._config_secret_key_mock)

        super(TestInitialSetup, cls).setup_class()

    def is_striked_through(self, el):
        """Find whether element is striked through"""
        return bool(el.find_elements(By.TAG_NAME, 'strike'))

    def check_progress_bar(self, expected_amount):
        """Check progress bar amount"""
        assert self.selenium_instance.find_element(By.ID, 'setup-progress-bar').get_attribute('value') == str(expected_amount)

    def check_only_card_is_displayed(self, expected_card):
        """Check all cards are hidden except expected card"""
        found_card = False
        # Iterate through all setup cards.
        for card in self.selenium_instance.find_elements(By.CLASS_NAME, 'initial-setup-card'):
            card_contents = self.wait_for_element(By.CLASS_NAME, 'card-content', parent=card, ensure_displayed=False)
            # Ensure the card contents is only displayed for the expected card
            if card.get_attribute('id') == f'setup-{expected_card}':
                found_card = True
                assert card_contents.is_displayed() == True
            else:
                assert card_contents.is_displayed() == False

        assert found_card

    def _test_auth_vars_step(self):
        """Test authentication variables step."""
        # Ensure that the content of setup-auth-vars is display
        auth_vars_card = self.wait_for_element(By.ID, 'setup-auth-vars')
        auth_vars_content = self.wait_for_element(By.CLASS_NAME, 'card-content', parent=auth_vars_card)

        # Check other cards are hidden
        self.check_only_card_is_displayed('auth-vars')

        # Ensure environment variables are not stricked through
        admin_token_li = auth_vars_content.find_element(By.ID, 'setup-step-auth-vars-admin-authentication-token')
        assert self.is_striked_through(admin_token_li) == False
        secret_key_li = auth_vars_content.find_element(By.ID, 'setup-step-auth-vars-secret-key')
        assert self.is_striked_through(secret_key_li) == False

        self.check_progress_bar(0)

        # Set auth token
        with self.update_mock(self._config_admin_authentication_key_mock, 'new', 'admin-setup-password'):
            # Reload page and ensure admin password is striked through
            self.selenium_instance.get(self.get_url('/initial-setup'))

            admin_token_li = self.wait_for_element(By.ID, 'setup-step-auth-vars-admin-authentication-token')
            assert self.is_striked_through(admin_token_li) == True
            secret_key_li = self.wait_for_element(By.ID, 'setup-step-auth-vars-secret-key')
            assert self.is_striked_through(secret_key_li) == False
            self.check_progress_bar(10)

        # Set secret key
        with self.update_mock(self._config_secret_key_mock, 'new', 'abcdefabcdef'):
            # Reload page and ensure secret is striked through
            self.selenium_instance.get(self.get_url('/initial-setup'))

            admin_token_li = self.wait_for_element(By.ID, 'setup-step-auth-vars-admin-authentication-token')
            assert self.is_striked_through(admin_token_li) == False
            secret_key_li = self.wait_for_element(By.ID, 'setup-step-auth-vars-secret-key')
            assert self.is_striked_through(secret_key_li) == True
            self.check_progress_bar(10)

    def _test_login_step(self):
        """Test login step."""
        # Reload page
        self.selenium_instance.get(self.get_url('/initial-setup'))

        # Ensure that login step is displayed and no other tabs are
        login_card = self.wait_for_element(By.ID, 'setup-login')
        login_card_content = self.wait_for_element(By.CLASS_NAME, 'card-content', parent=login_card)
        self.check_only_card_is_displayed('login')

        self.check_progress_bar(20)

        # Click link to login
        login_card_content.find_element(By.TAG_NAME, 'a').click()
        assert self.selenium_instance.current_url == self.get_url('/login')

        # Login as admin
        self.perform_admin_authentication('admin-setup-password')

    def _test_create_module_step(self):
        """Test create module step."""
        # Ensure user has been redirected back to initial setup
        self.assert_equals(lambda: self.selenium_instance.current_url, self.get_url('/initial-setup'))
        create_module_card = self.wait_for_element(By.ID, 'setup-create-module')
        create_module_card_content = self.wait_for_element(By.CLASS_NAME, 'card-content', parent=create_module_card)
        self.check_only_card_is_displayed('create-module')

        self.check_progress_bar(40)

        # Click link to create module
        create_module_card_content.find_element(By.TAG_NAME, 'a').click()
        assert self.selenium_instance.current_url == self.get_url('/create-module')

    def _test_index_version_git_step(self, module_provider):
        """Test step for importing a module version from git."""
        # Create module with git clone URL

        module_provider.update_attributes(repo_clone_url_template='https://example.com/mymodulepath')

        # Reload page and check step 4a is displayed
        self.selenium_instance.get(self.get_url('/initial-setup'))
        index_git_card = self.wait_for_element(By.ID, 'setup-index-git')
        index_git_card_content = self.wait_for_element(By.CLASS_NAME, 'card-content', parent=index_git_card)
        self.check_only_card_is_displayed('index-git')
        self.check_progress_bar(60)

        # Ensure warning about unpublished version is not present
        assert self.selenium_instance.find_element(By.ID, 'setup-step-index-git-not-published-warning').is_displayed() == False

        # Check link to integrations tab
        index_module_verison_link = index_git_card_content.find_element(By.TAG_NAME, 'a')
        assert index_module_verison_link.get_attribute('href') == self.get_url('/modules/unittestnamespace/setupmodulename/setupprovider#integrations')

    def _test_index_version_upload_step(self, module_provider):
        """Test step for uploading a module version."""
        module_provider.update_attributes(repo_clone_url_template=None)

        # Reload page and check step 4b is displayed
        self.selenium_instance.get(self.get_url('/initial-setup'))
        index_upload_card = self.wait_for_element(By.ID, 'setup-index-upload')
        index_upload_card_content = self.wait_for_element(By.CLASS_NAME, 'card-content', parent=index_upload_card)
        self.check_only_card_is_displayed('index-upload')
        self.check_progress_bar(60)

        expected_upload_instructions = [
            'Create a zip/tar.gz archive with the contents of the terraform module',
            f'Upload the module by performing a POST request to the upload endpoint: {self.get_url("/v1/terrareg/modules/unittestnamespace/setupmodulename/setupprovider/${version}/upload")}\n'
            'The archive file should be supplied as a file attachment.',
            f'Publish version of the module by performing a POST request to the \'publish\' endpoint: {self.get_url("/v1/terrareg/modules/unittestnamespace/setupmodulename/setupprovider/${version}/publish")}'
        ]
        for index_upload_li in index_upload_card_content.find_elements(By.TAG_NAME, 'li'):
            assert index_upload_li.text == expected_upload_instructions.pop(0)

        # Check example command for uploading/publishing version
        upload_command = index_upload_card_content.find_element(By.ID, 'setup-step-upload-module-version-example-command')
        assert upload_command.text == (
            '# Zip module\n'
            'cd path/to/module\n'
            'zip * ../module.zip\n\n'
            'version=1.0.0\n\n'
            '# Upload module version\n'
            'curl -X POST \\\n'
            f'    "{self.get_url("/v1/terrareg/modules/unittestnamespace/setupmodulename/setupprovider/${version}/upload")}" \\\n'
            '    -F file=@../module.zip\n\n'
            '# Publish module version\n'
            'curl -X POST \\\n'
            f'    "{self.get_url("/v1/terrareg/modules/unittestnamespace/setupmodulename/setupprovider/${version}/publish")}"'
        )

    def _test_publish_module_version_upload_step(self, module_provider):
        """Test index module version upload with unpublished version."""
        module_provider.update_attributes(repo_clone_url_template=None)

        # Reload page and ensure module version upload steps are striked
        self.selenium_instance.get(self.get_url('/initial-setup'))

        index_upload_card = self.wait_for_element(By.ID, 'setup-index-upload')
        index_upload_card_content = self.wait_for_element(By.CLASS_NAME, 'card-content', parent=index_upload_card)

        self.check_progress_bar(70)

        # Ensure first two steps are striked and third is still active
        expected_strikes = [True, True, False]
        for index_upload_li in index_upload_card_content.find_elements(By.TAG_NAME, 'li'):
            assert self.is_striked_through(index_upload_li) == expected_strikes.pop(0)

    def _test_publish_module_version_git_step(self, module_provider):
        """Test index module version from git with unpublished version."""
        module_provider.update_attributes(repo_clone_url_template='https://example.com/mymodulepath')
        self.selenium_instance.get(self.get_url('/initial-setup'))

        # Ensure only git index card is displayed
        self.check_only_card_is_displayed('index-git')

        self.check_progress_bar(70)

        # Ensure warning about unpublished version is present
        unpublished_version_warning = self.selenium_instance.find_element(By.ID, 'setup-step-index-git-not-published-warning')
        assert unpublished_version_warning.is_displayed() == True

        # Click link to show publish instructions
        unpublished_version_warning.find_element(By.TAG_NAME, 'a').click()

        # Ensure module version upload instructions are displayed
        assert self.selenium_instance.find_element(By.ID, 'setup-index-upload').find_element(By.CLASS_NAME, 'card-content').is_displayed() == True

    def _test_secure_instance_step(self):
        """Test secure instance step."""
        # Reload page and check step 5 is displayed
        self.selenium_instance.get(self.get_url('/initial-setup'))
        secure_card = self.wait_for_element(By.ID, 'setup-secure')
        secure_card_content = self.wait_for_element(By.CLASS_NAME, 'card-content', parent=secure_card)
        self.check_only_card_is_displayed('secure')        

        self.check_progress_bar(80)

        # Ensure secure items are not stricked through
        secure_upload_li = secure_card_content.find_element(By.ID, 'setup-step-secure-upload')
        assert self.is_striked_through(secure_upload_li) == False
        secure_publish_li = secure_card_content.find_element(By.ID, 'setup-step-secure-publish')
        assert self.is_striked_through(secure_publish_li) == False

        # Set upload API keys
        with self.update_mock(self._config_upload_api_keys_mock, 'new', ['some-api-upload-key']):
            # Reload page and ensure admin password is striked through
            self.selenium_instance.get(self.get_url('/initial-setup'))

            secure_upload_li = self.wait_for_element(By.ID, 'setup-step-secure-upload')
            assert self.is_striked_through(secure_upload_li) == True
            secure_publish_li = self.wait_for_element(By.ID, 'setup-step-secure-publish')
            assert self.is_striked_through(secure_publish_li) == False
            self.check_progress_bar(90)

        # Set publish API keys
        with self.update_mock(self._config_publish_api_keys_mock, 'new', ['some-api-publish-key']):
            # Reload page and ensure secret is striked through
            self.selenium_instance.get(self.get_url('/initial-setup'))

            secure_upload_li = self.wait_for_element(By.ID, 'setup-step-secure-upload')
            assert self.is_striked_through(secure_upload_li) == False
            secure_publish_li = self.wait_for_element(By.ID, 'setup-step-secure-publish')
            assert self.is_striked_through(secure_publish_li) == True
            self.check_progress_bar(90)

    def _test_ssl_step(self):
        """Test SSL step."""
        self.selenium_instance.get(self.get_url('/initial-setup'))
        ssl_card = self.wait_for_element(By.ID, 'setup-ssl')
        self.wait_for_element(By.CLASS_NAME, 'card-content', parent=ssl_card)
        self.check_only_card_is_displayed('ssl')
        self.check_progress_bar(100)

    def _test_complete_step(self):
        """Test complete step."""
        # Rerun loadSetupPage with override to ignore HTTP check
        self.selenium_instance.execute_script('loadSetupPage(true);')

        # Ensure setup complete step is shown
        complete_card = self.wait_for_element(By.ID, 'setup-complete')
        self.wait_for_element(By.CLASS_NAME, 'card-content', parent=complete_card)
        self.check_only_card_is_displayed('complete')
        self.check_progress_bar(120)

    def test_setup_page(self):
        """Test functionality of setup page."""
        # Load homepage
        self.selenium_instance.get(self.get_url('/'))

        # Check that we are re-directed to setup page
        self.assert_equals(lambda: self.selenium_instance.current_url, self.get_url('/initial-setup'))

        # Check page title
        assert self.selenium_instance.title == 'Initial Setup - Terrareg'

        # STEP 1 - Auth environment variables
        self._test_auth_vars_step()

        # STEP 2 - Login
        with self.update_mock(self._config_admin_authentication_key_mock, 'new', 'admin-setup-password'), \
                self.update_mock(self._config_secret_key_mock, 'new', 'abcdefabcdef'):
            self._test_login_step()

            # Step 3 - Create a module
            self._test_create_module_step()

            # Create module provider
            namespace = Namespace(name='unittestnamespace')
            module = Module(namespace=namespace, name='setupmodulename')
            module_provider = ModuleProvider.get(module=module, name='setupprovider', create=True)

            # Step 4a. - Index module version from git
            self._test_index_version_git_step(module_provider)

            # Step 4b. - Index module version from source
            self._test_index_version_upload_step(module_provider)

            # Create module version to move to next step
            module_version = ModuleVersion(module_provider=module_provider, version='1.0.0')
            module_version.prepare_module()

            # Check upload module version steps with unpublished version
            self._test_publish_module_version_upload_step(module_provider)

            # Step 4a. (repeat with unpublished version)
            self._test_publish_module_version_git_step(module_provider)

            # Publish module version to get to step 5
            module_version.publish()

            # Step 5 - Secure instance
            self._test_secure_instance_step()

            # STEP 6 - HTTPS
            with self.update_mock(self._config_upload_api_keys_mock, 'new', ['some-api-upload-key']), \
                    self.update_mock(self._config_publish_api_keys_mock, 'new', ['some-api-publish-key']):
                self._test_ssl_step()

                # Step 7 - Success
                self._test_complete_step()
