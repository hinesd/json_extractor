from django.contrib import admin
from django.urls import path
from extractionapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('state/endpoint_state_list/', views.endpoint_state_list),
    path('state/extract_content/', views.extract_content),

]
