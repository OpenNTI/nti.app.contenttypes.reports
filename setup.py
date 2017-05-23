from setuptools import setup, find_packages
import codecs

VERSION = '0.0.0'

entry_points = {
	"z3c.autoinclude.plugin": [
		'target = nti.app',
	],
}

tests_require = [
	'nti.app.testing'
]

setup(
	name='nti.app.contenttypes.reports',
	version=VERSION,
	author='NextThought',
	author_email='austin.graham@nextthought.com',
	description="Report generation for reportable objects",
	long_description=codecs.open('README.rst', encoding='utf-8').read(),
	license='Proprietary',
	keywords='pyramid reportlab courses reporting',
	classifiers=[
		'Framework :: Pyramid',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: Implementation :: CPython'
	],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti', 'nti.app', 'nti.app.contenttypes'],
	install_requires=[
		'setuptools',
		'z3c.rml',
		'z3c.macro',
		'z3c.pagelet',
		'z3c.template',
		'zope.viewlet',
		'zope.contentprovider',
		'nti.app.pyramid_zope'
	],
	extras_require={
		'test': tests_require,
	},
	entry_points=entry_points
)
