from datetime import date, time

from django.db import migrations, models

from cms.parse_schedule import parse_event_date, parse_event_times


def forwards(apps, schema_editor):
    WorkshopEvent = apps.get_model("cms", "WorkshopEvent")
    for event in WorkshopEvent.objects.all():
        if hasattr(event, "date_display") and event.date_display:
            try:
                event.event_date = parse_event_date(event.date_display)
            except Exception:
                event.event_date = date.today()
        elif not event.event_date:
            event.event_date = date.today()

        if hasattr(event, "time_display") and event.time_display:
            start, end = parse_event_times(event.time_display)
            event.start_time = start
            event.end_time = end
        elif not event.start_time:
            event.start_time = time(10, 0)

        event.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="workshopevent",
            name="event_date",
            field=models.DateField(default=date.today),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshopevent",
            name="start_time",
            field=models.TimeField(default=time(10, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshopevent",
            name="end_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="workshopevent",
            name="date_display",
        ),
        migrations.RemoveField(
            model_name="workshopevent",
            name="time_display",
        ),
    ]
