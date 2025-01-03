from io import BytesIO
from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from imagekit.models import ProcessedImageField,ImageSpecField
from imagekit.processors import ResizeToFit
from django.utils import timezone
from colorfield.fields import ColorField
from embed_video.fields import EmbedVideoField
from imagekit.cachefiles import ImageCacheFile
from imagekit.specs import ImageSpec
from PIL import Image
from django.core.files.base import ContentFile
# Create your models here.

class BlogPost(models.Model):
    rank = models.IntegerField(default=0)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(
        blank=True,
        null=True
    )
    thumbnail = ImageSpecField(source='image',processors=[ResizeToFit(600,600)],
                                           format='JPEG',
                                           options={'quality': 60},
                                           )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)
    embed = EmbedVideoField(blank=True)
    pinned = models.BooleanField(default=False)
    recent_activity_time = models.DateTimeField(null=True, blank=True,editable=True)

    def __str__(self):
        return self.title
    def is_gif(self):
        if self.image:
            return self.image.name.lower().endswith('.gif')
        return False
    class Meta:
        ordering = ("-id","rank")

#logic for rate limitng post
class UserPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    rank = models.IntegerField(default=0)
    text = models.TextField(blank=True)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        blank=True,
        null=True
    )
    embed = EmbedVideoField(blank=True)
    thumbnail = ImageSpecField(source='image',processors=[ResizeToFit(600,600)],
                                           format='JPEG',
                                           options={'quality': 60},
                                           )
    def process_image(self):
        try:
            exif_orientation = self.image._getexif().get(274, 1)
            if exif_orientation in [3, 6, 8]:
                img = Image.open(self.image)
                img = img.transpose(Image.Transpose.ROTATE_270)
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                self.image.save(self.image.name, ContentFile(img_io.getvalue()), save=False)
        except (AttributeError, KeyError, IndexError):
            pass

    class ThumbnailSpec(ImageSpec):
        processors = [ResizeToFit(600, 600)]
        format = 'JPEG'
        options = {'quality': 60}

    thumbnail = ImageSpecField(source='image', spec=ThumbnailSpec)
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'
    def is_gif(self):
        if self.image:
            return self.image.name.lower().endswith('.gif')
        return False
    class Meta:
        ordering = ("id","rank")

class UserProfile(models.Model):
    rank = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        blank=True,
        null=True
    )
    thumbnail = ImageSpecField(source='profile_picture',processors=[ResizeToFit(600,600)],
                                           format='JPEG',
                                           options={'quality': 60},
                                           )
    def is_gif(self):
        if self.profile_picture:
            return self.profile_picture.name.lower().endswith('.gif')
        return False
    def __str__(self):
        return self.user.username
    class Meta:
        ordering = ("user","rank")

class Theme(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    background_color = ColorField(default='#FFFFFF')
    text_color = ColorField(default='#000000')
    link_color = ColorField(default='#0000FF')
    FONT_CHOICES = [
        ('Times', 'Times'),
        ('Helvetica', 'Helvetica'),
        ('Courier', 'Courier'),
    ]
    font_family = models.CharField(max_length=100, choices=FONT_CHOICES, default='Times')
    custom_font = models.FileField(upload_to='fonts/', blank=True, null=True)

    class Meta:
        ordering = ("user", "id")
    


class ChatMessage(models.Model):
    content = models.TextField()
    sender = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp","-id")





class Challenge(models.Model):
    rank = models.IntegerField(default=0)
    name = models.CharField(blank=True,max_length=999)
    description = models.TextField(blank=True)
    date = models.CharField(blank=True,max_length=999)
    slug = models.SlugField(blank=True)
    ongoing = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ("-rank","name")


class Track(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)  
    rank = models.IntegerField(default=0)
    track_name = models.CharField(blank=True,max_length=999)
    track_author = models.CharField(blank=True,max_length=999)
    track_description = models.TextField(blank=True)
    audio = models.FileField(blank=True)

    def __str__(self):
        return self.track_name
    class Meta:
        ordering = ("-rank","track_name")