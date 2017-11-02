from setuptools import setup, find_packages

setup(
    name='cms',
    version='1.0.0',
    packages=find_packages(exclude=['data', 'events', 'file_server']),
    url='http://www.curwsl.org',
    license='Apache 2.0',
    author='Gihan Karunarathne',
    author_email='gihan.09@cse.mrt.ac.lk',
    description='CMS Server Utilities',
    requires=['shapely', 'joblib', 'netCDF4', 'matplotlib', 'imageio', 'scipy', 'geopandas'],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'unittest2',
    ],
)
