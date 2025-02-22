
from unittest import mock
import pytest
from terrareg.database import Database

from terrareg.models import Module, ModuleVersion, Namespace, ModuleProvider
import terrareg.errors
from test.integration.terrareg import TerraregIntegrationTest


class TestModuleProvider(TerraregIntegrationTest):

    @pytest.mark.parametrize('module_provider_name', [
        'invalid@atsymbol',
        'invalid"doublequote',
        "invalid'singlequote",
        '-startwithdash',
        'endwithdash-',
        '_startwithunderscore',
        'endwithunscore_',
        'a:colon',
        'or;semicolon',
        'who?knows',
        'with-dash',
        'with_underscore',
        'withAcapital',
        'StartwithCaptital',
        'endwithcapitaL',
        ''
    ])
    def test_invalid_module_provider_names(self, module_provider_name):
        """Test invalid module names"""
        namespace = Namespace(name='test')
        module = Module(namespace=namespace, name='test')
        with pytest.raises(terrareg.errors.InvalidModuleProviderNameError):
            ModuleProvider(module=module, name=module_provider_name)

    @pytest.mark.parametrize('module_provider_name', [
        'normalname',
        'name2withnumber',
        '2startendiwthnumber2',
        'contains4number'
    ])
    def test_valid_module_provider_names(self, module_provider_name):
        """Test valid module names"""
        namespace = Namespace(name='test')
        module = Module(namespace=namespace, name='test')
        ModuleProvider(module=module, name=module_provider_name)


    def test_module_provider_name_in_allow_list(self):
        """Test module provider name that is not in allow list"""
        with mock.patch('terrareg.config.Config.ALLOWED_PROVIDERS', ['aws', 'azure', 'test']):
            namespace = Namespace(name='test')
            module = Module(namespace=namespace, name='test')
            ModuleProvider(module=module, name='aws')
            ModuleProvider(module=module, name='azure')
            ModuleProvider(module=module, name='test')


    def test_module_provider_name_not_in_allow_list(self):
        """Test module provider name that is not in allow list"""
        with mock.patch('terrareg.config.Config.ALLOWED_PROVIDERS', ['onlyallow']):
            namespace = Namespace(name='test')
            module = Module(namespace=namespace, name='test')
            with pytest.raises(terrareg.errors.ProviderNameNotPermittedError):
                ModuleProvider(module=module, name='notallowed')

    def test_module_provider_get_versions(self):
        """Test that a module provider with versions in the wrong order are still returned correctly."""
        namespace = Namespace(name='testnamespace')
        module = Module(namespace=namespace, name='wrongversionorder')
        module_provider = ModuleProvider.get(module=module, name='testprovider')

        assert [mv.version for mv in module_provider.get_versions()] == [
            '23.2.3-beta', '10.23.0', '2.1.0',
            '1.5.4', '0.1.10', '0.1.09', '0.1.8',
            '0.1.1', '0.0.9'
        ]

    def test_module_provider_get_versions_without_beta(self):
        """Test that a module provider with versions in the wrong order are still returned correctly."""
        namespace = Namespace(name='testnamespace')
        module = Module(namespace=namespace, name='wrongversionorder')
        module_provider = ModuleProvider.get(module=module, name='testprovider')

        assert [mv.version for mv in module_provider.get_versions(include_beta=False)] == [
            '10.23.0', '2.1.0', '1.5.4',
            '0.1.10', '0.1.09', '0.1.8',
            '0.1.1', '0.0.9'
        ]

    def test_module_provider_get_latest_version(self):
        """
        Test that a module provider with versions in the wrong order return correct
        latest version and ignores beta version.
        """
        namespace = Namespace(name='testnamespace')
        module = Module(namespace=namespace, name='wrongversionorder')
        module_provider = ModuleProvider.get(module=module, name='testprovider')
        module_version = module_provider.get_latest_version()

        assert module_version.version == '10.23.0'

    @pytest.mark.parametrize('module_name', [
        # Module with no versions at all
        'noversions',
        # Module with only unpublished version
        'onlyunpublished',
        # Module with only a published beta version
        'onlybeta'
    ])
    def test_module_provider_get_latest_version_with_no_version(self, module_name):
        """
        Test that a module provider without any versions does not return
        a latest version.
        """
        namespace = Namespace(name='testnamespace')
        module = Module(namespace=namespace, name=module_name)
        module_provider = ModuleProvider.get(module=module, name='testprovider')
        module_version = module_provider.get_latest_version()

        assert module_version is None

    def test_module_provider_calculate_latest_version(self):
        """
        Test that a module provider with versions in the wrong order return correct
        latest version and ignores beta version with calculate_latest_version.
        """
        namespace = Namespace(name='testnamespace')
        module = Module(namespace=namespace, name='wrongversionorder')
        module_provider = ModuleProvider.get(module=module, name='testprovider')
        module_version = module_provider.calculate_latest_version()

        assert module_version.version == '10.23.0'

    @pytest.mark.parametrize('module_name', [
        # Module with no versions at all
        'noversions',
        # Module with only unpublished version
        'onlyunpublished',
        # Module with only a published beta version
        'onlybeta'
    ])
    def test_module_provider_calculate_latest_version_with_no_version(self, module_name):
        """
        Test that a module provider without any versions does not return
        a latest version using calculate_latest_version.
        """
        namespace = Namespace(name='testnamespace')
        module = Module(namespace=namespace, name=module_name)
        module_provider = ModuleProvider.get(module=module, name='testprovider')
        module_version = module_provider.calculate_latest_version()

        assert module_version is None

    def test_get_total_count(self):
        """Test get_total_count method"""
        assert ModuleProvider.get_total_count() == 42

    def test_get_module_provider_existing(self):
        """Attempt to get existing module provider"""
        namespace = Namespace(name='genericmodules')
        module = Module(namespace=namespace, name='modulename')
        module_provider = ModuleProvider.get(module=module, name='providername')
        assert module_provider is not None
        row = module_provider._get_db_row()
        assert row['id'] == 48
        assert row['namespace'] == 'genericmodules'
        assert row['module'] == 'modulename'
        assert row['provider'] == 'providername'

    def test_get_module_provider_non_existent(self):
        """Attempt to get non-existent module provider"""
        namespace = Namespace(name='genericmodules')
        module = Module(namespace=namespace, name='modulename')
        module_provider = ModuleProvider.get(module=module, name='doesnotexist')
        assert module_provider is None

    def test_get_module_provider_with_create(self):
        """Attempt to get non-existent module provider with create"""
        namespace = Namespace(name='genericmodules')
        module = Module(namespace=namespace, name='modulename')
        with mock.patch('terrareg.config.Config.AUTO_CREATE_MODULE_PROVIDER', True):
            module_provider = ModuleProvider.get(module=module, name='doesnotexistgetcreate', create=True)
            assert module_provider is not None
            assert module_provider._get_db_row()['provider'] == 'doesnotexistgetcreate'

    def test_get_module_provider_with_create_auto_create_disabled(self):
        """Attempt to get non-existent module provider with auto-creation disabled"""
        namespace = Namespace(name='genericmodules')
        module = Module(namespace=namespace, name='modulename')
        with mock.patch('terrareg.config.Config.AUTO_CREATE_MODULE_PROVIDER', False):
            module_provider = ModuleProvider.get(module=module, name='doesnotexist', create=True)
            assert module_provider is None

    def test_get_module_provider_with_create_existing(self):
        """Attempt to get non-existent module provider with create"""
        namespace = Namespace(name='genericmodules')
        module = Module(namespace=namespace, name='modulename')
        with mock.patch('terrareg.config.Config.AUTO_CREATE_MODULE_PROVIDER', True):
            module_provider = ModuleProvider.get(module=module, name='providername', create=True)
            assert module_provider is not None
            assert module_provider._get_db_row()['id'] == 48

    def test_get_module_provider_with_create_auto_create_disabled_existing(self):
        """Attempt to get non-existent module provider with auto-creation disabled"""
        namespace = Namespace(name='genericmodules')
        module = Module(namespace=namespace, name='modulename')
        with mock.patch('terrareg.config.Config.AUTO_CREATE_MODULE_PROVIDER', False):
            module_provider = ModuleProvider.get(module=module, name='providername', create=True)
            assert module_provider is not None
            assert module_provider._get_db_row()['id'] == 48

    @pytest.mark.parametrize('git_path,expected_git_path', [
        (None, None),
        ('', None),
        ('./', None),
        ('/', None),
        ('subpath', 'subpath'),
        ('/subpath', 'subpath'),
        ('./subpath', 'subpath'),
        ('./subpath/', 'subpath'),
        ('./test/another/dir', 'test/another/dir'),
        ('./test/another/dir/', 'test/another/dir'),
        ('.//lots/of///slashes//', 'lots/of/slashes')
    ])
    def test_git_path(self, git_path, expected_git_path):
        """Test git_path property"""
        module_provider = ModuleProvider.get(Module(Namespace('moduledetails'), 'git-path'), 'provider')
        module_provider.update_git_path(git_path)
        assert module_provider.git_path == expected_git_path

    def test_delete(self):
        """Test deletion of module version."""
        existing_module_provider_count = ModuleProvider.get_total_count()
        namespace = Namespace(name='testnamespace')
        module = Module(namespace=namespace, name='to-delete')

        # Create test module provider
        module_provider = ModuleProvider.get(module=module, name='testprovider', create=True)
        module_provider_pk = module_provider.pk

        # Create test module versions
        module_version_pks = []
        for itx in ['1.0.0', '1.1.1', '1.2.3']:
            module_version = ModuleVersion(module_provider=module_provider, version=itx)
            module_version.prepare_module()
            module_version.publish()
            module_version_pks.append(module_version.pk)

        assert ModuleProvider.get_total_count() == (existing_module_provider_count + 1)

        # Ensure that all of the rows can be fetched
        db = Database.get()
        with db.get_connection() as conn:

            res = conn.execute(db.module_provider.select().where(db.module_provider.c.id==module_provider_pk))
            assert res.fetchone() is not None

            for mv_pk in module_version_pks:
                res = conn.execute(db.module_version.select().where(db.module_version.c.id==mv_pk))
                assert res.fetchone() is not None

        # Delete module provider
        module_provider.delete()

        assert ModuleProvider.get_total_count() == existing_module_provider_count

        # Check module_version, example and example file have been removed
        with db.get_connection() as conn:

            res = conn.execute(db.module_provider.select().where(db.module_provider.c.id==module_provider_pk))
            assert res.fetchone() is None

            for mv_pk in module_version_pks:
                res = conn.execute(db.module_version.select().where(db.module_version.c.id==mv_pk))
                assert res.fetchone() is None
