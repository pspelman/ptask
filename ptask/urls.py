"""ptask URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

import views

from data_management import send_results, make_csv
from ptask import task_urls

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)
# from urls import urlpatterns


urlpatterns = [
    url(r'^research/$', include(task_urls)),
    url(r'^research/', include(task_urls)),
    url(r'^/research/', include(task_urls)),
    url(r'^$', include(task_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^favicon\.ico$', favicon_view),
]

handler404 = views.error404
handler500 = views.error404
