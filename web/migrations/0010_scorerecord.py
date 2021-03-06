# Generated by Django 2.2.3 on 2020-08-18 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_auto_20200818_0545'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoreRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='理由')),
                ('score', models.IntegerField(help_text='违纪扣分写负值，表现邮寄加分写正值', verbose_name='分值')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='web.Student', verbose_name='学生')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='web.UserInfo', verbose_name='执行人')),
            ],
        ),
    ]
