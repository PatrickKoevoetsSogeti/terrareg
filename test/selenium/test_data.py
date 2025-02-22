
from datetime import datetime
import json

from terrareg.database import Database


integration_git_providers = {
    1: {
        'name': 'testgitprovider',
        'base_url_template': 'https://localhost.com/{namespace}/{module}-{provider}',
        'browse_url_template': 'https://localhost.com/{namespace}/{module}-{provider}/browse/{tag}/{path}',
        'clone_url_template': 'ssh://localhost.com/{namespace}/{module}-{provider}'
    },
    2: {
        'name': 'repo_url_tests',
        'base_url_template': 'https://base-url.com/{namespace}/{module}-{provider}',
        'browse_url_template': 'https://browse-url.com/{namespace}/{module}-{provider}/browse/{tag}/{path}suffix',
        'clone_url_template': 'ssh://clone-url.com/{namespace}/{module}-{provider}'
    },
    3: {
        'name': 'repo_url_tests_uri_encoded',
        'base_url_template': 'https://base-url.com/{namespace}/{module}-{provider}',
        'browse_url_template': 'https://browse-url.com/{namespace}/{module}-{provider}/browse/{path}?at={tag_uri_encoded}',
        'clone_url_template': 'ssh://clone-url.com/{namespace}/{module}-{provider}'
    },
    4: {
        'name': 'no_browse_url',
        'base_url_template': 'https://base-url.com/{namespace}/{module}-{provider}',
        'browse_url_template': None,
        'clone_url_template': 'ssh://clone-url.com/{namespace}/{module}-{provider}'
    }
}

one_namespace_test_data = {
    'testnamespace': {
        'onemodule': {'testprovider': {
            'id': 1,
            'versions': {'1.5.0': {'published': True}}
        }},
        'module-two': {'testprovider': {
            'id': 2,
            'versions': {'1.8.0': {'published': True}}
        }}
    }
}

