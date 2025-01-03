from datetime import datetime, timedelta
from django import template

register = template.Library()

@register.filter
def has_recent_activity(blog_post):
    now = datetime.now()
    twelve_hours_ago = now - timedelta(hours=12)
    
    return blog_post.recent_activity_time is not None and blog_post.recent_activity_time >= twelve_hours_ago
