# -*- coding: utf-8 -*-
# author: itimor

from celery import shared_task
from croniter import croniter
from django.utils import timezone
from datetime import datetime, timedelta
from celery_tasks.models import *
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.conf import settings
import pytz
from utils.index import gen_time_pid
import subprocess


@shared_task
def get_task():
    """
    获取所有任务脚本，并执行
    """
    now = timezone.now()
    # 前一天
    start = now - timedelta(hours=23, minutes=59, seconds=59)
    tz = pytz.timezone(settings.TIME_ZONE)
    local_date = tz.localize(now)
    all_task = Task.objects.filter(status=True, start_time__lt=start, expire_time__gt=start)
    for task in all_task:
        iter = croniter(task.cron, local_date)
        t = iter.get_next(datetime)
        cron_obj, created = CrontabSchedule.objects.get_or_create(minute=t.minute, hour=t.hour, day_of_month=t.month, month_of_year=t.year, timezone=settings.TIME_ZONE)
        kwargs = dict()
        kwargs['type'] = task.code_type
        kwargs['code'] = task.code
        kwargs['args'] = task.args
        PeriodicTask.objects.create(
            name=task.name,
            task='celery_tasks.tasks.run_task',
            kwargs=kwargs,
            enabled=True,
            one_off=True,
            crontab=cron_obj,
            start_time=t
        )
        task.save()


@shared_task
def run_task(**kwargs):
    script_type = kwargs['type']
    script_code = kwargs['code']
    script_args = kwargs['args']
    script_name = "/tmp/" + gen_time_pid(type)
    with open(script_name, 'w') as fn:
        fn.read(script_code)

    if script_type == 'shell':
        r = subprocess.check_output(["basn", script_name, script_args], shell=True)
    elif script_type == 'python':
        r = subprocess.check_output(["python", script_name, script_args], shell=True)
    else:
        r = 'error'
    return r
