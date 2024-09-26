from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('borrower/', include('borrower.urls', namespace='borrower')),
    path('investor/', include('investor.urls', namespace='investor')),
    path('loans/', include('loans.urls', namespace='loans')),
    path('', include('home.urls', namespace='home')),  # Default root/homepage
]
