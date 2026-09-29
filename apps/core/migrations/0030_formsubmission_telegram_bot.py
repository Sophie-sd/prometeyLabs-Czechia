# Generated manually for telegram-bot form_type choice.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_proposal_cms_visuals'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formsubmission',
            name='form_type',
            field=models.CharField(
                choices=[
                    ('manual', 'Ручна заявка'),
                    ('site-request', 'Заявка на розробку сайту'),
                    ('developer', 'Заявка на курси'),
                    ('consultation', 'Заявка на консультацію'),
                    ('contact', 'Заявка зі сторінки контактів'),
                    ('call-request', 'Замовлення дзвінка'),
                    ('footer-consultation', 'Заявка з футера'),
                    ('test_result', 'Результат тесту калькулятора'),
                    ('tz_generator', 'Генератор ТЗ для сайту'),
                    ('telegram-bot', 'Заявка на Telegram-бота'),
                ],
                db_index=True,
                default='manual',
                max_length=30,
                verbose_name='Тип форми',
            ),
        ),
    ]
