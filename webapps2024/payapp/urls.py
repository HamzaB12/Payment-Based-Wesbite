from django.urls import path
from . import views
from .views import delete_notification, accept_payment, refuse_payment

urlpatterns = [
    path("", views.index, name="payapp"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("delete_notification/<int:notification_id>/", delete_notification, name="delete_notification"),
    path("accept_payment/<int:notification_id>/", accept_payment, name="accept_payment"),
    path("refuse_payment/<int:notification_id>/", refuse_payment, name="refuse_payment"),
]