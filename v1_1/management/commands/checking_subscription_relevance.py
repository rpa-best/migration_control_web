# from django.core.management.base import BaseCommand
# from migration_control_web.celery import app
# from celery.bin import beat
# from ...models.subscription import checking_subscription_relevance
#
#
# class Command(BaseCommand):
#     help = 'Run continuous task to check subscription relevance'
#
#     def handle(self, *args, **options):
#         checking_subscription_relevance.apply_async(countdown=0, eta=None)


#
# class Command(BaseCommand):
#     help = 'Start Celery Beat'
#
#     def handle(self, *args, **options):
#         beat.Program(app=app).run()