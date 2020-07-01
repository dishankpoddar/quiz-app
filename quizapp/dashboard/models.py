from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django import forms
import uuid

class User(AbstractUser):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    ADMIN = 'AD'
    TEACHER = 'TE'
    STUDENT = 'ST'
    UNDEFINED = 'UD'
    ROLE_CHOICES = [
        (ADMIN,'Admin'),
        (TEACHER,'Teacher'),
        (STUDENT, 'Student'),
    ]
    role = models.CharField(max_length=2,choices=ROLE_CHOICES,default=UNDEFINED,)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username

class Quiz(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    title = models.CharField(max_length = 100)
    description = models.TextField()
    author = models.ForeignKey(Teacher, on_delete=models.CASCADE,related_name='quizzes')

    def __str__(self):
        return self.title
        
class Question(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    text = models.CharField('Question', max_length=255)
    author = models.ForeignKey(Teacher, on_delete=models.CASCADE,related_name='questions')

    def __str__(self):
        return self.text

class Answer(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text

class SelectedQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='selected_question',related_query_name="question")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='selected_question')

class AssignedQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assigned_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='assigned_quizzes')
    date = models.DateTimeField(auto_now_add=True)

class StartedQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='started_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='started_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class CompletedQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='completed_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='completed_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='answered')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answered')