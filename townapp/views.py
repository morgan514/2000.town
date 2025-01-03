from django.http import Http404, HttpResponseForbidden,HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import (
    RegistrationForm,
    LoginForm,BlogPostForm,
    UserProfileForm, 
    CommentForm,
    BlogPostFilterForm,
    CustomPasswordResetForm,
    CustomUserEditForm,
    CustomPasswordChangeForm,
    ThemeForm
)
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import BlogPost, Theme, UserProfile, Comment,UserPost, Challenge, Track
from django.contrib.auth.models import User
from django.db.models import Q, Max, F, Case, When, Value, DateTimeField,Count
from django.views.generic import TemplateView, ListView
from taggit.models import Tag
from datetime import datetime, timedelta
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse, reverse_lazy
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.


def toggle_text_only_mode(request):
    if request.session.get('text_only_mode'):
        request.session['text_only_mode'] = False
    else:
        request.session['text_only_mode'] = True
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def home(request):
    current_time = timezone.now()
    threshold_time = current_time - timedelta(hours=12)
    
    filter_form = BlogPostFilterForm(request.GET)
    blog_posts = BlogPost.objects.all().select_related('author__userprofile')
    
    blog_posts = blog_posts.annotate(
        most_recent_activity=Max(
            Case(
                When(comment__created_at__isnull=False, then=F('comment__created_at')),
                default=F('date'),
                output_field=DateTimeField(),
            )
        )
    ).order_by('-pinned', '-most_recent_activity')
    
    if filter_form.is_valid():
        filter_option = filter_form.cleaned_data.get('filter_option')
        if filter_option == 'chronological':
            blog_posts = blog_posts.order_by('-date')
        elif filter_option == 'recent_activity':
            blog_posts = blog_posts.order_by('-most_recent_activity')
        elif filter_option == 'comment_count':
            blog_posts = blog_posts.annotate(comment_count=Count('comment')).order_by('-comment_count', '-date')
    
    blogposts = BlogPost.objects.all()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(blog_posts, 20)
    try:
        blog_posts = paginator.page(page)
    except PageNotAnInteger:
        blog_posts = paginator.page(1)
    except EmptyPage:
        blog_posts = paginator.page(paginator.num_pages)
    
    if request.user.is_authenticated:
        try:
            user_theme = Theme.objects.get(user=request.user)
        except Theme.DoesNotExist:
            user_theme = None
    else:
        user_theme = None 

    show_images = not 'noimg' in request.GET
    logged_out = request.GET.get('logged_out') == 'True'
    
    return render(request, 'home.html', {
        'blog_posts': blog_posts,
        'blogposts': blogposts,
        'user': request.user,
        'logged_out': logged_out,
        'filter_form': filter_form,
        'current_time': current_time,
        'threshold_time': threshold_time,
        'user_theme': user_theme,
        'show_images': show_images
    })

@login_required
def tagged(request,slug):
    filter_form = BlogPostFilterForm(request.GET)
    
    tag = get_object_or_404(Tag, slug=slug)
    blog_posts = BlogPost.objects.filter(tags=tag).select_related('author__userprofile')
    blog_posts = blog_posts.order_by('-recent_activity_time')

    if filter_form.is_valid():
        filter_option = filter_form.cleaned_data.get('filter_option')
        if filter_option == 'chronological':
            blog_posts = blog_posts.order_by('-date')
        elif filter_option == 'recent_activity':
           blog_posts = blog_posts.annotate(
                most_recent_activity=Max(
                    Case(
                        When(comment__created_at__isnull=False, then=F('comment__created_at')),
                        default=F('date'),
                        output_field=DateTimeField(),
                    )
                )
            ).order_by('-most_recent_activity')
        elif filter_option == 'comment_count':
            blog_posts = blog_posts.annotate(comment_count=Count('comment')).order_by('-comment_count','-date')

    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    logged_out = request.GET.get('logged_out') == 'True'
    return render(request, 'tag.html', {'blog_posts': blog_posts, 'user': request.user, 'logged_out': logged_out,'tag': tag,'filter_form': filter_form,'user_theme': user_theme})

