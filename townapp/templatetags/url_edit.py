from django import template
register = template.Library()

def url_edit(text):
    return text.replace('<a ', '<a target="_blank" style="word-break:break-all;" ')

url_target_blank = register.filter(url_edit, is_safe = True)