"""Y_crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path,re_path,include
from stark.service.v1 import site
from web.views import account
urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^stark/', site.urls),
    re_path(r'^login/', account.login,name='login'),
    re_path(r'^logout/', account.logout,name='logout'),
    re_path(r'^index/', account.index,name='index'),
    re_path(r'^rbac/', include('rbac.urls', namespace='rbac'))
]
