from distutils.command import clean
from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm,PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm,PasswordResetForm
from .models import BlogPost, UserProfile, Comment,Theme
from django.forms import TextInput
from captcha.fields import CaptchaField
from colorfield.widgets import ColorWidget
import os
from django.core.exceptions import ValidationError

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    captcha=CaptchaField()

    class Meta:
        model = User
        
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    pass


class CustomPasswordResetForm(PasswordResetForm):
    pass


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'image','embed','tags']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['autofocus'] = False 

class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ['background_color', 'text_color', 'link_color', 'font_family', 'custom_font']
        widgets = {
            'background_color': ColorWidget,
            'text_color': ColorWidget,
            'link_color': ColorWidget,
        }

    def clean_custom_font(self):
        custom_font = self.cleaned_data.get('custom_font')
        if custom_font:
            valid_extensions = ['.ttf', '.otf', '.woff', '.woff2','.ttc']
            extension = os.path.splitext(custom_font.name)[1]
            if not extension.lower() in valid_extensions:
                raise ValidationError('Unsupported file extension. Please upload a TTF, OTF, WOFF, or WOFF2 font file.')
        return custom_font

class CustomUserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password')
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['autofocus'] = False 


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['autofocus'] = False 


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'image','embed'] 


class BlogPostFilterForm(forms.Form):
    FILTER_CHOICES = (
        ('recent_activity', 'Recent Activity'),
        ('chronological', 'Chronological'),
        ('comment_count', 'Most Comments')
        ,
    )

    filter_option = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )