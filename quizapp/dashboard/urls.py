from django.urls import path
from . import views
from .views import (ListQuizView,CreateQuizView,UpdateQuizView,DeleteQuizView,AssignQuizView,
                    SelectQuestionView,ListQuestionView,CreateQuestionView,UpdateQuestionView,DeleteQuestionView,
                    TeacherDashboard)
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
    path('dashboard/teacher', TeacherDashboard.as_view(), name='teacher-dashboard'),
    path('quiz/view/', ListQuizView.as_view(), name='quiz-view'),
    path('quiz/add/', CreateQuizView.as_view(), name='quiz-add'),
    path('quiz/<int:pk>/', UpdateQuizView.as_view(), name='quiz-edit'),
    path('quiz/<int:pk>/delete', DeleteQuizView.as_view(), name='quiz-delete'),
    path('quiz/<int:pk>/select', SelectQuestionView.as_view(), name='quiz-select'),
    path('quiz/<int:pk>/assign', AssignQuizView.as_view(), name='quiz-assign'),
    path('quiz/<int:pk>/remove-question/<int:select_pk>', views.remove_question, name='question-remove'),
    path('question/view/', ListQuestionView.as_view(), name='question-view'),
    path('question/add/', CreateQuestionView.as_view(), name='question-add'),
    path('question/<int:pk>/', UpdateQuestionView.as_view(), name='question-edit'),
    path('question/<int:pk>/delete', DeleteQuestionView.as_view(), name='question-delete'),
]
