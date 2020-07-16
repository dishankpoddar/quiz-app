from rest_framework import serializers
from .models import (User,Student,Teacher,
                    Quiz,Question,SelectedQuestion,Answer,AssignedQuiz,
                    StudentAnswer)
from django.db import transaction,IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.request import Request
from django.test import RequestFactory
factory = RequestFactory()
request = factory.get('/')

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk','username','password','role',]
        write_only_fields = ['password']
    
    @transaction.atomic
    def create(self,validated_data):
        username = validated_data['username']
        role = validated_data['role']
        password = validated_data['password']
        user = User(
            username = username,
            role = role
        )
        user.set_password(password)
        if(role==User.TEACHER):
            Teacher.objects.create(user=user)
        if(role==User.STUDENT):
            Student.objects.create(user=user)
        user.save()
        return validated_data

class LoginSerializer(serializers.ModelSerializer):
    token = serializers.CharField(allow_blank = True,read_only=True)
    username = serializers.CharField()
    class Meta:
        model = User
        fields = ['pk','username','password','role','token']
        write_only_fields = ['password']
        read_only_fields = ['role']

    def validate(self,data):
        username = data["username"]
        password = data["password"]
        user = User.objects.filter(username=username).first()
        if(user):
            if not user.check_password(password):
                raise serializers.ValidationError("Incorrect password. Please try again!")
        
            else:
                data["pk"] = user.pk
                data["role"] = user.role
                data["token"] = "LE TOKEN"
        else:
            raise serializers.ValidationError("User not found!")

        return data

class CreateQuizSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Quiz
        fields = ['pk','title','description','author']
        read_only_fields = ['author']
    
    def get_author(self,obj):
        return DetailUserSerializer(obj['author'].user).data
    
    @transaction.atomic
    def create(self,validated_data):
        title = validated_data['title']
        description = validated_data['description']
        author = validated_data['author']
        quiz = Quiz(
            title = title,
            description = description,
            author = author
        )
        quiz.save()
        validated_data['pk'] = quiz.pk
        return validated_data

class DetailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk','username']

def teacher_dashboard_serializer(request):
    class TeacherDashboardSerializer(serializers.ModelSerializer):
        quizzes = serializers.SerializerMethodField()
        questions = serializers.SerializerMethodField()
        class Meta:
            model = Teacher
            fields = ['quizzes','questions']

        def __init__(self, *args, **kwargs):
            self.request = request
            return super(TeacherDashboardSerializer, self).__init__(*args, **kwargs)

        def get_quizzes(self,obj):
            return ListQuizSerializer(obj.quizzes.all(),many=True,context={'request':self.request}).data

        def get_questions(self,obj):
            return ListQuestionSerializer(obj.questions.all(),many=True,context={'request':self.request}).data

    return TeacherDashboardSerializer

def list_selected_question_serializer(request,obj):    
    class ListSelectedQuestionSerializer(serializers.ModelSerializer):
        question = serializers.SerializerMethodField()
        remove_url = serializers.HyperlinkedIdentityField(
            read_only=True,
            view_name='api-question-remove',
        )
        class Meta:
            model = SelectedQuestion
            fields = ['pk','question','remove_url']

        def __init__(self, *args, **kwargs):
            self.request = request
            return super(ListSelectedQuestionSerializer, self).__init__(*args, **kwargs)

        def get_question(self,obj):
            return  ListQuestionSerializer(obj.question,context={'request':self.request}).data
    
    return ListSelectedQuestionSerializer(obj.selected_question.all(),many=True,context={'request':request})

def list_assigned_quiz_serializer(request,obj):    
    class ListAssignedQuizSerializer(serializers.ModelSerializer):
        student = serializers.SerializerMethodField()
        unassign_url = serializers.HyperlinkedIdentityField(
            read_only=True,
            view_name='api-quiz-unassign',
        )
        quiz = serializers.HyperlinkedRelatedField(
            read_only=True,
            view_name='api-quiz-get'
        )
        class Meta:
            model = AssignedQuiz
            fields = ['pk','quiz','student','status','score','unassign_url']
        def get_student(self,obj):
            return DetailUserSerializer(obj.student.user).data

    return ListAssignedQuizSerializer(obj.assigned_quizzes.all(),many=True,context={'request':request})

