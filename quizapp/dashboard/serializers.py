from rest_framework import serializers
from .models import User,Student,Teacher,Quiz,Question,SelectedQuestion,Answer
from django.db import transaction
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
        return DetailAuthorSerializer(obj['author'].user).data
    
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

def list_selected_question_serializer(request,obj):    
    class ListSelectedQuestionSerializer(serializers.ModelSerializer):
        question = serializers.SerializerMethodField()
        class Meta:
            model = SelectedQuestion
            fields = ['pk','question']

        def __init__(self, *args, **kwargs):
            self.request = request
            return super(ListSelectedQuestionSerializer, self).__init__(*args, **kwargs)

        def get_question(self,obj):
            return  ListQuestionSerializer(obj.question,context={'request':self.request}).data
    
    return ListSelectedQuestionSerializer(obj.selected_question.all(),many=True)

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
        return DetailAuthorSerializer(obj.author.user).data

def update_quiz_serializer(request):
    class UpdateQuizSerializer(serializers.ModelSerializer):
        author = serializers.SerializerMethodField()
        selected_questions = serializers.SerializerMethodField()
        delete_url = serializers.HyperlinkedIdentityField(
            read_only=True,
            view_name='api-quiz-delete',
        )
        #selected_question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
        class Meta:
            model = Quiz
            fields = ['pk','title','description','author','delete_url']
            fields += ['selected_questions',]
            read_only_fields = ['author']

        def __init__(self, *args, **kwargs):
            self.request = request
            return super(UpdateQuizSerializer, self).__init__(*args, **kwargs)

        
        def get_selected_questions(self,obj):
            return  list_selected_question_serializer(self.request,obj).data

        def get_author(self,obj):
            return DetailAuthorSerializer(obj.author.user).data

    return UpdateQuizSerializer

class CreateQuestionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = ['pk','text','author']
        read_only_fields = ['author']

    def get_author(self,obj):
        return DetailAuthorSerializer(obj['author'].user).data
    
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
        return DetailAuthorSerializer(obj.author.user).data

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
        return DetailAuthorSerializer(obj.author.user).data
    
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

class SelectQuestionSerializer(serializers.ModelSerializer):
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
        return DetailAuthorSerializer(obj.author.user).data

"""class SelectQuestionsSerializer(serializers.ModelSerializer):
    question = SelectQuestionSerializer(many=True)
    class Meta:
        model = SelectedQuestion"""
    


    