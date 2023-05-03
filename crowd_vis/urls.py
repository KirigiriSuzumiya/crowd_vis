"""crowd_vis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from . import views
from dbmodel import views as dbviews

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('video/(.*)$', views.video),
    path('', views.index),
    path('num_count', views.num_count),
    path('graph_vis', views.graph_vis),
    path("video_recall", views.data_recall),
    path("api/warn/", dbviews.my_view),
    path('api/info/', dbviews.my_info),
    path("vue_index", views.vue_index),
    path("graph_vis_vue", views.graph_vis_vue),
    path("graph_vis_en", views.graph_vis_en),
    path("en", views.index_en),
    path("api/display/", dbviews.deal_crowdinfo)
]
