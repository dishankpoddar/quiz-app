from django.shortcuts import render,HttpResponse, redirect,get_object_or_404
from django.conf import settings 
from django.contrib import messages
from .models import User,Quiz,Question,Answer,SelectedQuestion,AssignedQuiz,Student
from django.db import transaction
from django.db.models import Avg, Count, F, Aggregate
from django.urls import reverse, reverse_lazy

from .serializers import UserSerializer,LoginSerializer,ListQuizSerializer
from rest_framework import generics,status,permissions
from rest_framework.response import Response

class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
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

class ListQuizAPIView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = ListQuizSerializer
    permission_classes = [permissions.AllowAny]