from django.urls import path
from . import views
from poll.views import change_password
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('vote/<int:candidate_id>/', views.vote, name='vote'),
    path('add-candidate/', views.add_candidate, name='add_candidate'),
    path('change-phase/<str:phase_name>/', views.change_phase, name='change_phase'),
    path('results/', views.results, name='results'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('changepass', views.change_password, name='changepass'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)