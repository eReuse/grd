from setuptools import setup, find_packages


setup(
    name="ereuse-grd",
    version="0.1",
    packages=find_packages(),
    description = ('The Global Record of Devices (GRD) is a log of '
                   'information and traceability for any device, worldwide.'),
    url = 'https://github.com/eReuse/grd',
    author = 'eReuse team',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: System :: Logging',
        'Topic :: Utilities',
    ],
)