@login_required
def post_blog(request):
    user = request.user
    now = timezone.now()

    hourly_rate_limit_duration = timedelta(hours=1)
    daily_rate_limit_duration = timedelta(days=1)
    hourly_allowed_posts = 2
    daily_allowed_posts = 3 

    recent_hourly_posts = UserPost.objects.filter(user=user, timestamp__gte=now - hourly_rate_limit_duration)

    if recent_hourly_posts.count() >= hourly_allowed_posts:
        return render(request, 'post_blog.html', {'form': None, 'rate_limit_message': "You have exceeded the hourly rate limit for posting. Please try again later."})

    recent_daily_posts = UserPost.objects.filter(user=user, timestamp__gte=now - daily_rate_limit_duration)

    if recent_daily_posts.count() >= daily_allowed_posts:
        return render(request, 'post_blog.html', {'form': None, 'rate_limit_message': "You have exceeded the daily rate limit for posting. Please try again later."})

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.recent_activity_time = timezone.now()
            blog_post.save()
            form.save_m2m()
            UserPost(user=request.user).save() 
            return redirect('home')
    else:
        form = BlogPostForm()

    try:
        user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
        user_theme = None

    return render(request, 'post_blog.html', {'form': form, 'user_theme': user_theme, 'rate_limit_message': ""})


@login_required
def post(request, id):
    blog_post = BlogPost.objects.get(pk=id)
    logged_out = request.GET.get('logged_out') == 'True'
    blog_post.author.userprofile = UserProfile.objects.get(user=blog_post.author)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment_text = form.cleaned_data['text']
            image = form.cleaned_data['image']
            embed = form.cleaned_data['embed']
            comment = Comment(text=comment_text, post=blog_post, user=request.user, image=image,embed=embed)
            comment.save()

            comment.process_image()

            blog_post.recent_activity_time = datetime.now()
            blog_post.save()

            return redirect('post', id=id)
    else:
        form = CommentForm()
    
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None

    sort_order = request.GET.get('sort', 'asc')

    if sort_order == 'asc':
        comments = Comment.objects.filter(post=blog_post).order_by('id')
    elif sort_order == 'desc':
        comments = Comment.objects.filter(post=blog_post).order_by('-id')
    else:
        raise Http404("Invalid comment order")
    

    return render(request, 'post.html', {'user': request.user, 'logged_out': logged_out, 'blog_post':blog_post, 'form': form,'user_theme': user_theme, 'comments': comments, 'sort_order': sort_order})

@login_required
def tags(request):
    tags = Tag.objects.annotate(post_count=Count('blogpost'))
    tags = tags.order_by("slug")
    Tag.objects.filter(blogpost=None).delete()
    logged_out = request.GET.get('logged_out') == 'True'
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(request, "tags.html", {'user': request.user, 'logged_out': logged_out, 'tags': tags,'user_theme': user_theme})

@login_required
def filter_by_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) 
        except ValueError:
            start_date = None
            end_date = None

    if start_date and end_date:
        blog_posts = BlogPost.objects.filter(date__range=(start_date, end_date)).select_related('author__userprofile')
    else:
        blog_posts = BlogPost.objects.all().select_related('author__userprofile')

    logged_out = request.GET.get('logged_out') == 'True'
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(
        request,
        'filter_by_date.html',
        {'blog_posts': blog_posts, 'user': request.user, 'logged_out': logged_out,'user_theme': user_theme}
    )

@login_required
def image(request, image):
    blog_post = BlogPost.objects.get(image=image)
    logged_out = request.GET.get('logged_out') == 'True'
    return render(request, 'image.html', {'user': request.user, 'logged_out': logged_out, 'blog_post':blog_post})

@login_required
def edit_post(request, id):
    blog_post = get_object_or_404(BlogPost, pk=id)

    if request.user != blog_post.author:
        return redirect('post', id=id)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog_post)
        if form.is_valid():
            form.save()
            return redirect('post', id=id)
    else:
        form = BlogPostForm(instance=blog_post)
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(request, 'edit_post.html', {'form': form, 'blog_post': blog_post,'user_theme': user_theme})


