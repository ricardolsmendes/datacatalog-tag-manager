from setuptools import find_namespace_packages, setup

packages = [package for package in find_namespace_packages(where='./src', include='datacatalog_tag_manager.*')]

setup(
    name='datacatalog-tag-manager',
    version='0.0.1',
    author='Ricardo Mendes',
    author_email='ricardolsmendes@gmail.com',
    description='A package to manage Google Cloud Data Catalog tags, loading metadata from external sources',
    platforms='Posix; MacOS X; Windows',
    packages=packages,
    package_dir={
        '': 'src'
    },
    include_package_data=True,
    install_requires=(
        'google-cloud-datacatalog',
        'pandas',
        'stringcase',
    ),
    setup_requires=(
        'pytest-runner',
    ),
    tests_require=(
        'pytest-cov',
    ),
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
