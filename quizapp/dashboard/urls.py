from django.urls import path
from . import views
from .views import (ListQuizView,CreateQuizView,UpdateQuizView,DeleteQuizView,AssignQuizView,TakeQuizView,ResultQuizView,
                    SelectQuestionView,ListQuestionView,CreateQuestionView,UpdateQuestionView,DeleteQuestionView,
                    StudentDashboard,TeacherDashboard)
from django.contrib.auth import views as auth_views

urlpatterns = [    
    path('', views.index, name='index'),
    path('home', views.index, name='index'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('signup/',views.registration, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'),name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='dashboard/logout.html'),name="logout"),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='dashboard/password_reset.html'),name="password_reset"),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password_reset_confirm.html'),name="password_reset_confirm"),
    path('password-reset-done', auth_views.PasswordResetDoneView.as_view(template_name='dashboard/password_reset_done.html'),name="password_reset_done"),
    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset_complete.html'),name="password_reset_complete"),
    path('dashboard/teacher', TeacherDashboard.as_view(), name='teacher-dashboard'),
    path('dashboard/student', StudentDashboard.as_view(), name='student-dashboard'),
    path('quiz/<uuid:pk>/take', TakeQuizView.as_view(), name='quiz-take'),
    path('quiz/view/', ListQuizView.as_view(), name='quiz-view'),
    path('quiz/add/', CreateQuizView.as_view(), name='quiz-add'),
    path('quiz/<uuid:pk>/', UpdateQuizView.as_view(), name='quiz-edit'),
    path('quiz/<uuid:pk>/delete', DeleteQuizView.as_view(), name='quiz-delete'),
    path('quiz/<uuid:pk>/select', SelectQuestionView.as_view(), name='quiz-select'),
    path('quiz/<uuid:pk>/assign', AssignQuizView.as_view(), name='quiz-assign'),
    path('quiz/<uuid:pk>/result', ResultQuizView.as_view(), name='quiz-result'),
    path('quiz/<uuid:pk>/remove-question/<int:select_pk>', views.remove_question, name='question-remove'),
    path('question/view/', ListQuestionView.as_view(), name='question-view'),
    path('question/add/', CreateQuestionView.as_view(), name='question-add'),
    path('question/<uuid:pk>/', UpdateQuestionView.as_view(), name='question-edit'),
    path('question/<uuid:pk>/delete', DeleteQuestionView.as_view(), name='question-delete'),
]
