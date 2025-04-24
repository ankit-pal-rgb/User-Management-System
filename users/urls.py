from django.urls import path
from . import views

urlpatterns = [
    path('get-user/<str:id>', views.get_user_by_id),
    path('get-users', views.get_all_users),
    path('update-user/<str:id>', views.update_user),
    path('delete-user/<str:id>', views.delete_user),
    path('user-add', views.add_new_user),
    path('profile', views.render_register_form),
    path('register', views.register_user_with_picture)
]