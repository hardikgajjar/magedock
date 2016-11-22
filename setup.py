"""
A tool to init Magento2 project with docker.
"""
from setuptools import find_packages, setup

dependencies = ['click', 'pathlib', 'clint', 'requests', 'jinja', 'docker-py>=1.10.4', 'dockerpty', 'PyYAML', 'click-help-colors']

setup(
    name='magedock',
    version='0.1.2',
    url='https://github.com/hardikgajjar/magedock',
    license='BSD',
    author='Hardik Gajjar',
    author_email='hardik.kwt@gmail.com',
    description='A tool to develop Magento2 project with docker.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'magedock = magedock.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
