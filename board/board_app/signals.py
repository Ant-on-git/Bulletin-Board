import os
from random import randint

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from .models import AdFiles, Profile, OneTimeCode, Reply
from django.conf import settings


@receiver(post_delete, sender=AdFiles)
def file_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(post_save, sender=Profile)
def notify_subscribers_new_post(sender, instance, created, **kwargs):
    if created:
        new_code = OneTimeCode.objects.create(code=randint(1000, 9999), user=instance)

        html_email_message = render_to_string('email/hi_new_user.html',
                                              {'username': instance.username,
                                               'href': 'http://127.0.0.1:8000/confirmEmail',
                                               'code': new_code.code})
        msg = EmailMultiAlternatives(subject=f'Регистрация на сайте B-Board.com',
                                     from_email=settings.DEFAULT_FROM_EMAIL,
                                     to=[instance.email])
        msg.attach_alternative(html_email_message, 'text/html')
        try:
            msg.send()
        except Exception as e:
            print('ошибка при отправке письма:')
            print(e)


@receiver(post_save, sender=Reply)
def new_reply_notyfication(sender, instance, created, **kwargs):
    if created:
        html_email_message = render_to_string('email/new_reply_notyfication.html',
                                              {'username': instance.ad.user.username,
                                               'ad_title': instance.ad.title,
                                               'reply_author': instance.user.username,
                                               'reply_text': instance.text})
        msg = EmailMultiAlternatives(subject=f'Новый отклик на сайте B-Board.com',
                                     from_email=settings.DEFAULT_FROM_EMAIL,
                                     to=[instance.ad.user.email])
        msg.attach_alternative(html_email_message, 'text/html')
        try:
            msg.send()
        except Exception as e:
            print('ошибка при отправке письма:')
            print(e)


@receiver(pre_save, sender=Reply)
def reply_accepted_notyfication(sender, instance, **kwargs):
    if instance.id is None: # new object will be created
        pass
    previous_reply_version = Reply.objects.get(id=instance.id)
    if previous_reply_version.accepted < 1 and instance.accepted == 1:  # если был принят отклик
        html_email_message = render_to_string('email/reply_accepted_notyfication.html',
                                              {'username': instance.user.username,
                                               'ad_title': instance.ad.title,
                                               'ad_author': instance.ad.user.username})
        msg = EmailMultiAlternatives(subject=f'Отклик на сайте B-Board.com принят!',
                                     from_email=settings.DEFAULT_FROM_EMAIL,
                                     to=[instance.user.email])
        msg.attach_alternative(html_email_message, 'text/html')
        try:
            msg.send()
        except Exception as e:
            print('ошибка при отправке письма:')
            print(e)