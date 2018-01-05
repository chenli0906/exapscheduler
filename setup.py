import os
from setuptools import setup, find_packages

here = os.path.dirname(__file__)
readme_path = os.path.join(here, 'README.rst')
readme = open(readme_path).read()

setup(
    name='ExAPScheduler',
    version='1.0',
    url='',
    description='Extended APScheduler',
    long_description=readme,
    packages=find_packages(exclude=['exapscheduler.test']),
    license='MIT',
    author='chen li',
    author_email='C_L_0312@qq.com',
    install_requires=['APScheduler == 3.3.0', 'sqlalchemy >= 0.8', 'PyYAML == 3.12'],
    dependency_links=[
        'https://artsz.zte.com.cn/artifactory/api/pypi/zxvmax-r-pypi/simple/APScheduler',
        'https://artsz.zte.com.cn/artifactory/api/pypi/zxvmax-r-pypi/simple/sqlalchemy',
        'https://artsz.zte.com.cn/artifactory/api/pypi/zxvmax-r-pypi/simple/PyYAML',
    ],
    zip_safe=False,
    keywords=["APScheduler"],
)
