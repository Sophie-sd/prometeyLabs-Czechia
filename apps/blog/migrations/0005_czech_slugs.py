"""Rename 14 blog slugs to Czech (apps.blog.slug_map) and rewrite internal links in content. Idempotent."""
from django.db import migrations

from apps.blog.slug_map import OLD_TO_NEW, replace_old_slugs

TEXT_FIELDS = ('content', 'content_cs', 'content_en', 'content_ru', 'excerpt', 'excerpt_cs', 'excerpt_en')


def forwards(apps, schema_editor):
    Post = apps.get_model('blog', 'BlogPost')
    for old, new in OLD_TO_NEW.items():
        if not Post.objects.filter(slug=new).exists():
            Post.objects.filter(slug=old).update(slug=new)
    for post in Post.objects.all():
        changed = []
        for f in TEXT_FIELDS:
            if not hasattr(post, f):
                continue
            val = getattr(post, f)
            new_val = replace_old_slugs(val)
            if new_val != val:
                setattr(post, f, new_val)
                changed.append(f)
        if changed:
            post.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [('blog', '0004_blogpost_content_cs_blogpost_content_en_and_more')]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
