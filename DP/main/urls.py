from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

app_name = 'main'

urlpatterns = [
    # Пътища за автентикация
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    # Основен изглед
    path('', views.index, name='index'),

    # API ендпойнти
    path('api/stats/', views.api_system_stats, name='api_system_stats'),
    path('api/processes/', views.api_top_processes, name='api_top_processes'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
