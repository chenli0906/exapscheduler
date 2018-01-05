import yaml
from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.util import datetime_repr
from exapscheduler.common.statuscode import JobStatus

from exapscheduler.common.utils import trigger_str_to_dict

from exapscheduler import scheduler_logger
from exapscheduler.eventshandler import set_job_status_listener, job_finish_listener
from exapscheduler.historyjob import HistoryJobManager
from scheduler import ExScheduler

exscheduler = ExScheduler()

historyjobmanager = HistoryJobManager()


def start_scheduler(config_path):
    scheduler_logger.info("Starting scheduler!")
    config = {}
    try:
        stream = file(config_path, 'r')
        config = yaml.load(stream)
    except IOError as e:
        scheduler_logger.warn(e)
    finally:
        dburl = config.get('jobstores', {}).get('db_url', 'sqlite:///jobs.sqlite')
        thread_pool_max = config.get('executors', {}).get('thread_pool_max_workers', 20)
        process_pool_max = config.get('executors', {}).get('process_pool_max_workers', 5)
        misfire_grace_time = config.get('jobdefaults', {}).get('misfire_grace_time', 600)
        coalesce = config.get('jobdefaults', {}).get('coalesce', False)
        max_instances = config.get('jobdefaults', {}).get('max_instances', 1)

    jobstores = {
        'default': SQLAlchemyJobStore(url=dburl)
    }
    executors = {
        'default': ThreadPoolExecutor(thread_pool_max),
        'processpool': ProcessPoolExecutor(process_pool_max),
    }
    job_defaults = {
        'misfire_grace_time': misfire_grace_time,
        'coalesce': coalesce,
        'max_instances': max_instances
    }
    exscheduler.start_scheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
    exscheduler.addlistener(set_job_status_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_SUBMITTED)
    exscheduler.addlistener(job_finish_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler_logger.info("Start scheduler done!")

    scheduler_logger.info("Initializing history job database!")
    historyjobmanager.init_db(dburl)
    scheduler_logger.info("Initialize history job database done!")


def get_history_job_info(event):
    job = exscheduler.getjob(event.job_id)
    return {"id": str(job.id),
            "name": str(job.name),
            "kwargs": job.kwargs,
            "trigger": trigger_str_to_dict(str(job.trigger)),
            "last_run_time": datetime_repr(event.scheduled_run_time),
            "status": JobStatus.SUCCESS if event.code == EVENT_JOB_EXECUTED else JobStatus.FAILED
            }
