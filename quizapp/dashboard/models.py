from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse



class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

class Quiz(models.Model):
    title = models.CharField(max_length = 100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('quiz-detail',kwargs={'pk': self.pk})

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='AssignedQuiz')

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username

class AssignedQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assigned_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='assigned_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
