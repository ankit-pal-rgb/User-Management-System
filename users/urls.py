from django.urls import path
from . import views

urlpatterns = [
    path('user/<str:id>', views.get_user_by_id),
    path('users', views.get_all_users),
    path('user/<str:id>', views.update_user),
    path('user/<str:id>', views.delete_user),
    path('user-add', views.add_new_user)
]