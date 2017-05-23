import codecs
from setuptools import setup, find_packages

entry_points = {
    "z3c.autoinclude.plugin": [
        'target = nti.app',
    ],
}


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()

setup(
    name='nti.app.contenttypes.reports',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Application Report Content Types",
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    license='Apache',
    keywords='pyramid content types reports',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti', 'nti.app', 'nti.app.contenttypes'],
    install_requires=[
        'setuptools',
        'nti.contenttypes.reports',
    ],
    entry_points=entry_points,
    test_suite="nti.app.contenttypes.reports.tests",
)
