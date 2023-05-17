from django.core.management.base import BaseCommand
from django.conf import settings

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from ...models import Advertisement, Profile
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class Command(BaseCommand):
    help = "Runs users mail notifications about new advertisement on last week."

    def handle(self, *args, **options):
        try:
            created_scheduler = create_scheduler()
            logger = created_scheduler['logger']
            scheduler = created_scheduler['scheduler']

            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)



def create_scheduler():
    logger = logging.getLogger(__name__)

    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # добавляем работу нашему задачнику
    scheduler.add_job(
        send_week_posts_mail,
        trigger=CronTrigger(day_of_week='wed', hour='12', minute='20'),
        id="check_new_posts_for_weekly_notification",  # "Идентификатор", присвоенный каждому заданию, должен быть уникальным
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'my_job'.")

    # Каждый понедельник в 00:00 будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added weekly job: 'delete_old_job_executions'.")

    return {'logger': logger, 'scheduler': scheduler}


def send_week_posts_mail():
    adv_list = Advertisement.objects.filter(date__gte=timezone.now()-timedelta(days=7))
    if adv_list:
        for user in Profile.objects.all():
            html_email_message = render_to_string('email/week_adv_updates.html',
                                                  {'username': user.username, 'adv_list': adv_list})
            msg = EmailMultiAlternatives(
                subject='Новые объявления за неделю на B-Board.com',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_email_message, 'text/html')
            try:
                msg.send()
            except Exception as e:
                print('ошибка при отправке письма. возможно, ЯНДЕКС\РАМБЛЕР ПОСЧИТАЛ ПИСЬМО ЗА СПАМ и заблокировал почту на 24 часа')
                print(e)