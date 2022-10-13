from django.urls import path
from rest_framework.routers import DefaultRouter
from used_bikes import views
router=DefaultRouter()
router.register("signup",views.UsersView,basename="olx_users")
router.register("bikes",views.BikeView,basename="olx_bikes")
router.register("offers",views.)
urlpatterns =[

]+router.urls