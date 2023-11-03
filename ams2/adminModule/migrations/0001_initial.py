# Generated by Django 4.2.6 on 2023-11-02 04:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="HajriTable",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("att_date", models.DateField(default=django.utils.timezone.now)),
                ("stu_regno", models.CharField(max_length=15)),
                ("stu_name", models.CharField(max_length=40)),
                ("stu_roll_no", models.IntegerField()),
                ("course", models.CharField(max_length=40)),
                ("is_present", models.CharField(default="1", max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name="ProfessorsInfoTable",
            fields=[
                (
                    "pid",
                    models.CharField(
                        max_length=50, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("professor_name", models.CharField(max_length=40)),
                ("email", models.CharField(max_length=30)),
                ("phone_number", models.CharField(max_length=10)),
                ("code", models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name="ProfessorsTable",
            fields=[
                (
                    "cid",
                    models.CharField(
                        max_length=50, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("pid", models.CharField(max_length=40)),
                ("professor_name", models.CharField(max_length=40)),
                ("course_code", models.CharField(max_length=8)),
                ("course_num", models.CharField(max_length=8)),
                ("course_name", models.CharField(max_length=50)),
                ("semester", models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name="StudentsTable",
            fields=[
                ("regno", models.CharField(max_length=50, unique=True)),
                (
                    "uid",
                    models.CharField(
                        max_length=50, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("student_rollno", models.IntegerField()),
                ("student_name", models.CharField(max_length=40)),
                ("student_semster", models.CharField(max_length=1)),
                ("student_email", models.CharField(max_length=30)),
                ("i_grade", models.CharField(default="0", max_length=1)),
            ],
        ),
    ]