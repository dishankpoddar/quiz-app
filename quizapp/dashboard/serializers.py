from rest_framework import serializers
from .models import User,Student,Teacher,Quiz,Question,SelectedQuestion,Answer
from django.db import transaction
from django.shortcuts import get_object_or_404

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk','username','password','role',]
        extra_kwargs = {
            'password':
            {"write_only":True},
        }
    
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
        extra_kwargs = {
            'password':
            {"write_only":True},
            'role':
            {'read_only':True}
        }

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
        extra_kwargs = {
            'author':
            {"read_only":True},
        }
    
    def get_author(self,obj):
        return obj.author.username
    
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

class DetailAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk','username']

class ListSelectedQuestionSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    class Meta:
        model = SelectedQuestion
        fields = ['pk','question']
    def get_question(self,obj):
        return  ListQuestionSerializer(obj.question).data

class ListQuizSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    assigned_count = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='api-quiz-edit',
    )
    print(url)
    #selected_question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['url','title','description','author']
        fields += ['question_count','assigned_count']

    def get_question_count(self,obj):
        return obj.selected_question.count()

    def get_assigned_count(self,obj):
        return obj.assigned_quizzes.count()

    def get_author(self,obj):
        return DetailAuthorSerializer(obj.author.user).data

class UpdateQuizSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    selected_questions = serializers.SerializerMethodField()
    #selected_question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['pk','title','description','author']
        fields += ['selected_questions',]
        read_only_fields = ['author']
    
    def get_selected_questions(self,obj):
        return  ListSelectedQuestionSerializer(obj.selected_question.all(),many=True).data

    def get_author(self,obj):
        return DetailAuthorSerializer(obj.author.user).data

class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['pk','text','author']
        extra_kwargs = {
            'author':
            {"read_only":True},
        }
    
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
    #selected_question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['pk','text','author']
        fields += ['quiz_count','answer_count']

    def get_quiz_count(self,obj):
        return obj.selected_question.count()

    def get_answer_count(self,obj):
        return obj.answers.count()

    def get_author(self,obj):
        return DetailAuthorSerializer(obj.author.user).data

class ListAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['text','is_correct']

class UpdateQuestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()
    #answers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['pk','text','author']
        fields += ['answers',]
        read_only_fields = ['author']

    def get_author(self,obj):
        return DetailAuthorSerializer(obj.author.user).data

    def get_answers(self,obj):
        return ListAnswerSerializer(obj.answers.all(),many=True).data