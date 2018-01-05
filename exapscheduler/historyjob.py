from collections import Mapping

import six
from sqlalchemy import Column
from sqlalchemy import LargeBinary
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base

from common.utils import singleton

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle

Base = declarative_base()


@singleton
class HistoryJobManager:
    def __init__(self):
        self.engine = None
        self.history_jobs = Table(
            'apscheduler_historyjobs', MetaData(),
            Column('jobid', Unicode(191, _warn_on_bytestring=False), nullable=False),
            Column('last_run_time', String(50), index=True, nullable=False),
            Column('historyjob_state', LargeBinary, nullable=False)
        )

    def init_db(self, dburl):
        self.engine = create_engine(dburl)
        self.history_jobs.create(self.engine, True)

    def drop_db(self):
        self.history_jobs.drop(self.engine, True)

    def add_history_job(self, **jobinfo):

        approved = {}

        if 'id' in jobinfo:
            value = jobinfo.pop('id')
            if not isinstance(value, six.string_types):
                raise TypeError("jobid must be a nonempty string")
            approved['id'] = value

        if 'name' in jobinfo:
            value = jobinfo.pop('name')
            if not value or not isinstance(value, six.string_types):
                raise TypeError("jobname must be a nonempty string")
            approved['name'] = value

        if 'type' in jobinfo:
            value = jobinfo.pop('type')
            if not isinstance(value, six.string_types):
                raise TypeError("jobtype must be a nonempty string")
            approved['type'] = value

        if 'kwargs' in jobinfo:
            value = jobinfo.pop('kwargs')
            if isinstance(value, six.string_types) or not isinstance(value, Mapping):
                raise TypeError('kwargs must be a dict-like object')
            approved['kwargs'] = value

        if 'trigger' in jobinfo:
            value = jobinfo.pop('trigger')
            if isinstance(value, six.string_types) or not isinstance(value, Mapping):
                raise TypeError('trigger must be a dict-like object')
            approved['trigger'] = value

        if 'last_run_time' in jobinfo:
            value = jobinfo.pop('last_run_time')
            if not isinstance(value, six.string_types):
                raise TypeError("last_run_time must be a nonempty string")
            approved['last_run_time'] = value

        if 'status' in jobinfo:
            value = jobinfo.pop('status')
            if not isinstance(value, six.string_types):
                raise TypeError("last_run_time must be a nonempty string")
            approved['status'] = value

        if jobinfo:
            raise AttributeError('The following are not modifiable attributes of Job: %s' %
                                 ', '.join(jobinfo))

        insert = self.history_jobs.insert().values(**{
            'jobid': approved['id'],
            'last_run_time': approved['last_run_time'],
            'historyjob_state': pickle.dumps(approved)
        })
        self.engine.execute(insert)

    def get_history_job_list(self, *conditions):
        jobs = []
        selectable = select(
            [self.history_jobs.c.jobid,
             self.history_jobs.c.historyjob_state]).order_by(self.history_jobs.c.last_run_time)
        selectable = selectable.where(*conditions) if conditions else selectable
        for row in self.engine.execute(selectable):
            jobs.append(pickle.loads(row.historyjob_state))
        return jobs

    def _remove_history_job(self, *conditions):
        deletable = self.history_jobs.delete()
        deletable = deletable.where(*conditions) if conditions else deletable
        self.engine.execute(deletable)

    def remove_all_history_job(self):
        self._remove_history_job()

    def remove_history_job_by_id_time(self, jobid, last_run_time):
        self._remove_history_job(
            and_(self.history_jobs.c.jobid == jobid, self.history_jobs.c.last_run_time == last_run_time))

