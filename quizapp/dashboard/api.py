from django.shortcuts import render,HttpResponse, redirect,get_object_or_404
from django.conf import settings 
from django.contrib import messages
from .models import User,Quiz,Question,Answer,SelectedQuestion,AssignedQuiz,Student
from django.db import transaction
from django.db.models import Avg, Count, F, Aggregate
from django.urls import reverse, reverse_lazy

from .serializers import (SignupSerializer,LoginSerializer,
    ListQuizSerializer,UpdateQuizSerializer,CreateQuizSerializer,
    ListQuestionSerializer,UpdateQuestionSerializer,CreateQuestionSerializer,
    ListAnswerSerializer)
from rest_framework import generics,status,permissions
from rest_framework.response import Response
from .permissions import IsAuthorOrReadOnly,IsTeacher


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self,request,*args,**kwargs):
        data = request.data
        serializer = LoginSerializer(data=data)
        if(serializer.is_valid(raise_exception=True)):
            new_data = serializer.data
            return Response(new_data,status = status.HTTP_200_OK)
        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)

class CreateQuizAPIView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = CreateQuizSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

    def perform_create(self,serializer):
        serializer.save(author=self.request.user.teacher)

class ListQuizAPIView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = ListQuizSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

class UpdateQuizAPIView(generics.RetrieveUpdateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = UpdateQuizSerializer
    permission_classes = [permissions.IsAuthenticated,IsAuthorOrReadOnly,IsTeacher]

class DeleteQuizAPIView(generics.DestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = UpdateQuizSerializer
    permission_classes = [permissions.IsAuthenticated,IsAuthorOrReadOnly,IsTeacher]

class CreateQuestionAPIView(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = CreateQuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

    def perform_create(self,serializer):
        serializer.save(author=self.request.user.teacher)

class ListQuestionAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = ListQuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

class UpdateQuestionAPIView(generics.RetrieveUpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = UpdateQuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsAuthorOrReadOnly,IsTeacher]
    

class DeleteQuestionAPIView(generics.DestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = UpdateQuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsAuthorOrReadOnly,IsTeacher]