from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('gallery', views.gallery, name='gallery'),
    path('services', views.services, name='services'),
    path('upload', views.upload, name='upload'),
    path('view_profile', views.view_profile, name='view_profile'),
    path('logout', views.logout_request, name='logout'),
    path('updateprofile', views.update_profile_request, name='updateprofile'),
    path('changepassword', views.change_password_request, name='changepassword'),
    path('history', views.history_view, name='history'),
    path('object_detection', views.object_detection, name='object_detection'),
    path('land_use', views.land_use, name='land_use'),
    path('parameter', views.parameter, name='parameter'),
    path('vegetation_localization', views.vegetation_localization, name='vegetation_localization'),
]
