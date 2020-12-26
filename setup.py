import setuptools

setuptools.setup(
    name='datacatalog-tag-manager',
    version='2.0.6',
    url='https://github.com/ricardolsmendes/datacatalog-tag-manager',
    author='Ricardo Mendes',
    author_email='ricardolsmendes@gmail.com',
    license='MIT',
    description='A package to manage Google Cloud Data Catalog tags,'
    ' loading metadata from external sources',
    platforms='Posix; MacOS X; Windows',
    packages=setuptools.find_packages(where='./src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'datacatalog-tags = datacatalog_tag_manager:main',
        ],
    },
    include_package_data=True,
    install_requires=(
        'google-cloud-datacatalog ~= 1.0',
        'numpy >= 1.19.0, <= 1.19.3',
        'pandas ~= 1.1.4',
    ),
    setup_requires=('pytest-runner', ),
    tests_require=('pytest-cov', ),
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
