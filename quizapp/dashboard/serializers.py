from rest_framework import serializers
from .models import User,Student,Teacher,Quiz,Question
from django.db import transaction
from django.shortcuts import get_object_or_404

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk','username','password','role',)
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
        fields = ('pk','username','password','role','token')
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
    
class ListQuizSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    assigned_count = serializers.SerializerMethodField()
    #selected_question = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['pk','title','description','author']
        fields += ['question_count','assigned_count']

    def get_question_count(self,obj):
        return obj.selected_question.count()

    def get_assigned_count(self,obj):
        return obj.assigned_quizzes.count()