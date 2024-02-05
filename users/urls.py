from django.urls import path
from users.views import login_user, register, profile, logout
from django.conf import settings
from django.conf.urls.static import static


app_name = 'users'
urlpatterns = [
    path('login/', login_user, name='login'),
    path('registration/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    ]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)