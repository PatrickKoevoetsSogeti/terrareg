
import os
import uuid

from terrareg.errors import InvalidBooleanConfigurationError

class Config:

    _INTERNAL_EXTRACTION_ANALYITCS_TOKEN = str(uuid.uuid4())
    """Analaytics token used by terraform initialised by the registry"""

    @property
    def DOMAIN_NAME(self):
        """Domain name that the system is hosted on"""
        return os.environ.get('DOMAIN_NAME', None)

    @property
    def DATA_DIRECTORY(self):
        return os.path.join(os.environ.get('DATA_DIRECTORY', os.getcwd()), 'data')

    @property
    def DATABASE_URL(self):
        """
        URL for database.
        Defaults to local sqlite database.

        To setup SQLite datbase, use `sqlite:///<path to sqlite DB>`

        To setup MySQL, use `mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<database>`
        """
        return os.environ.get('DATABASE_URL', 'sqlite:///modules.db')

    @property
    def LISTEN_PORT(self):
        """
        Port for server to listen on.
        """
        return int(os.environ.get('LISTEN_PORT', 5000))

    @property
    def SSL_CERT_PRIVATE_KEY(self):
        """
        Path to SSL private certificate key.

        If running in a container, the key must be mounted inside the container.
        This value must be set to the path of the key within the container.

        This must be set in accordance with SSL_CERT_PUBLIC_KEY - both must either be
        set or left empty.
        """
        return os.environ.get('SSL_CERT_PRIVATE_KEY', None)

    @property
    def SSL_CERT_PUBLIC_KEY(self):
        """
        Path to SSL public key.

        If running in a container, the key must be mounted inside the container.
        This value must be set to the path of the key within the container.

        This must be set in accordance with SSL_CERT_PRIVATE_KEY - both must either be
        set or left empty.
        """
        return os.environ.get('SSL_CERT_PUBLIC_KEY', None)

    @property
    def ALLOW_UNIDENTIFIED_DOWNLOADS(self):
        """
        Whether modules can be downloaded with terraform
        without specifying an identification string in
        the namespace
        """
        return self.convert_boolean(os.environ.get('ALLOW_UNIDENTIFIED_DOWNLOADS', 'False'))

    @property
    def DEBUG(self):
        """Whether flask and sqlalchemy is setup in debug mode."""
        return self.convert_boolean(os.environ.get('DEBUG', 'False'))

    @property
    def THREADED(self):
        """Whether flask is configured to enable threading"""
        return self.convert_boolean(os.environ.get('THREADED', 'True'))

    @property
    def ANALYTICS_TOKEN_PHRASE(self):
        """Name of analytics token to provide in responses (e.g. `application name`, `team name` etc.)"""
        return os.environ.get('ANALYTICS_TOKEN_PHRASE', 'analytics token')

    @property
    def ANALYTICS_TOKEN_DESCRIPTION(self):
        """Describe to be provided to user about analytics token (e.g. `The name of your application`)"""
        return os.environ.get('ANALYTICS_TOKEN_DESCRIPTION', '')

    @property
    def EXAMPLE_ANALYTICS_TOKEN(self):
        """
        Example analytics token to provide in responses (e.g. my-tf-application, my-slack-channel etc.).

        Note that, if this token is used in a module call, it will be ignored and treated as if
        an analytics token has not been provided.
        If analytics tokens are required, this stops users from accidently using the example placeholder in
        terraform projects.
        """
        return os.environ.get('EXAMPLE_ANALYTICS_TOKEN', 'my-tf-application')

    @property
    def ALLOWED_PROVIDERS(self):
        """
        Comma-seperated list of allowed providers.

        Leave empty to disable allow-list and allow all providers.
        """
        return [
            attr for attr in os.environ.get('ALLOWED_PROVIDERS', '').split(',') if attr
        ]

    @property
    def TRUSTED_NAMESPACES(self):
        """Comma-separated list of trusted namespaces."""
        return [
            attr for attr in os.environ.get('TRUSTED_NAMESPACES', '').split(',') if attr
        ]

    @property
    def TRUSTED_NAMESPACE_LABEL(self):
        """Custom name for 'trusted namespace' in UI."""
        return os.environ.get('TRUSTED_NAMESPACE_LABEL', 'Trusted')

    @property
    def CONTRIBUTED_NAMESPACE_LABEL(self):
        """Custom name for 'contributed namespace' in UI."""
        return os.environ.get('CONTRIBUTED_NAMESPACE_LABEL', 'Contributed')

    @property
    def VERIFIED_MODULE_NAMESPACES(self):
        """
        List of namespaces, who's modules will be automatically set to verified.
        """
        return [
            attr for attr in os.environ.get('VERIFIED_MODULE_NAMESPACES', '').split(',') if attr
        ]

    @property
    def VERIFIED_MODULE_LABEL(self):
        """Custom name for 'verified module' in UI."""
        return os.environ.get('VERIFIED_MODULE_LABEL', 'Verified')

    @property
    def DISABLE_TERRAREG_EXCLUSIVE_LABELS(self):
        """
        Whether to disable 'terrareg exclusive' labels from feature tabs in UI.

        Set to 'True' to disable the labels.
        """
        return self.convert_boolean(os.environ.get('DISABLE_TERRAREG_EXCLUSIVE_LABELS', 'False'))

    @property
    def DELETE_EXTERNALLY_HOSTED_ARTIFACTS(self):
        """
        Whether uploaded modules, that provide an external URL for the artifact,
        should be removed after analysis.
        If enabled, module versions with externally hosted artifacts cannot be re-analysed after upload.
        """
        return self.convert_boolean(os.environ.get('DELETE_EXTERNALLY_HOSTED_ARTIFACTS', 'False'))

    @property
    def ALLOW_MODULE_HOSTING(self):
        """
        Whether uploaded modules can be downloaded directly.
        If disabled, all modules must be configured with a git URL.
        """
        return self.convert_boolean(os.environ.get('ALLOW_MODULE_HOSTING', 'True'))

    @property
    def REQUIRED_MODULE_METADATA_ATTRIBUTES(self):
        """
        Comma-seperated list of metadata attributes that each uploaded module _must_ contain, otherwise the upload is aborted.
        """
        return [
            attr for attr in os.environ.get('REQUIRED_MODULE_METADATA_ATTRIBUTES', '').split(',') if attr
        ]

    @property
    def APPLICATION_NAME(self):
        """Name of application to be displayed in web interface."""
        return os.environ.get('APPLICATION_NAME', 'Terrareg')

    @property
    def LOGO_URL(self):
        """URL of logo to be used in web interface."""
        return os.environ.get('LOGO_URL', '/static/images/logo.png')

    @property
    def ANALYTICS_AUTH_KEYS(self):
        """
        List of comma-separated values for terraform auth tokens for deployment environments.

        E.g. `xxxxxx.deploy1.xxxxxxxxxxxxx:dev,zzzzzz.deploy1.zzzzzzzzzzzzz:prod`
        In this example, in the 'dev' environment, the auth token for terraform would be: `xxxxxx.deploy1.xxxxxxxxxxxxx`
        and the auth token for terraform for prod would be: `zzzzzz.deploy1.zzzzzzzzzzzzz`.

        To disable auth tokens and to report all downloads, leave empty.

        To only record downloads in a single environment, specify a single auth token. E.g. `zzzzzz.deploy1.zzzzzzzzzzzzz`

        For information on using these API keys, please see Terraform: https://docs.w3cub.com/terraform/commands/cli-config.html#credentials
        """
        return [
            token for token in os.environ.get('ANALYTICS_AUTH_KEYS', '').split(',') if token
        ]

    @property
    def UPLOAD_API_KEYS(self):
        """
        List of comma-separated list of API keys to upload/import new module versions.

        For bitbucket hooks, one of these keys must be provided as the 'secret' to the webhook.

        To disable authentication for upload endpoint, leave empty.
        """
        return [
            token
            for token in os.environ.get('UPLOAD_API_KEYS', '').split(',')
            if token
        ]

    @property
    def PUBLISH_API_KEYS(self):
        """
        List of comma-separated list of API keys to publish module versions.

        To disable authentication for publish endpoint, leave empty.
        """
        return [
            token
            for token in os.environ.get('PUBLISH_API_KEYS', '').split(',')
            if token
        ]

    @property
    def ADMIN_AUTHENTICATION_TOKEN(self):
        """
        Token to use for authorisation to be able to modify modules in the user interface.
        """
        return os.environ.get('ADMIN_AUTHENTICATION_TOKEN', None)

    @property
    def SECRET_KEY(self):
        """
        Flask secret key used for encrypting sessions.

        Can be generated using: `python -c 'import secrets; print(secrets.token_hex())'`
        """
        return os.environ.get('SECRET_KEY', None)

    @property
    def ADMIN_SESSION_EXPIRY_MINS(self):
        """
        Session timeout for admin cookie sessions
        """
        return int(os.environ.get('ADMIN_SESSION_EXPIRY_MINS', 60))

    @property
    def AUTO_PUBLISH_MODULE_VERSIONS(self):
        """
        Whether new module versions (either via upload, import or hook) are automatically
        published and available.

        If this is disabled, the publish endpoint must be called before the module version
        is displayed in the list of module versions.

        NOTE: Even whilst in an unpublished state, the module version can still be accessed directly, but not used within terraform.
        """
        return self.convert_boolean(os.environ.get('AUTO_PUBLISH_MODULE_VERSIONS', 'True'))

    @property
    def AUTO_CREATE_MODULE_PROVIDER(self):
        """
        Whether to automatically create module providers when
        uploading module versions, either from create endpoint or hooks.

        If disabled, modules must be created using the module provider create endpoint (or via the web interface).
        """
        return self.convert_boolean(os.environ.get('AUTO_CREATE_MODULE_PROVIDER', 'True'))

    @property
    def MODULES_DIRECTORY(self):
        """
        Directory with a module's source that contains sub-modules.

        submodules are expected to be within sub-directories of the submodule directory.

        E.g. If MODULES_DIRECTORY is set to `modules`, with the root module, the following would be expected for a submodule: `modules/submodulename/main.tf`.

        This can be set to an empty string, to expected submodules to be in the root directory of the parent module.
        """
        return os.environ.get('MODULES_DIRECTORY', 'modules')

    @property
    def EXAMPLES_DIRECTORY(self):
        """
        Directory with a module's source that contains examples.

        Examples are expected to be within sub-directories of the examples directory.

        E.g. If EXAMPLES_DIRECTORY is set to `examples`, with the root module, the following would be expected for an example: `examples/myexample/main.tf`.
        """
        return os.environ.get('EXAMPLES_DIRECTORY', 'examples')

    @property
    def GIT_PROVIDER_CONFIG(self):
        """
        Git provider config.
        JSON list of known git providers.
        Each item in the list should contain the following attributes:
        - name - Name of the git provider (e.g. 'Corporate Gitlab')

        - base_url - Formatted base URL for project's repo.
                    (e.g. 'https://github.com/{namespace}/{module}'
                        or 'https://gitlab.corporate.com/{namespace}/{module}')
        - clone_url - Formatted clone URL for modules.
                    (e.g. 'ssh://gitlab.corporate.com/scm/{namespace}/{module}.git'
                        or 'https://github.com/{namespace}/{module}-{provider}.git')
                    Note: Do not include '{version}' placeholder in the URL -
                    the git tag will be automatically provided.

        - browse_url - Formatted URL for user-viewable source code
                        (e.g. 'https://github.com/{namespace}/{module}-{provider}/tree/{tag}/{path}'
                        or 'https://bitbucket.org/{namespace}/{module}/src/{version}?at=refs%2Ftags%2F{tag_uri_encoded}').
                        Must include placeholdes:
                         - {path} (for source file/folder path)
                         - {tag} or {tag_uri_encoded} for the git tag

        An example for public repositories might be:
        ```
        [{"name": "Github", "base_url": "https://github.com/{namespace}/{module}", "clone_url": "ssh://git@github.com:{namespace}/{module}.git", "browse_url": "https://github.com/{namespace}/{module}/tree/{tag}/{path}"},
        {"name": "Bitbucket", "base_url": "https://bitbucket.org/{namespace}/{module}", "clone_url": "ssh://git@bitbucket.org:{namespace}/{module}-{provider}.git", "browse_url": "https://bitbucket.org/{namespace}/{module}-{provider}/src/{tag}/{path}"},
        {"name": "Gitlab", "base_url": "https://gitlab.com/{namespace}/{module}", "clone_url": "ssh://git@gitlab.com:{namespace}/{module}-{provider}.git", "browse_url": "https://gitlab.com/{namespace}/{module}-{provider}/-/tree/{tag}/{path}"}]
        ```
        """
        return os.environ.get('GIT_PROVIDER_CONFIG', '[]')

    @property
    def ALLOW_CUSTOM_GIT_URL_MODULE_PROVIDER(self):
        """
        Whether module providers can specify their own git repository source.
        """
        return self.convert_boolean(os.environ.get('ALLOW_CUSTOM_GIT_URL_MODULE_PROVIDER', 'True'))

    @property
    def ALLOW_CUSTOM_GIT_URL_MODULE_VERSION(self):
        """
        Whether module versions can specify git repository in terrareg config.
        """
        return self.convert_boolean(os.environ.get('ALLOW_CUSTOM_GIT_URL_MODULE_VERSION', 'True'))

    @property
    def TERRAFORM_EXAMPLE_VERSION_TEMPLATE(self):
        """
        Template of version number string to be used in terraform examples in the UI.
        This is used by the snippet example of a terraform module and the 'resource builder' example.

        The template can contain the following placeholders:
         * `{major}`, `{minor}`, `{patch}`
         * `{major_minus_one}`, `{minor_minus_one}`, `{patch_minus_one}`
         * `{major_plus_one}`, `{minor_plus_one}`, `{patch_plus_one}`

        Some examples:
         * `>= {major}.{minor}.{patch}, < {major_plus_one}.0.0`
         * `~> {major}.{minor}.{patch}`

        For more information, see terraform documentation: https://www.terraform.io/language/expressions/version-constraints

        """
        return os.environ.get('TERRAFORM_EXAMPLE_VERSION_TEMPLATE', '{major}.{minor}.{patch}')

    @property
    def AUTOGENERATE_MODULE_PROVIDER_DESCRIPTION(self):
        """
        Whether to automatically generate module provider descriptions, if they are not provided in terrareg metadata file of the module.
        """
        return self.convert_boolean(os.environ.get('AUTOGENERATE_MODULE_PROVIDER_DESCRIPTION', 'True'))

    @property
    def AUTOGENERATE_USAGE_BUILDER_VARIABLES(self):
        """
        Whether to automatically generate usage builder variables from the required variables and their descriptions.
        When disabled, the usage builder will only be displayed on a module when the "variable_template" section
        of the terrareg.json metadata file is populated.
        """
        return self.convert_boolean(os.environ.get('AUTOGENERATE_USAGE_BUILDER_VARIABLES', 'True'))

    @property
    def ENABLE_SECURITY_SCANNING(self):
        """
        Whether to perform security scans of uploaded modules and display them against the module, submodules and examples.
        """
        return self.convert_boolean(os.environ.get('ENABLE_SECURITY_SCANNING', 'True'))

    @property
    def INFRACOST_API_KEY(self):
        """
        API key for Infracost.

        Set this to enable cost-analysis of module examples.

        To generate an API key:
        Log in at https://dashboard.infracost.io > select your organization > Settings
        """
        return os.environ.get('INFRACOST_API_KEY', None)

    @property
    def INFRACOST_PRICING_API_ENDPOINT(self):
        """
        Self-hosted infracost pricing API endpoint.

        For information on self-hosting the infracost pricing API, see https://www.infracost.io/docs/cloud_pricing_api/self_hosted/
        """
        return os.environ.get('INFRACOST_PRICING_API_ENDPOINT', None)

    @property
    def INFRACOST_TLS_INSECURE_SKIP_VERIFY(self):
        """
        Whether to skip TLS verification for self-hosted pricing endpoints
        """
        return self.convert_boolean(os.environ.get('INFRACOST_TLS_INSECURE_SKIP_VERIFY', 'False'))

    def convert_boolean(self, string):
        """Convert boolean environment variable to boolean."""
        if string.lower() in ['true', 'yes', '1']:
            return True
        elif string.lower() in ['false', 'no', '0']:
            return False

        raise InvalidBooleanConfigurationError('Boolean config value not valid. Must be one of: true, yes, 1, false, no, 0')
