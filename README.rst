===================
ExAPScheduler
===================

Extended Advanced Python Scheduler (ExAPScheduler) is an extension task scheduling system based on APScheduler

Use setuptools to `publish to artifactory <https://www.jfrog.com/confluence/display/RTF/PyPI+Repositories#PyPIRepositories-PublishingtoArtifactory>`_

Create the $HOME/.pypirc File:

::

    [distutils]
    index-servers =
        local
        pypi
     
    [pypi]
    repository: https://pypi.python.org/pypi
    username: mrBagthrope
    password: notToBeSeen
     
    [local]
    repository: http://localhost:8081/artifactory/api/pypi/pypi-local
    username: admin
    password: password



then run the command:

::

    python setup.py sdist upload -r local


use pip to resolve from Artifactory

::

    pip install -i http://localhost:8081/artifactory/api/pypi/pypi-local/simple ExAPScheduler


put schedulerconfig.yml to your project root path