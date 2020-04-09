import setuptools

setuptools.setup(
    name='datacatalog-tag-manager',
    version='0.1.2',
    author='Ricardo Mendes',
    author_email='ricardolsmendes@gmail.com',
    description='A package to manage Google Cloud Data Catalog tags,'
    ' loading metadata from external sources',
    platforms='Posix; MacOS X; Windows',
    packages=setuptools.find_packages(where='./src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'datacatalog-tag-manager = datacatalog_tag_manager:main',
        ],
    },
    include_package_data=True,
    install_requires=(
        'google-cloud-datacatalog',
        'pandas',
    ),
    setup_requires=('pytest-runner', ),
    tests_require=('pytest-cov', ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
