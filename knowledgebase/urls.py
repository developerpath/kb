from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
from . import forms

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^profile/', views.user_profile, name='profile'),

    url(r'^login/', auth_views.LoginView.as_view(
        authentication_form=forms.LoginForm), name='login'),
    url(r'^logout/', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^pass/', auth_views.PasswordResetView.as_view(), name='pass'),
    url(r'^password_reset_done/', auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    
    url(r'^signup/', views.signup, name='signup'),
    
    url(r'^$', views.space_view),
    url(r'^page_view/(?P<space_id>[0-9]+)/(?:(?P<page_id>[0-9]+)/)?$',
        views.page_view, name='page_view'),
    url(r'^page_edit/(?P<space_id>[0-9]+)/(?P<page_id>[0-9]+)/(?:(?P<action>[0-9]+)/)?$',
        views.page_edit, name='page_edit'),
    url(r'^space_view/$', views.space_view, name='space_view'),
    url(r'^space_edit/(?P<space_id>[0-9]+)/(?:(?P<action>[0-9]+)/)?$',
        views.space_edit, name='space_edit'),
#    url(r'^page_update/$', views.page_update, name='page_update'),
]
