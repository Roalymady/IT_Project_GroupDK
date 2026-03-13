from django.db import migrations, models
from django.db.models import Count, Max


def dedupe_orders(apps, schema_editor):
    # Remove duplicate (user, groupbuy) rows so the unique constraint can be applied safely.
    Order = apps.get_model("groupbuy", "Order")

    duplicates = (
        Order.objects.values("user_id", "groupbuy_id")
        .annotate(row_count=Count("id"), keep_id=Max("id"))
        .filter(row_count__gt=1)
    )

    for dup in duplicates:
        Order.objects.filter(user_id=dup["user_id"], groupbuy_id=dup["groupbuy_id"]).exclude(id=dup["keep_id"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("groupbuy", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(dedupe_orders, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.UniqueConstraint(fields=("user", "groupbuy"), name="uniq_order_user_groupbuy"),
        ),
    ]
