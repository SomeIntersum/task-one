from django.urls import path

from accounts.views import login_page, register_page, user_logout

urlpatterns = [
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register'),
    path('logout/', user_logout, name='logout'),
]
