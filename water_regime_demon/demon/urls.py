from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.site_list, name="site_list"),
    url(r"^(?P<site_id>\d+)/$", views.site_data, name="site_data"),
    url(r"^(?P<site_id>\d+)/export/.*$", views.export_csv, name="export_csv"),
]
