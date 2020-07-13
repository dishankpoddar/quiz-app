from django.shortcuts import render,HttpResponse, redirect,get_object_or_404
from django.conf import settings 
from django.contrib import messages
from .models import User,Quiz,Question,Answer,SelectedQuestion,AssignedQuiz,Student
from django.db import transaction
from django.db.models import Avg, Count, F, Aggregate
from django.urls import reverse, reverse_lazy

from .serializers import (SignupSerializer,LoginSerializer,
    ListQuizSerializer,update_quiz_serializer,CreateQuizSerializer,
    ListQuestionSerializer,UpdateQuestionSerializer,CreateQuestionSerializer,
    ListAnswerSerializer,SelectQuestionSerializer)
from rest_framework import generics,status,permissions
from rest_framework.response import Response
from .permissions import IsAuthorOrReadOnly,IsTeacher,IsAuthor


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
    permission_classes = [permissions.IsAuthenticated,IsAuthorOrReadOnly,IsTeacher]

    def get_serializer_class(self):
        return update_quiz_serializer(
                request=self.request
                )

class DeleteQuizAPIView(generics.DestroyAPIView):
    queryset = Quiz.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsAuthor,IsTeacher]

    def get_serializer_class(self):
        return update_quiz_serializer(
                request=self.request
                )

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
    permission_classes = [permissions.IsAuthenticated,IsAuthor,IsTeacher]

class SelectedQuestionAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = SelectQuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher,IsAuthor]

    def get_queryset(self,*args,**kwargs):
        pk=self.kwargs['pk']
        quiz = Quiz.objects.filter(pk=pk).filter(author=self.request.user.teacher).first()
        #queryset = Question.objects.first()
        #print(quiz)
        #quiz = get_object_or_404(Quiz, pk=pk ,author=self.request.user.teacher)
        if(quiz):
            selected_question_objects = list(quiz.selected_question.select_related('question').all())
            selected_questions = []
            for selected_question_object in selected_question_objects:
                selected_questions.append(selected_question_object.question.pk)
            queryset = Question.objects.exclude(pk__in=selected_questions)
        print(queryset)
        return queryset

        #def get(self,request,*args,**kwargs):

    