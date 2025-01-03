from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views
from .views import HomePageView, SearchResultsView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('post/', views.post_blog, name='post_blog'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('logo/', views.logo, name='logo'),
    path('post/<int:id>/', views.post, name='post'),
    path('post/<int:id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:id>/delete/', views.delete_post, name='delete_post'),
    path('captcha/', include('captcha.urls')),
    path('user/<str:username>/', views.user, name='user'),
    path('users',views.users,name="users"),
    path("search/", SearchResultsView.as_view(), name="search_results"),
    path("home", HomePageView.as_view()),
    path('user/profile/edit', views.edit_profile, name='edit_profile'),
    path('post/<int:post_id>/add_comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('image/<str:image>',views.image,name="image"),
    path('image_comment/<str:image>',views.image_comment,name="image_comment"),
    path('image_bio/<str:image>',views.image_bio,name="image_bio"),
    path("tags",views.tags,name="tags"),
    path("tag/<slug>",views.tagged,name="tagged"),
    path("about",views.about,name="about"),
    path('date/', views.filter_by_date, name='date'),
    path('theme/', views.theme, name='theme'),
    path('reset_theme/', views.reset_theme, name='reset_theme'),
    path('t/', views.toggle_text_only_mode, name='toggle_text_only_mode'),


    path('challenge/', views.challenge, name='challenge'),
    path('challenge/<slug>', views.challengetrack, name='challengetrack'),

    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
   ]