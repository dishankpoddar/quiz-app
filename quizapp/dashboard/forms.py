from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django.forms import inlineformset_factory

from .models import (Student,Teacher,User,Question,Answer,Quiz)

class SignUpForm(UserCreationForm):
    CHOICES = [(User.TEACHER,'Teacher'),(User.STUDENT,'Student')]
    role = forms.ChoiceField(label="Role",widget=forms.RadioSelect, choices=CHOICES)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role',)
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if(self.data['role']==User.TEACHER):
            Teacher.objects.create(user=user)
        if(self.data['role']==User.STUDENT):
            Student.objects.create(user=user)
        
        user.save()
        return user

class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.TEACHER
        user.save()
        teacher = Teacher.objects.create(user=user)
        return user


class StudentSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = User.STUDENT
        user.save()
        student = Student.objects.create(user=user)
        return user

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', )



class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        has_one_correct_answer = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_correct', False):
                    has_one_correct_answer = True
                    break
        if not has_one_correct_answer:
            raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')

AnswerFormSet = inlineformset_factory(
    Question,  # parent model
    Answer,  # base model
    formset=BaseAnswerInlineFormSet,
    fields=('text', 'is_correct'),
    min_num=4,
    validate_min=True,
    max_num=4,
    validate_max=True
)
