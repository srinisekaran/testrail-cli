try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='testrail_cli',
    version='0.1',
    description='TestRail CLI.',
    author='Srinivaas Sekaran',
    author_email='srinivaas.web@gmail.com',
    url='https://github.com/ssrinivaas',
    py_modules=['trcli'],
    install_requires=[
        'Click',
    ]
)