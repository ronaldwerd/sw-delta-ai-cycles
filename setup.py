from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sw-delta-ai-cycles',
    version='0.1.0',
    description='Delta AI Cycles Machine',
    long_description=readme,
    author='signalwealth.ai',
    author_email='ronald.partridge@signalwealth.ai',
    url='https://www.signalwealth.ai',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
