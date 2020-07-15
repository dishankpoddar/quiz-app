from django.shortcuts import render,HttpResponse, redirect,get_object_or_404
from django.conf import settings 
from django.contrib import messages
from .models import User,Quiz,Question,Answer,SelectedQuestion,AssignedQuiz,Student,Teacher,StudentAnswer
from django.db import transaction
from django.db.models import Avg, Count, F, Aggregate
from django.urls import reverse, reverse_lazy

from .serializers import (SignupSerializer,LoginSerializer,
    ListQuizSerializer,update_quiz_serializer,CreateQuizSerializer,
    ListQuestionSerializer,UpdateQuestionSerializer,CreateQuestionSerializer,
    ListAnswerSerializer,teacher_dashboard_serializer,student_dashboard_serializer,take_quiz_serializer,
    ListSelectQuestionSerializer,CreateSelectQuestionSerializer,RemoveQuestionSerializer,
    ListAssignQuizSerializer,CreateAssignQuizSerializer,UnAssignQuizSerializer)
from rest_framework import generics,status,permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .permissions import IsAuthorOrReadOnly,IsTeacher,IsAuthor,IsStudent


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

class TeacherDashboardAPIView(generics.RetrieveAPIView):
    queryset = Teacher.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

    def get_serializer_class(self):
        return teacher_dashboard_serializer(request=self.request)

    def get_object(self):
            queryset = self.filter_queryset(self.get_queryset())
            # make sure to catch 404's below
            obj = queryset.get(user=self.request.user)
            self.check_object_permissions(self.request, obj)
            return obj

class StudentDashboardAPIView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

    def get_serializer_class(self):
        return student_dashboard_serializer(request=self.request)

    def get_object(self):
            queryset = self.filter_queryset(self.get_queryset())
            # make sure to catch 404's below
            obj = queryset.get(user=self.request.user)
            self.check_object_permissions(self.request, obj)
            return obj

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
        return update_quiz_serializer(request=self.request)

class DeleteQuizAPIView(generics.DestroyAPIView):
    queryset = Quiz.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsAuthor,IsTeacher]

    def get_serializer_class(self):
        return update_quiz_serializer(request=self.request)

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

class ListSelectQuestionAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = ListSelectQuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher,IsAuthor]

    def get_queryset(self,*args,**kwargs):
        pk=self.kwargs['pk']
        quiz = get_object_or_404(Quiz,pk=pk,author=self.request.user.teacher)
        if(quiz):
            selected_question_objects = list(quiz.selected_question.select_related('question').all())
            selected_questions = []
            for selected_question_object in selected_question_objects:
                selected_questions.append(selected_question_object.question.pk)
            queryset = Question.objects.exclude(pk__in=selected_questions)

        return queryset

class CreateSelectQuestionAPIView(generics.CreateAPIView):
    """
        Post request should be of the form:
        [
            {
                "question": "pk_of_first_question"
            },
            {
                "question": "pk_of_second_question"
            },
            ...
        ]
    """
    queryset = SelectedQuestion.objects.all()
    serializer_class = CreateSelectQuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(CreateSelectQuestionAPIView, self).get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        #print(request.data)
        """for select_question in select_questions:
            select_question.quiz=quiz"""
        if isinstance(request.data, list):
            for item in request.data:
                item["quiz"] = kwargs["pk"]
        else:
            raise ValidationError("Invalid Input")
        #print(request.data)
        return super(CreateSelectQuestionAPIView, self).post(request, *args, **kwargs)

class RemoveQuestionAPIView(generics.DestroyAPIView):
    serializer_class = RemoveQuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

    def get_queryset(self,*args,**kwargs):
        pk=self.kwargs['pk']
        selected_question = SelectedQuestion.objects.filter(pk=pk).first()
        quiz = get_object_or_404(Quiz,pk=selected_question.quiz.pk,author=self.request.user.teacher)
        queryset = SelectedQuestion.objects.all()
        return queryset

class ListAssignQuizAPIView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = ListAssignQuizSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher,IsAuthor]

    def get_queryset(self,*args,**kwargs):
        pk=self.kwargs['pk']
        quiz = get_object_or_404(Quiz,pk=pk,author=self.request.user.teacher)
        if(quiz):
            assigned_quiz_objects = list(quiz.assigned_quizzes.select_related('student').all())
            assigned_quizzes = []
            for assigned_quiz_object in assigned_quiz_objects:
                assigned_quizzes.append(assigned_quiz_object.student.pk)
            queryset = Student.objects.exclude(pk__in=assigned_quizzes)

        return queryset

class UnAssignQuizAPIView(generics.DestroyAPIView):
    serializer_class = UnAssignQuizSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

    def get_queryset(self,*args,**kwargs):
        pk=self.kwargs['pk']
        assigned_quiz = AssignedQuiz.objects.filter(pk=pk).first()
        quiz = get_object_or_404(Quiz,pk=assigned_quiz.quiz.pk,author=self.request.user.teacher)
        queryset = AssignedQuiz.objects.all()
        return queryset

class CreateAssignQuizAPIView(generics.CreateAPIView):
    """
        Post request should be of the form:
        [
            {
                "student": "pk_of_first_student"
            },
            {
                "student": "pk_of_second_student"
            },
            ...
        ]
    """
    queryset = AssignedQuiz.objects.all()
    serializer_class = CreateAssignQuizSerializer
    permission_classes = [permissions.IsAuthenticated,IsTeacher]

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(CreateAssignQuizAPIView, self).get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        #print(request.data)
        """for select_question in select_questions:
            select_question.quiz=quiz"""
        if isinstance(request.data, list):
            for item in request.data:
                item["quiz"] = kwargs["pk"]
        else:
            raise ValidationError("Invalid Input")
        #print(request.data)
        return super(CreateAssignQuizAPIView, self).post(request, *args, **kwargs)

class TakeQuizAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsStudent]

    def get_unanswered_questions(self,student,quiz):
        answered_questions = student.answered \
            .filter(quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        #selected_questions = quiz.selected_question.select_related('questions').order_by('-date')
        selected_questions = quiz.selected_question.all().order_by('?')
        questions = []
        for selected_question in selected_questions:
            if(selected_question.question.pk not in answered_questions):
                questions.append(selected_question.question)
        return questions

    def get_questions(self,student,quiz):
        total_questions = quiz.selected_question.count()
        unanswered_questions = self.get_unanswered_questions(student,quiz)
        print(total_questions,unanswered_questions)
        total_unanswered_questions = len(unanswered_questions)
        progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
        question = unanswered_questions[0]
        return question,progress

    def get_serializer_class(self,*args,**kwargs):
        quiz_pk = self.kwargs['pk']
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        student = self.request.user.student
        question,progress= self.get_questions(student,quiz)
        #print(question)
        assigned_quiz = get_object_or_404(AssignedQuiz, quiz=quiz,student=student)
        assigned_quiz.status = AssignedQuiz.STARTED
        assigned_quiz.save()
        data = {"question":question,"progress":progress}
        return take_quiz_serializer(self.request,question,progress,data)

    def get(self,request,*args,**kwargs):
        serializer = self.get_serializer_class()
        if(serializer.is_valid(raise_exception=True)):
            new_data = serializer.data
            return Response(serializer.data,status = status.HTTP_200_OK)
        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
    # def get_object(self):
    #     queryset = self.get_queryset()
    #     filter = {}
    #     for field in self.multiple_lookup_fields:
    #         filter[field] = self.kwargs[field]

    #     obj = get_object_or_404(queryset, **filter)
    #     self.check_object_permissions(self.request, obj)
    #     return obj