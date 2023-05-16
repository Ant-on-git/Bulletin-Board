import os
from random import randint

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from .models import AdFiles, Profile, OneTimeCode
from django.conf import settings


@receiver(post_delete, sender=AdFiles)
def file_delete(sender, instance, **kwargs):
    if type(instance.file) is str:
        file_path = instance.file
    else:
        file_path = os.path.join(instance.file.storage._wrapped.location, instance.file.name)
    os.remove(file_path)


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