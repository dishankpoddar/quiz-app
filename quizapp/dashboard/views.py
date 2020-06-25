from django.shortcuts import render,HttpResponse, redirect
from django.conf import settings 
from django.contrib import messages
from .forms import TeacherSignUpForm,StudentSignUpForm
from .models import Quiz
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView,UpdateView
from django.db import transaction
from django.db.models import Avg, Count
from django.urls import reverse, reverse_lazy


# Create your views here.
def index(request):
    return render(request, 'dashboard/home.html')

def register(request):
    return render(request, 'dashboard/signup.html')

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def teacherRegistration(request):
    if(request.method == 'POST'):
        form = TeacherSignUpForm(request.POST)
        if(form.is_valid()):
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Teacher Account created for {username}! You can now login')
            return redirect('login')
    else:
        form = TeacherSignUpForm()
    return render(request,'dashboard/register.html',{'form':form,'is_student':False})

def studentRegistration(request):
    if(request.method == 'POST'):
        form = StudentSignUpForm(request.POST)
        if(form.is_valid()):
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Student Account created for {username}! You can now login')
            return redirect('login')
    else:
        form = TeacherSignUpForm()
    return render(request,'dashboard/register.html',{'form':form,'is_student':True})

@method_decorator(login_required, name="dispatch")
class ListQuizView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/dashboard.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(assigned_count=Count('assigned_quizzes', distinct=True))
        return queryset

@method_decorator(login_required, name="dispatch")
class CreateQuizView(CreateView):
    model = Quiz
    fields = ('title','description')
    template_name = 'dashboard/quiz_add.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.author = self.request.user
        quiz.save()
        messages.success(self.request, 'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('quiz-edit', quiz.pk)

@method_decorator(login_required, name="dispatch")
class UpdateQuizView(UpdateView):
    model = Quiz
    fields = ('title', 'description', )
    context_object_name = 'quiz'
    template_name = 'dashboard/quiz_edit.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz-edit', kwargs={'pk': self.object.pk})
