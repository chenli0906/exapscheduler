from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from common.statuscode import JobStatus
from exapscheduler import scheduler_logger


def set_job_status_listener(event):
    from exapscheduler.scheduler_apis import exscheduler
    if event.code == EVENT_JOB_SUBMITTED:
        scheduler_logger.info("Job[%s] was submitted to be run" % event.job_id)
        exscheduler.setjobstatus(event.job_id, JobStatus.RUNNING)
    elif event.code == EVENT_JOB_EXECUTED:
        scheduler_logger.info("Job[%s] was executed successfully" % event.job_id)
        exscheduler.setjobstatus(event.job_id, JobStatus.SCHEDULING)
    elif event.code == EVENT_JOB_ERROR:
        scheduler_logger.info("Job[%s] was executed failed" % event.job_id)
        exscheduler.setjobstatus(event.job_id, JobStatus.SCHEDULING)


def job_finish_listener(event):
    from exapscheduler.scheduler_apis import historyjobmanager, get_history_job_info
    jobinfo = get_history_job_info(event)
    historyjobmanager.add_history_job(**jobinfo)