integration_test_data = {
    'testnamespace': {
        'wrongversionorder': {'testprovider': {
            'id': 17,
            'versions': {
                '1.5.4': {'published': True}, '2.1.0': {'published': True}, '0.1.1': {'published': True},
                '10.23.0': {'published': True}, '0.1.10': {'published': True}, '0.0.9': {'published': True},
                '0.1.09': {'published': True}, '0.1.8': {'published': True},
                '23.2.3-beta': {'published': True, 'beta': True}, '5.21.2': {}
            }
        }}
    },
    'onlyunpublished': {
        'betamodule': {'test': {
            'id': 60,
            'versions': {
                '1.5.0': {'published': False}
            }
        }}
    },
    'onlybeta': {
        'betamodule': {'test': {
            'id': 61,
            'versions': {
                '1.4.0-beta': {'beta': True, 'published': True}
            }
        }}
    },
    'moduleextraction': {
        'test-module': { 'testprovider': {
            'id': 7,
            'repo_clone_url_template': 'ssh://example.com/repo.git'
        }},
        'bitbucketexample': {
            'testprovider': {
                'id': 8,
                'repo_clone_url_template': 'ssh://git@localhost:7999/bla/test-module.git',
                'git_tag_format': 'v{version}',
                'versions': []
            }
        },
        'gitextraction': {
            'staticrepourl': {
                'id': 9,
                'repo_clone_url_template': 'ssh://git@localhost:7999/bla/test-module.git',
                'git_tag_format': 'v{version}',
                'versions': []
            },
            'placeholdercloneurl': {
                'id': 10,
                'repo_clone_url_template': 'ssh://git@localhost:7999/{namespace}/{module}-{provider}.git',
                'git_tag_format': 'v{version}',
                'versions': []
            },
            'usesgitprovider': {
                'id': 11,
                'git_provider_id': 1,
                'git_tag_format': 'v{version}',
                'versions': []
            },
            'nogittagformat': {
                'id': 12,
                'git_provider_id': 1,
                'versions': []
            },
            'complexgittagformat': {
                'id': 13,
                'git_provider_id': 1,
                'git_tag_format': 'unittest{version}value',
                'versions': []
            },
            'norepourl': {
                'id': 14,
                'git_tag_format': 'v{version}',
                'versions': []
            }
        },
    },
    'real_providers': {
        'test-module': {
            'aws': {
                'id': 22,
                'versions': {
                    '1.0.0': {'published': True}
                }
            },
            'gcp': {
                'id': 23,
                'versions': {
                    '1.0.0': {'published': True}
                }
            },
            'null': {
                'id': 55,
                'versions': {
                    '1.0.0': {'published': True}
                }
            },
            'datadog': {
                'id': 59,
                'versions': {
                    '1.0.0': {'published': True}
                }
            },
            'doesnotexist': {
                'id': 24,
                'versions': {
                    '1.0.0': {'published': True}
                }
            }
        }
    },
    'repo_url_tests': {
        'no-git-provider': {'test': {
            'id': 18,
            'versions': {
                '1.0.0': {},
                '1.4.0': {
                    'repo_base_url_template': 'https://mv-base-url.com/{namespace}/{module}-{provider}',
                    'repo_browse_url_template': 'https://mv-browse-url.com/{namespace}/{module}-{provider}/browse/{tag}/{path}suffix',
                    'repo_clone_url_template': 'ssh://mv-clone-url.com/{namespace}/{module}-{provider}'
                }
            }
        }},
        'no-git-provider-uri-encoded': {'test': {
            'id': 46,
            'versions': {
                '1.4.0': {
                    'repo_base_url_template': 'https://mv-base-url.com/{namespace}/{module}-{provider}',
                    'repo_browse_url_template': 'https://mv-browse-url.com/{namespace}/{module}-{provider}/browse/{path}?at={tag_uri_encoded}',
                    'repo_clone_url_template': 'ssh://mv-clone-url.com/{namespace}/{module}-{provider}'
                }
            },
            'git_tag_format': 'release@test/{version}/'
        }},
        'git-provider-uri-encoded': {'test': {
            'id': 47,
            'versions': {
                '1.4.0': {}
            },
            'git_provider_id': 3,
            'git_tag_format': 'release@test/{version}/'
        }},
        'git-provider-urls': {'test': {
            'id': 19,
            'versions': {
                '1.1.0': {},
                '1.4.0': {
                    'repo_base_url_template': 'https://mv-base-url.com/{namespace}/{module}-{provider}',
                    'repo_browse_url_template': 'https://mv-browse-url.com/{namespace}/{module}-{provider}/browse/{tag}/{path}suffix',
                    'repo_clone_url_template': 'ssh://mv-clone-url.com/{namespace}/{module}-{provider}'
                }
            },
            'git_provider_id': 2
        }},
        'module-provider-urls': { 'test': {
            'id': 20,
            'versions': {
                '1.2.0': {},
                '1.4.0': {
                    'repo_base_url_template': 'https://mv-base-url.com/{namespace}/{module}-{provider}',
                    'repo_browse_url_template': 'https://mv-browse-url.com/{namespace}/{module}-{provider}/browse/{tag}/{path}suffix',
                    'repo_clone_url_template': 'ssh://mv-clone-url.com/{namespace}/{module}-{provider}'
                }
            },
            'repo_base_url_template': 'https://mp-base-url.com/{namespace}/{module}-{provider}',
            'repo_browse_url_template': 'https://mp-browse-url.com/{namespace}/{module}-{provider}/browse/{tag}/{path}suffix',
            'repo_clone_url_template': 'ssh://mp-clone-url.com/{namespace}/{module}-{provider}'
        }},
        'module-provider-override-git-provider': { 'test': {
            'id': 21,
            'versions': {
                '1.3.0': {},
                '1.4.0': {
                    'repo_base_url_template': 'https://mv-base-url.com/{namespace}/{module}-{provider}',
                    'repo_browse_url_template': 'https://mv-browse-url.com/{namespace}/{module}-{provider}/browse/{tag}/{path}suffix',
                    'repo_clone_url_template': 'ssh://mv-clone-url.com/{namespace}/{module}-{provider}'
                }
            },
            'repo_base_url_template': 'https://mp-base-url.com/{namespace}/{module}-{provider}',
            'repo_browse_url_template': 'https://mp-browse-url.com/{namespace}/{module}-{provider}/browse/{tag}/{path}suffix',
            'repo_clone_url_template': 'ssh://mp-clone-url.com/{namespace}/{module}-{provider}',
            'git_provider_id': 2
        }}
    },
    'modulesearch': {
        'contributedmodule-oneversion': {'aws': {
            'id': 25,
            'versions': {'1.0.0': {'published': True}}
        }},
        'contributedmodule-multiversion': {'aws': {
            'id': 26,
            'versions': {
                '1.2.3': {'published': True},
                '2.0.0': {'published': True}
            }
        }},
        'contributedmodule-withbetaversion': {'aws': {
            'id': 49,
            'versions': {
                '1.2.3': {'published': True},
                '2.0.0-beta': {'published': True, 'beta': True}
            }
        }},
        'contributedmodule-onlybeta': {'aws': {
            'id': 50,
            'versions': {
                '2.5.0-beta': {'published': True, 'beta': True}
            }
        }},
        'contributedmodule-differentprovider': {'gcp': {
            'id': 27,
            'versions': {
                '1.2.3': {'published': True}
            }
        }},
        'contributedmodule-unpublished': {'aws': {
            'id': 28,
            'versions': {
                '1.0.0': {}
            }
        }},
        'verifiedmodule-oneversion': {'aws': {
            'verified': True,
            'id': 29,
            'versions': {'1.0.0': {'published': True}}
        }},
        'verifiedmodule-withbetaversion': {'aws': {
            'id': 51,
            'versions': {
                '1.2.3': {'published': True},
                '2.0.0-beta': {'published': True, 'beta': True}
            }
        }},
        'verifiedmodule-onybeta': {'aws': {
            'id': 52,
            'versions': {
                '2.0.0-beta': {'published': True, 'beta': True}
            }
        }},
        'verifiedmodule-differentprovider': {'gcp': {
            'verified': True,
            'id': 31,
            'versions': {
                '1.2.3': {'published': True}
            }
        }},
        'verifiedmodule-unpublished': {'aws': {
            'verified': True,
            'id': 32,
            'versions': {
                '1.0.0': {}
            }
        }}
    },
    'modulesearch-contributed': {
        'mixedsearch-result': {'aws': {
            'id': 33,
            'versions': {'1.0.0': {'published': True}}
        }},
        'mixedsearch-result-multiversion': {'aws': {
            'id': 34,
            'versions': {
                '1.2.3': {'published': True},
                '2.0.0': {'published': True}
            }
        }},
        'mixedsearch-result-unpublished': {'aws': {
            'id': 35,
            'versions': {
                '1.2.3': {},
                '2.0.0': {}
            }
        }},
    },
    'modulesearch-trusted': {
        'mixedsearch-trusted-result': {'aws': {
            'id': 36,
            'versions': {'1.0.0': {'published': True}}
        }},
        'mixedsearch-trusted-second-result': {'datadog': {
            'id': 37,
            'versions': {
                '5.2.1': {'published': True},
            }
        }},
        'mixedsearch-trusted-result-multiversion': {'null': {
            'id': 38,
            'versions': {
                '1.2.3': {'published': True},
                '2.0.0': {'published': True}
            }
        }},
        'mixedsearch-trusted-result-unpublished': {'aws': {
            'id': 39,
            'versions': {
                '1.2.3': {},
                '2.0.0': {}
            }
        }},
        'mixedsearch-trusted-result-verified': {'gcp': {
            'id': 54,
            'verified': True,
            'versions': {
                '2.0.0': {'published': True}
            }
        }},
    },
    'searchbynamespace': {
        'searchbymodulename1': {
            'searchbyprovideraws': {
                'id': 40,
                'versions': {
                    '1.2.3': {'published': True}
                },
                'verified': True
            },
            'searchbyprovidergcp': {
                'id': 41,
                'versions': {
                    '2.0.0': {'published': True}
                }
            }
        },
        'searchbymodulename2': {
            'notpublished': {
                'id': 42,
                'versions': {'1.2.3': {}}
            },
            'published': {
                'id': 43,
                'versions': {
                    '3.1.6': {'published': True}
                }
            }
        }
    },
    'trustednamespace': {
        'secondlatestmodule': {'aws': {
            'id': 44,
            'versions': {'4.4.1': {'published': True}}
        }},
        'searchbymodulename4': {'aws': {
            'id': 45,
            'versions': {'5.5.5': {'published': True}}
        }}
    },
    'moduledetails': {
        'fullypopulated': {'testprovider': {
            'id': 56,
            'repo_base_url_template': 'https://mp-base-url.com/{namespace}/{module}-{provider}',
            'repo_browse_url_template': 'https://mp-browse-url.com/{namespace}/{module}-{provider}/browse/{tag}/{path}suffix',
            'repo_clone_url_template': 'ssh://mp-clone-url.com/{namespace}/{module}-{provider}',
            'versions': {
                # Older version
                '1.2.0': {'published': True},
                # Newer unpublished version
                '1.6.0': {},
                # Newer published beta version
                '1.6.1-beta': {'published': True, 'beta': True},
                # Unpublished and beta version
                '1.0.0-beta': {'published': False, 'beta': True},
                '1.5.0': {
                    'description': 'This is a test module version for tests.',
                    'owner': 'This is the owner of the module',
                    'repo_base_url_template': 'https://link-to.com/source-code-here',
                    'published': True,
                    'beta': False,
                    'internal': False,
                    'published_at': datetime(2022, 1, 5, 22, 53, 12),
                    'readme_content': '# This is an exaple README!',
                    'variable_template': json.dumps([
                        {
                            'name': 'name_of_application',
                            'type': 'text',
                            'quote_value': True,
                            'additional_help': 'Provide the name of the application'
                        }

                    ]),
                    'terraform_docs': json.dumps({
                        'header': '',
                        'footer': '',
                        'inputs': [
                            {
                                'name': 'name_of_application',
                                'type': 'string',
                                'description': 'Enter the application name',
                                'default': None,
                                'required': True
                            },
                            {
                                'name': 'string_with_default_value',
                                'type': 'string',
                                'description': 'Override the default string',
                                'default': 'this is the default',
                                'required': False
                            },
                            {
                                'name': 'example_boolean_input',
                                'type': 'bool',
                                'description': 'Override the truthful boolean',
                                'default': True,
                                'required': False
                            },
                            {
                                'name': 'example_list_input',
                                'type': 'list',
                                'description': 'Override the stringy list',
                                'default': ['value 1', 'value 2'],
                                'required': False
                            }
                        ],
                        'modules': [],
                        'outputs': [
                            {
                                'name': 'generated_name',
                                'description': 'Name with randomness'
                            },
                            {
                                'name': 'no_desc_output',
                                'description': None
                            }
                        ],
                        'providers': [
                            {
                                'name': 'random',
                                'alias': 'random-alias',
                                'version': '5.2.1'
                            },
                            {
                                'name': 'someothercompany/unsafe',
                                'alias': None,
                                'version': '2.0.0'
                            }
                        ],
                        'requirements': [],
                        'resources': [
                            {
                                'type': 'string',
                                'name': 'random_suffix',
                                'provider': 'random',
                                'source': 'hashicorp/random',
                                'mode': 'managed',
                                'version': 'latest',
                                'description': None
                            }
                        ]
                    }),
                    'examples': {
                        'examples/test-example': {
                            'example_files': {
                                'examples/test-example/data.tf': '# This contains data objects',
                                'examples/test-example/variables.tf': 'variable "test" {\n  description = "test variable"\n  type = string\n}',
                                'examples/test-example/main.tf': '# Call root module\nmodule "root" {\n  source = "../../"\n}'
                            },
                            'readme_content': '# Example 1 README',
                            'infracost': json.dumps({
                                'totalMonthlyCost': '61.536',
                                'totalHourlyCost': '0.0842958904109589',
                                'timeGenerated': '2022-08-17T18:39:55.964808023Z',
                                'currency': 'USD',
                                'diffTotalHourlyCost':
                                '0.0842958904109589',
                                'version': '0.2',
                                'pastTotalHourlyCost': '0',
                                'pastTotalMonthlyCost': '0',
                                'diffTotalMonthlyCost': '61.536',
                                'summary': {
                                    'totalNoPriceResources': 0,
                                    'unsupportedResourceCounts': {},
                                    'totalUsageBasedResources': 1,
                                    'totalUnsupportedResources': 0,
                                    'totalDetectedResources': 1,
                                    'totalSupportedResources': 1,
                                    'noPriceResourceCounts': {}
                                },
                                'projects': [
                                    {
                                        'pastBreakdown': {
                                            'totalMonthlyCost': '0',
                                            'totalHourlyCost': '0',
                                            'resources': []
                                        },
                                        'breakdown': {
                                            'totalMonthlyCost': '61.536',
                                            'totalHourlyCost': '0.0842958904109589',
                                            'resources': [
                                                {
                                                    'hourlyCost': '0.0842958904109589',
                                                    'name': 'aws_instance.test',
                                                    'monthlyCost': '61.536',
                                                    'costComponents': [
                                                        {
                                                            'hourlyCost': '0.0832',
                                                            'name': 'Instance usage (Linux/UNIX, on-demand, t3.large)',
                                                            'hourlyQuantity': '1',
                                                            'price': '0.0832',
                                                            'monthlyCost': '60.736',
                                                            'monthlyQuantity': '730',
                                                            'unit': 'hours'
                                                        },
                                                        {
                                                            'hourlyCost': '0',
                                                            'name': 'CPU credits',
                                                            'hourlyQuantity': '0',
                                                            'price': '0.05',
                                                            'monthlyCost': '0',
                                                            'monthlyQuantity': '0',
                                                            'unit': 'vCPU-hours'
                                                        }
                                                    ],
                                                    'subresources': [
                                                        {
                                                            'costComponents': [
                                                                {
                                                                    'hourlyCost': '0.0010958904109589',
                                                                    'name': 'Storage (general purpose SSD, gp2)',
                                                                    'hourlyQuantity': '0.010958904109589',
                                                                    'price': '0.1',
                                                                    'monthlyCost': '0.8',
                                                                    'monthlyQuantity': '8',
                                                                    'unit': 'GB'
                                                                }
                                                            ],
                                                            'hourlyCost': '0.0010958904109589',
                                                            'monthlyCost': '0.8',
                                                            'name': 'root_block_device',
                                                            'metadata': {}
                                                        }
                                                    ],
                                                    'metadata': {
                                                        'calls': [
                                                            {
                                                                'filename': 'main.tf',
                                                                'blockName': 'aws_instance.test'
                                                            }
                                                        ],
                                                        'filename': 'main.tf'
                                                    }
                                                }
                                            ]
                                        },
                                        'name': '2222/pub/terrareg/example/cost_example',
                                        'summary': {
                                            'totalNoPriceResources': 0,
                                            'unsupportedResourceCounts': {},
                                            'totalUsageBasedResources': 1,
                                            'totalUnsupportedResources': 0,
                                            'totalDetectedResources': 1,
                                            'totalSupportedResources': 1,
                                            'noPriceResourceCounts': {}
                                        },
                                        'diff': {
                                            'totalMonthlyCost': '61.536',
                                            'totalHourlyCost': '0.0842958904109589',
                                            'resources': [
                                                {
                                                    'hourlyCost': '0.0842958904109589',
                                                    'name': 'aws_instance.test',
                                                    'monthlyCost': '61.536',
                                                    'costComponents': [
                                                        {
                                                            'hourlyCost': '0.0832',
                                                            'name': 'Instance usage (Linux/UNIX, on-demand, t3.large)',
                                                            'hourlyQuantity': '1',
                                                            'price': '0.0832',
                                                            'monthlyCost': '60.736',
                                                            'monthlyQuantity': '730',
                                                            'unit': 'hours'
                                                        },
                                                        {
                                                            'hourlyCost': '0',
                                                            'name': 'CPU credits',
                                                            'hourlyQuantity': '0',
                                                            'price': '0.05',
                                                            'monthlyCost': '0',
                                                            'monthlyQuantity': '0',
                                                            'unit': 'vCPU-hours'
                                                        }
                                                    ],
                                                    'subresources': [
                                                        {
                                                            'costComponents': [
                                                                {
                                                                    'hourlyCost': '0.0010958904109589',
                                                                    'name': 'Storage (general purpose SSD, gp2)',
                                                                    'hourlyQuantity': '0.010958904109589',
                                                                    'price': '0.1',
                                                                    'monthlyCost': '0.8',
                                                                    'monthlyQuantity': '8',
                                                                    'unit': 'GB'
                                                                }
                                                            ],
                                                            'hourlyCost': '0.0010958904109589',
                                                            'monthlyCost': '0.8',
                                                            'name': 'root_block_device',
                                                            'metadata': {}
                                                        }
                                                    ],
                                                    'metadata': {}
                                                }
                                            ]
                                        },
                                        'metadata': {
                                            'path': '.',
                                            'type': 'terraform_dir',
                                            'vcsSubPath': 'example/cost_example'
                                        }
                                    }
                                ],
                                'metadata': {
                                    'commitTimestamp': '2022-08-17T06:58:57Z',
                                    'commitMessage': 'Add screenshot of example page to README',
                                    'vcsRepoUrl': 'https://gitlab.dockstudios.co.uk:2222/pub/terrareg.git',
                                    'commitAuthorName': 'Matthew John',
                                    'infracostCommand': 'breakdown',
                                    'branch': '226-investigate-showing-costs-of-each-module-examples',
                                    'commit': '4822f3af904200b26ff0a3399750c76d20007f6b',
                                    'commitAuthorEmail': 'matthew@dockstudios.co.uk'
                                    }
                                }
                            ),
                            'terraform_docs': json.dumps({
                                'header': '',
                                'footer': '',
                                'inputs': [
                                    {
                                        'name': 'input_for_example',
                                        'type': 'string',
                                        'description': 'Enter the example name',
                                        'default': None,
                                        'required': True
                                    }
                                ],
                                'modules': [],
                                'outputs': [
                                    {
                                        'name': 'example_output',
                                        'description': 'Example name with randomness'
                                    }
                                ],
                                'providers': [
                                    {
                                        'name': 'example_random',
                                        'alias': None,
                                        'version': None
                                    }
                                ],
                                'requirements': [],
                                'resources': [
                                    {
                                        'type': 'string',
                                        'name': 'example_random_suffix',
                                        'provider': 'example_random',
                                        'source': 'hashicorp/example_random',
                                        'mode': 'managed',
                                        'version': 'latest',
                                        'description': None
                                    }
                                ]
                            })
                        }
                    },
                    'submodules': {
                        'modules/example-submodule1': {
                            'readme_content': '# Submodule 1 README',
                            'terraform_docs': json.dumps({
                                'header': '',
                                'footer': '',
                                'inputs': [
                                    {
                                        'name': 'input_for_submodule',
                                        'type': 'string',
                                        'description': 'Enter the submodule name',
                                        'default': None,
                                        'required': True
                                    }
                                ],
                                'modules': [],
                                'outputs': [
                                    {
                                        'name': 'submodule_output',
                                        'description': 'Submodule name with randomness'
                                    }
                                ],
                                'providers': [
                                    {
                                        'name': 'submodule_random',
                                        'alias': None,
                                        'version': None
                                    }
                                ],
                                'requirements': [],
                                'resources': [
                                    {
                                        'type': 'string',
                                        'name': 'submodule_random_suffix',
                                        'provider': 'submodule_random',
                                        'source': 'hashicorp/submodule_random',
                                        'mode': 'managed',
                                        'version': 'latest',
                                        'description': None
                                    }
                                ]
                            })
                        }
                    }
                },
            }
        }},
        'infracost': {'testprovider': {
            'id': 68,
            'versions': {'1.0.0': {
                'published': True,
                'examples': {
                    'examples/with-cost': {
                        'infracost': json.dumps({
                            'totalMonthlyCost': '12.5123',
                        })
                    },
                    'examples/free': {
                        'infracost': json.dumps({
                            'totalMonthlyCost': '0.000',
                        })
                    },
                    'examples/no-infracost-data': {
                        'infracost': None
                    }
                }
            }}
        }},
        'withsecurityissues': {'testprovider': {
            'id': 62,
            'versions': {
                '1.2.0': {
                    'published': True,
                    'submodules': {
                        'modules/withanotherissue': {
                            'tfsec': json.dumps({
                                'results': [
                                    {'status': 0}
                                ]
                            })
                        }
                    }
                },
                '1.1.0': {
                    'published': True,
                    'examples': {
                        'examples/withsecissue': {
                            'tfsec': json.dumps({
                                'results': [
                                    {'status': 0},
                                    {'status': 0},
                                    {'status': 0}
                                ]
                            })
                        }
                    }
                },
                '1.0.0': {
                    'published': True,
                    'tfsec': json.dumps({
                        'results': [
                            {
                                'description': 'Secret explicitly uses the default key.',
                                'impact': 'Using AWS managed keys reduces the flexibility and '
                                        'control over the encryption key',
                                'links': [
                                    'https://aquasecurity.github.io/tfsec/v1.26.0/checks/aws/ssm/secret-use-customer-key/',
                                    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret#kms_key_id'
                                ],
                                'location': {
                                    'end_line': 4,
                                    'filename': 'main.tf',
                                    'start_line': 2
                                },
                                'long_id': 'aws-ssm-secret-use-customer-key',
                                'resolution': 'Use customer managed keys',
                                'resource': 'aws_secretsmanager_secret.this',
                                'rule_description': 'Secrets Manager should use customer managed '
                                                    'keys',
                                'rule_id': 'AVD-AWS-0098',
                                'rule_provider': 'aws',
                                'rule_service': 'ssm',
                                'severity': 'LOW',
                                'status': 0,
                                'warning': False
                            },
                            {
                                'description': 'Some security issue 2.',
                                'impact': 'Entire project is compromised',
                                'links': [
                                    'https://example.com/issuehere',
                                    'https://example.com/docshere'
                                ],
                                'location': {
                                    'end_line': 1,
                                    'filename': 'main.tf',
                                    'start_line': 6
                                },
                                'long_id': 'dodgy-bad-is-bad',
                                'resolution': 'Do not use bad code',
                                'resource': 'some_data_resource.this',
                                'rule_description': 'Dodgy code should be removed',
                                'rule_id': 'DDG-ANC-001',
                                'rule_provider': 'bad',
                                'rule_service': 'code',
                                'severity': 'HIGH',
                                'status': 0,
                                'warning': False
                            }
                        ]
                    })
                }
            }
        }},
        'noversion': {'testprovider': {
            'id': 57,
            'versions': {}
        }}
    },

    # Small namespace with module providers
    # with unpublished and beta versions
    'unpublished-beta-version-module-providers': {
        'publishedone': {
            'testprovider': {
                'id': 63,
                'versions': {
                    '2.1.1': {
                        'published': True,
                        'description': 'Test module description for testprovider'
                    }
                }
            },
            'secondprovider': {
                'id': 64,
                'versions': {
                    '2.2.2': {
                        'published': True,
                        'description': 'Description of second provider in module'
                    }
                }
            }
        },
        'noversions': {'testprovider': {
            'id': 67
        }},
        'onlybeta': {'testprovider': {
            'id': 65,
            'versions': {
                '2.2.4-beta': {
                    'published': True,
                    'beta': True,
                    'description': 'Test description'
                }
            }
        }},
        'onlyunpublished': {'testprovider': {
            'id': 66,
            'versions': {
                '1.0.0': {
                    'published': False,
                    'description': 'Test description'
                }
            }
        }}
    },

    ## THESE MUST BE AT THE BOTTOM
    'mostrecent': {
        'modulename': {'providername': {
            'id': 48,
            'versions': {'1.2.3': {'published': True}}
        }}
    },
    'mostrecentunpublished': {
        'modulename': {'providername': {
            'id': 53,
            'versions': {
                '1.2.3': {'published': False},
                '1.5.3-beta': {'published': True, 'beta': True}
            }
        }}
    }
}