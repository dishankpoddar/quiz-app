from django.urls import path
from . import views
from .views import CreateQuizView,UpdateQuizView,ListQuizView
from django.contrib.auth import views as auth_views

urlpatterns = [    
    path('', views.index, name='index'),
    path('home', views.index, name='index'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('signup/',views.register, name='register'),
    path('signup/student',views.studentRegistration, name='student-registration'),
    path('signup/teacher',views.teacherRegistration, name='teacher-registration'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'),name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='dashboard/logout.html'),name="logout"),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='dashboard/password_reset.html'),name="password_reset"),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password_reset_confirm.html'),name="password_reset_confirm"),
    path('password-reset-done', auth_views.PasswordResetDoneView.as_view(template_name='dashboard/password_reset_done.html'),name="password_reset_done"),
    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset_complete.html'),name="password_reset_complete"),
    path('dashboard/teacher', ListQuizView.as_view(), name='teacher-dashboard'),
    path('quiz/add/', CreateQuizView.as_view(), name='quiz-add'),
    path('quiz/<int:pk>/', UpdateQuizView.as_view(), name='quiz-edit'),
]