@login_required
def theme(request):
    theme, created = Theme.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        theme_form = ThemeForm(request.POST, request.FILES, instance=theme) 
        if theme_form.is_valid():
            theme_form.save()
            return redirect('theme')

    else:
        theme_form = ThemeForm(instance=theme)

    try:
        user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
        user_theme = None
    return render(request, 'theme.html', {'theme_form': theme_form,'user_theme': user_theme})

def reset_theme(request):
    if request.user.is_authenticated:
        user_theme = Theme.objects.filter(user=request.user).first()
        if user_theme:
            user_theme.background_color = '#FFFFFF'
            user_theme.text_color = '#000000'
            user_theme.link_color = '#0000FF'
            user_theme.font_family = 'Times New Roman'
            user_theme.custom_font.delete(save=False) 
            user_theme.custom_font = None
            user_theme.save()
    return HttpResponseRedirect(reverse('theme'))


@login_required
def delete_post(request, id):
    blog_post = get_object_or_404(BlogPost, pk=id)

    if request.user != blog_post.author:
        return redirect('post', id=id)

    if request.method == 'POST':
        blog_post.delete()
        return redirect('home')

    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(request, 'delete_post.html', {'blog_post': blog_post,'user_theme': user_theme})

class HomePageView(TemplateView):
    template_name = 'home.html'

class SearchResultsView(ListView):
    model = BlogPost
    template_name = 'search_results.html'
    

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query is not None:
            object_list = BlogPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(date__icontains=query) 
            )
            
        return object_list
    
@login_required
def user(request, username):
    filter_form = BlogPostFilterForm(request.GET)
    author_user = get_object_or_404(User, username=username)
    blog_posts = BlogPost.objects.filter(author=author_user)
    user_profile = UserProfile.objects.get(user=author_user)
    current_user = UserProfile.objects.get(user=request.user)
    blog_posts = blog_posts.annotate(
                most_recent_activity=Max(
                    Case(
                        When(comment__created_at__isnull=False, then=F('comment__created_at')),
                        default=F('date'),
                        output_field=DateTimeField(),
                    )
                )
            ).order_by('-most_recent_activity')
    if filter_form.is_valid():
        filter_option = filter_form.cleaned_data.get('filter_option')
        if filter_option == 'chronological':
            blog_posts = blog_posts.order_by('-date')
        elif filter_option == 'recent_activity':
           blog_posts = blog_posts.annotate(
                most_recent_activity=Max(
                    Case(
                        When(comment__created_at__isnull=False, then=F('comment__created_at')),
                        default=F('date'),
                        output_field=DateTimeField(),
                    )
                )
            ).order_by('-most_recent_activity')
        elif filter_option == 'comment_count':
            blog_posts = blog_posts.annotate(comment_count=Count('comment')).order_by('-comment_count','-date')
    logged_out = request.GET.get('logged_out') == 'True'
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(request, 'user.html', {'blog_posts': blog_posts, 'user': request.user,'author_user':author_user,'current_user':current_user, 'user_profile':user_profile, 'logged_out': logged_out,'filter_form': filter_form,'user_theme': user_theme})

@login_required
def users(request):
    users_list = User.objects.annotate(post_count=Count('blogpost'))
    users_list = User.objects.all()
    users_list = users_list.order_by('username')
    logged_out = request.GET.get('logged_out') == 'True'
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(request, 'users.html', {'users_list': users_list, 'user': request.user, 'logged_out': logged_out,'user_theme': user_theme})


@login_required
def about(request):
    logged_out = request.GET.get('logged_out') == 'True'
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(request, 'about.html', {'user': request.user, 'logged_out': logged_out,'user_theme': user_theme})


@login_required
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)


    if request.method == 'POST':
        user_form = CustomUserEditForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user = user_form.save()
            update_session_auth_hash(request, user) 
            return redirect('user', username=user.username) 
    else:
        user_form = CustomUserEditForm(instance=request.user)


    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('user', username=user_profile)
    else:
        profile_form = UserProfileForm(instance=user_profile)
    
    

    if request.method == 'POST':
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, request.user)
    else:
        password_form = CustomPasswordChangeForm(request.user)
    
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(request, 'edit_profile.html', {
        'user_profile': user_profile,
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'user_theme': user_theme
    })


