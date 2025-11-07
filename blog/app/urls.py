from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginusr, name='loginusr'),        
    path('home/', views.home, name='home'),
    path('crtblog/', views.crtblog, name='crtblog'),
    path('register/', views.register, name='register'),
    path('logout/', views.logoutusr, name='logout'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('post/<int:id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    # path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile/<int:user_id>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/remove_image/', views.remove_profile_image, name='remove_profile_image'),

]
