PACKAGE_NAME = 'arcana'
CODE_URL = f'https://github.com/australian-imaging-service/{PACKAGE_NAME}'

__authors__ = [
    ("Thomas G. Close", "tom.g.close@gmail.com")]

install_requires = [
    'xnat>=0.3.17',
    'pydra>=0.17',
    'pydra-dcm2niix>=1.0.0rc2',
    'pydra-mrtrix3>=0.1',
    'pydicom>=1.0.2',
    'nibabel>=3.2.1',
    'natsort>=7.1.1',
    'fasteners>=0.7.0',
    'docker>=5.0.2',
    'neurodocker==0.7.0',
    'deepdiff>=3.3',
    'importlib-metadata>=1.4']

tests_require = [
    'pytest>=5.4.3',
    'pytest-env>=0.6.2',
    'pytest-cov>=2.12.1',
    'xnat4tests>=0.1']

python_versions = ['3.8', '3.9']