@login_required
def add_comment(request, post_id):
    blog_post = get_object_or_404(BlogPost, pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment_text = form.cleaned_data['text']
            image = form.cleaned_data['image']
            embed = form.cleaned_data['embed']
            comment = Comment(text=comment_text, post=blog_post, user=request.user, image=image,embed=embed)
            comment.save()

            return redirect('post', id=post_id)
    else:
        form = CommentForm()

    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    return render(request, 'post.html', {'blog_post': blog_post, 'form': form,'user_theme': user_theme})

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    if request.user == comment.user:
        if request.method == 'POST':
            form = CommentForm(request.POST, request.FILES, instance=comment)  
            if form.is_valid():
                comment.text = form.cleaned_data['text']
                comment.image = form.cleaned_data['image']
                comment.embed = form.cleaned_data['embed']
                comment.save()

                return redirect('post', id=comment.post.id)
        else:
            form = CommentForm(instance=comment, initial={'text': comment.text, 'image': comment.image, 'embed':comment.embed})

        return render(request, 'edit_comment.html', {'form': form, 'comment': comment,'user_theme': user_theme})
    else:
        return HttpResponseForbidden("You do not have permission to edit this comment.")

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    try:
            user_theme = Theme.objects.get(user=request.user)
    except Theme.DoesNotExist:
            user_theme = None
    if request.user == comment.user:
        if request.method == 'POST':
            comment.delete()
            return redirect('post', id=comment.post.id)
        else:
            return render(request, 'delete_comment.html', {'comment': comment,'user_theme': user_theme})
    else:
        return HttpResponseForbidden("You do not have permission to delete this comment.")

@login_required
def image_comment(request, image):
    comment_post = Comment.objects.get(image=image)
    logged_out = request.GET.get('logged_out') == 'True'
    return render(request, 'image2.html', {'user': request.user, 'logged_out': logged_out, 'comment_post':comment_post,})

@login_required
def image_bio(request, image):
    user_profile = UserProfile.objects.get(profile_picture=image)
    logged_out = request.GET.get('logged_out') == 'True'
    return render(request, 'image3.html', {'user': request.user, 'logged_out': logged_out, 'user_profile':user_profile,})


def logo(request):
    return render(request, 'logo.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('home') 
    else:
        form = RegistrationForm()
    if request.user.is_authenticated:
        try:
            user_theme = Theme.objects.get(user=request.user)
        except Theme.DoesNotExist:
            user_theme = None 
    else:
        user_theme = None 
    return render(request, 'registration/register.html', {'form': form,'user_theme': user_theme})



def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home') 
    else:
        form = LoginForm()
    if request.user.is_authenticated:
        try:
            user_theme = Theme.objects.get(user=request.user)
        except Theme.DoesNotExist:
            user_theme = None 
    else:
        user_theme = None 
    return render(request, 'registration/login.html', {'form': form,'user_theme': user_theme})



class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/custom_password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/custom_password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/custom_password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/custom_password_reset_complete.html'




def challenge(request):

    challenge = Challenge.objects.all().filter(ongoing=False)
    ongoing = Challenge.objects.all().filter(ongoing=True)


    if request.user.is_authenticated:
        try:
            user_theme = Theme.objects.get(user=request.user)
        except Theme.DoesNotExist:
            user_theme = None
    else:
        user_theme = None 
    return render(request, 'challenge.html',{'challenge': challenge,'ongoing':ongoing,'user_theme': user_theme})



def challengetrack(request,slug):

    challenge = Challenge.objects.get(slug=slug)


    

    if request.user.is_authenticated:
        try:
            user_theme = Theme.objects.get(user=request.user)
        except Theme.DoesNotExist:
            user_theme = None  
    else:
        user_theme = None 
    return render(request, 'challengetrack.html',{'challenge': challenge,'user_theme': user_theme})



