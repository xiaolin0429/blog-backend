# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0004_post_allow_comment_post_pinned"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE post_post ALTER COLUMN excerpt DROP NOT NULL;
            ALTER TABLE post_post ALTER COLUMN auto_save_content DROP NOT NULL;
            ALTER TABLE post_post ALTER COLUMN auto_save_title DROP NOT NULL;
            ALTER TABLE post_post ALTER COLUMN auto_save_excerpt DROP NOT NULL;
            ALTER TABLE post_post ALTER COLUMN auto_save_time DROP NOT NULL;
            ALTER TABLE post_post ALTER COLUMN published_at DROP NOT NULL;
            ALTER TABLE post_post ALTER COLUMN deleted_at DROP NOT NULL;
            """,
            reverse_sql="""
            ALTER TABLE post_post ALTER COLUMN excerpt SET NOT NULL;
            ALTER TABLE post_post ALTER COLUMN auto_save_content SET NOT NULL;
            ALTER TABLE post_post ALTER COLUMN auto_save_title SET NOT NULL;
            ALTER TABLE post_post ALTER COLUMN auto_save_excerpt SET NOT NULL;
            ALTER TABLE post_post ALTER COLUMN auto_save_time SET NOT NULL;
            ALTER TABLE post_post ALTER COLUMN published_at SET NOT NULL;
            ALTER TABLE post_post ALTER COLUMN deleted_at SET NOT NULL;
            """,
        ),
    ]
