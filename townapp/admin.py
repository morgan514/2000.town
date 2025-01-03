from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import BlogPost, UserProfile, ChatMessage, Comment, Challenge, Track
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.

class CommentAdmin(admin.StackedInline):
    list_display = ('id',)
    model = Comment

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date', 'pinned','recent_activity_time')
    list_filter = ('pinned',)
    search_fields = ('title', 'content')

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'image', 'tags', 'pinned'),
        }),
    )

    inlines = [
        CommentAdmin,
    ]



class ChatMessageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('timestamp','sender')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','bio')


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined') 
    ordering = ('-date_joined',) 


class TrackAdmin(SortableInlineAdminMixin,admin.StackedInline):
    list_display = ('rank','track_name','track_author')
    model = Track

class ChallengeAdmin(SortableAdminMixin,admin.ModelAdmin):
    list_display = ('name','date','slug')

    prepopulated_fields = {"slug": ("name",)}

    inlines = [
        TrackAdmin,
    ]



admin.site.register(BlogPost,BlogPostAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Challenge, ChallengeAdmin)

# admin.site.register(ChatMessage,ChatMessageAdmin)
# admin.site.unregister(Group)

