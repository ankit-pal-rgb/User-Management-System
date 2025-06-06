from django.urls import path
from . import views

urlpatterns = [
    path('get-user/<str:id>', views.get_user_by_id),
    path('get-users', views.get_all_users),
    path('update-user/<str:id>', views.update_user),
    path('delete-user/<str:id>', views.delete_user),
    path('user-add/', views.render_register_form),
    path('register/', views.register_user_with_picture),
    path('sent-invite/', views.invite_user),
    path('soft-delete/<str:id>', views.soft_delete_user),
    path('restore-user/<str:id>', views.restore_user)
]