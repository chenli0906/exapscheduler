import re


def singleton(cls):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


# cron[day_of_week=2, hour=10] to {'day_of_week':'2', 'hour':'10'}
def trigger_str_to_dict(triggerstr):
    d = {}
    for ele in re.compile(r'\[(.*?)\]').findall(triggerstr)[0].split(', '):
        kw = ele.split('=')
        d[kw[0].strip()] = kw[1].replace("'", "")
    return d