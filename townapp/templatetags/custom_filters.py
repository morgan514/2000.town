from django import template
import re
from django.urls import reverse
from django.utils.html import mark_safe

register = template.Library()

@register.filter
def parse_mentions(value):
    mention_pattern = r'(?:(?<=\s)|(?<=^)|(?<=\W))@([\w.-]+@[\w.-]+|[\w.-]+)'

    def replace_mentions(match):
        mention_text = match.group(0)

        if '@' in mention_text and '.' in mention_text:    
            return f'<a href="mailto:{mention_text}">{mention_text}</a>'

        username = match.group(1)

        user_profile_url = reverse('user', args=[username])
        return f'<a href="{user_profile_url}">@{username}</a>'

    return re.sub(mention_pattern, replace_mentions, value)

@register.filter
def parse_hashtags(value):
    hashtag_pattern = r'(?<!&)(#(\w+))'

    url_pattern = r'(https?://\S+|www\.\S+)'

    def replace_hashtags(match):
        tag = match.group(2)

        tag_url = reverse('tagged', args=[tag]).lower()
        return f'<a href="{tag_url}">#{tag}</a>'

    parts = re.split(url_pattern, value)  

    for i, part in enumerate(parts):
        if not re.match(url_pattern, part): 
            parts[i] = re.sub(hashtag_pattern, replace_hashtags, part)

    return ''.join(parts) 