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
favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.welcome_vew),
    url(r'^instructions', views.instructions_view),
    url(r'^begin_task', views.begin_task),
    url(r'^task_view', views.task_view),
    url(r'^process_form', views.process_form_data),
    url(r'^completion', views.task_complete_view),
    url(r'^logout', views.logout_view),
    url(r'^(?P<researcher_email>[0-9]+)/(begin_task_with_url_params)', views.begin_task_with_url_params),
    url(ur'^task/(?P<researcher_email>.*)/$', views.begin_task_with_url_params),
    url(ur'^task/(?P<researcher_email>.*)/(?P<participant_id>[0-9]+)', views.begin_task_with_url_params),
    url(ur'^task/?researcher_email=(?P<researcher_email>.*)&participant_id=(?P<participant_id>[0-9]+)',
        views.begin_task_with_url_params),
    url(ur'^task/manual_input', views.manual_input),
    url(r'^favicon\.ico$', favicon_view),
    url(r'send_results', send_results, name='send_results'),
    url(r'make_csv', make_csv, name='make_csv'),
]

handler404 = views.error404
handler500 = views.error404
