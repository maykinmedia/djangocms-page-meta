# Generated by Django 1.11.9 on 2018-01-08 22:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_page_meta", "0009_auto_20171230_1954"),
    ]

    operations = [
        migrations.AlterField(
            model_name="titlemeta",
            name="description",
            field=models.CharField(blank=True, default="", max_length=2000),
        ),
        migrations.AlterField(
            model_name="titlemeta",
            name="gplus_description",
            field=models.CharField(blank=True, default="", max_length=2000, verbose_name="Google+ Description"),
        ),
        migrations.AlterField(
            model_name="titlemeta",
            name="keywords",
            field=models.CharField(blank=True, default="", max_length=2000),
        ),
        migrations.AlterField(
            model_name="titlemeta",
            name="og_description",
            field=models.CharField(blank=True, default="", max_length=2000, verbose_name="Facebook Description"),
        ),
        migrations.AlterField(
            model_name="titlemeta",
            name="twitter_description",
            field=models.CharField(blank=True, default="", max_length=2000, verbose_name="Twitter Description"),
        ),
    ]
