from django.urls import path

from blog.views import home, create_post, user_list, toggle_subscription, user_profile, post_detail, public_posts, \
    request_access, manage_requests, approve_request, my_posts, edit_post, delete_post

urlpatterns = [
    path('', home, name='home'),
    path('create/', create_post, name='create_post'),
    path('users/', user_list, name='user_list'),
    path('subscribe/<int:user_id>/', toggle_subscription, name='toggle_subscription'),
    path('profile/<int:user_id>/', user_profile, name='user_profile'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('public-posts/', public_posts, name='public_posts'),
    path('request_access/<int:post_id>/', request_access, name='request_access'),
    path('manage_requests/', manage_requests, name='manage_requests'),
    path('approve_request/<int:request_id>/', approve_request, name='approve_request'),
    path('my_posts/', my_posts, name='my_posts'),
    path('edit_post/<int:post_id>/', edit_post, name='edit_post'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
]
