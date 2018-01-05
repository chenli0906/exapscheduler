from apscheduler.events import EVENT_ALL
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import datetime_repr

from common.statuscode import JobStatus
from common.utils import singleton, trigger_str_to_dict


@singleton
class ExScheduler(object):
    def __init__(self):
        self.__scheduler = BackgroundScheduler()
        self.__jobstatuslist = {}

    def start_scheduler(self, **options):
        self.__scheduler.configure(**options)
        self.__scheduler.start()

    def shutdownscheduler(self):
        self.__scheduler.shutdown(wait=False)

    def getjob(self, jobid):
        return self.__scheduler.get_job(jobid)

    def scheduledjob(self, *args, **kw):
        return self.__scheduler.scheduled_job(*args, **kw)

    def addjob(self, *args, **kw):
        job = self.__scheduler.add_job(*args, **kw)
        self.__scheduler.wakeup()
        return job

    def removejob(self, job_id, jobstore=None):
        self.__scheduler.remove_job(job_id=job_id, jobstore=jobstore)

    def pausejob(self, job_id, jobstore=None):
        self.__scheduler.pause_job(job_id=job_id, jobstore=jobstore)
        self.setjobstatus(job_id, JobStatus.PAUSED)

    def resumejob(self, job_id, jobstore=None):
        self.__scheduler.resume_job(job_id=job_id, jobstore=jobstore)
        self.setjobstatus(job_id, JobStatus.SCHEDULING)

    def modifyjob(self, job_id, jobstore=None, **kw):
        job = self.__scheduler.modify_job(job_id=job_id, jobstore=jobstore, **kw)
        return job

    def getjoblist(self):
        joblist = self.__scheduler.get_jobs()
        return map(self._getjobinfo, joblist)

    def addlistener(self, callback, mask=EVENT_ALL):
        self.__scheduler.add_listener(callback, mask)

    def setjobstatus(self, jobid, jobstatus):
        self.__jobstatuslist[jobid] = jobstatus

    def jobstatusinitial(self, job_id, jobstore=None):
        job = self.__scheduler.get_job(job_id=job_id, jobstore=jobstore)
        if job_id not in self.__jobstatuslist:
            status = (JobStatus.SCHEDULING if job.next_run_time else JobStatus.PAUSED) if hasattr(job,
                                                                                                  'next_run_time') else JobStatus.PENDING
            self.setjobstatus(job_id, status)

    def _getjobinfo(self, job):
        self.jobstatusinitial(job.id)
        return {"id": str(job.id),
                "name": str(job.name),
                "kwargs": job.kwargs,
                "trigger": trigger_str_to_dict(str(job.trigger)),
                "next_run_time": datetime_repr(job.next_run_time) if self.__jobstatuslist[
                                                                         str(job.id)] == JobStatus.SCHEDULING or
                                                                     self.__jobstatuslist[
                                                                         str(job.id)] == JobStatus.RUNNING else "--",
                "status": self.__jobstatuslist[str(job.id)]}