def student_dashboard_serializer(request):
    class StudentDashboardSerializer(serializers.ModelSerializer):
        assigned_quizzes = serializers.SerializerMethodField()
        class Meta:
            model = Teacher
            fields = ['assigned_quizzes']

        def __init__(self, *args, **kwargs):
            self.request = request
            return super(StudentDashboardSerializer, self).__init__(*args, **kwargs)

        def get_assigned_quizzes(self,obj):
            return  list_assigned_quiz_serializer(self.request,obj).data

    return StudentDashboardSerializer

class ListQuizSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    assigned_count = serializers.SerializerMethodField()
    edit_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='api-quiz-edit',
    )
    delete_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='api-quiz-delete',
    )
    #selected_question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['edit_url','pk','title','description','author','delete_url']
        fields += ['question_count','assigned_count']

    def get_question_count(self,obj):
        return obj.selected_question.count()

    def get_assigned_count(self,obj):
        return obj.assigned_quizzes.count()

    def get_author(self,obj):
        return DetailUserSerializer(obj.author.user).data

def update_quiz_serializer(request):
    class UpdateQuizSerializer(serializers.ModelSerializer):
        author = serializers.SerializerMethodField()
        selected_questions = serializers.SerializerMethodField()
        assigned_quizzes = serializers.SerializerMethodField()
        delete_url = serializers.HyperlinkedIdentityField(
            read_only=True,
            view_name='api-quiz-delete',
        )
        select_list_url = serializers.HyperlinkedIdentityField(
            read_only=True,
            view_name='api-quiz-select-list',
        )
        select_create_url = serializers.HyperlinkedIdentityField(
            read_only=True,
            view_name='api-quiz-select-create',
        )
        assign_list_url = serializers.HyperlinkedIdentityField(
            read_only=True,
            view_name='api-quiz-assign-list',
        )
        assign_create_url = serializers.HyperlinkedIdentityField(
            read_only=True,
            view_name='api-quiz-assign-create',
        )
        class Meta:
            model = Quiz
            fields = ['pk','title','description','author','delete_url',]
            fields += ['select_list_url','select_create_url','selected_questions']
            fields += ['assign_list_url','assign_create_url','assigned_quizzes']
            read_only_fields = ['author']

        def __init__(self, *args, **kwargs):
            self.request = request
            return super(UpdateQuizSerializer, self).__init__(*args, **kwargs)

        def get_selected_questions(self,obj):
            return  list_selected_question_serializer(self.request,obj).data

        def get_assigned_quizzes(self,obj):
            return  list_assigned_quiz_serializer(self.request,obj).data

        def get_author(self,obj):
            return DetailUserSerializer(obj.author.user).data

    return UpdateQuizSerializer

class CreateQuestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = ['pk','text','author']
        read_only_fields = ['author']

    def get_author(self,obj):
        return DetailUserSerializer(obj['author'].user).data
    
    @transaction.atomic
    def create(self,validated_data):
        text = validated_data['text']
        author = validated_data['author']
        question = Question(
            text = text,
            author = author
        )
        question.save()
        validated_data['pk'] = question.pk
        return validated_data

class ListQuestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    quiz_count = serializers.SerializerMethodField()
    answer_count = serializers.SerializerMethodField()
    edit_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='api-question-edit',
    )
    delete_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='api-question-delete',
    )
    #selected_question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['edit_url','pk','text','author','delete_url']
        fields += ['quiz_count','answer_count']

    def get_quiz_count(self,obj):
        return obj.selected_question.count()

    def get_answer_count(self,obj):
        return obj.answers.count()

    def get_author(self,obj):
        return DetailUserSerializer(obj.author.user).data

class ListAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['pk','text','is_correct']
    
    def update(self, instance, validated_data):
        print(validated_data)
        instance.text = validated_data.get('text', instance.text)
        instance.is_correct = validated_data.get('is_correct', instance.is_correct)
        instance.save()

        return instance

class UpdateQuestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    answers = ListAnswerSerializer(many=True)
    delete_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='api-question-delete',
    )
    #answers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['pk','text','author','delete_url']
        fields += ['answers',]
        read_only_fields = ['author']

    def get_author(self,obj):
        return DetailUserSerializer(obj.author.user).data
    
    def update(self,instance,validated_data):
        old_answers = list(instance.answers.all())
        new_answers = validated_data.pop('answers')
        for _ in range(min(len(old_answers),len(new_answers))):
            old_answer = old_answers.pop(0)
            new_answer = new_answers.pop(0)
            answer = Answer.objects.filter(pk = old_answer.pk).first()
            answer.text = new_answer['text']
            answer.is_correct = new_answer['is_correct']
            answer.save()
        for new_answer in new_answers:
            answer = Answer(text=new_answer['text'],is_correct=new_answer['is_correct'],question=Question.objects.filter(pk=instance.pk).first())
            answer.save()
        for old_answer in old_answers:
            answer = Answer.objects.filter(pk = old_answer.pk).first()
            answer.delete()
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance

class RemoveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedQuestion
        fields = '__all__'

class ListSelectQuestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    answers = ListAnswerSerializer(many=True)
    add = serializers.BooleanField(default= False)
    #answers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['pk','text','author']
        fields += ['answers','add']
        read_only_fields = ['pk','text','author','answers']

    def get_author(self,obj):
        return DetailUserSerializer(obj.author.user).data

class BulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [self.child.create(attrs) for attrs in validated_data]
        print(result)
        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise serializers.ValidationError(e)
        return result

class CreateSelectQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedQuestion
        fields = ['pk','question','quiz']
        list_serializer_class = BulkCreateListSerializer
        
    def create(self, validated_data):
        #print(validated_data)
        instance = SelectedQuestion(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()

        return instance

class ListAssignQuizSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    add = serializers.BooleanField(default= False)
    class Meta:
        model = Student
        fields = ['pk','user','add']
        read_only_fields = ['pk','user','add']

    def get_user(self,obj):
        return DetailUserSerializer(obj.user).data

class UnAssignQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedQuiz
        fields = '__all__'

class CreateAssignQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedQuiz
        fields = ['pk','student','quiz']
        list_serializer_class = BulkCreateListSerializer
        
    def create(self, validated_data):
        #print(validated_data)
        instance = AssignedQuiz(**validated_data)
        if isinstance(self._kwargs["data"], dict):
            instance.save()

        return instance

def take_quiz_serializer(request,question,progress,data):
    class TakeQuizSerializer(serializers.Serializer):
        question = serializers.SerializerMethodField()
        progress = serializers.SerializerMethodField()

        def __init__(self, *args, **kwargs):
            self.request = request
            self.progress = progress
            self.question = question
            return super(TakeQuizSerializer, self).__init__(*args, **kwargs)

        def get_question(self,obj):
            return  UpdateQuestionSerializer(self.question,context={'request':self.request}).data
        
        def get_progress(self,obj):
            return  self.progress

    return TakeQuizSerializer(data=data)

class CreateStudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = '__all__'
        read_only_fields = ['quiz','student']
    
    # @transaction.atomic
    # def create(self,validated_data):
    #     title = validated_data['title']
    #     description = validated_data['description']
    #     author = validated_data['author']
    #     quiz = Quiz(
    #         title = title,
    #         description = description,
    #         author = author
    #     )
    #     quiz.save()
    #     validated_data['pk'] = quiz.pk
    #     return validated_data
