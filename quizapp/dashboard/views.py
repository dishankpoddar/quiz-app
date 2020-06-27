from django.shortcuts import render,HttpResponse, redirect,get_object_or_404
from django.conf import settings 
from django.contrib import messages
from .forms import TeacherSignUpForm,StudentSignUpForm,BaseAnswerInlineFormSet,AnswerFormSet,QuestionForm
from .models import Quiz,Question,Answer,SelectedQuestion
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View,TemplateView,CreateView, DeleteView, DetailView, ListView,UpdateView,FormView
from django.db import transaction
from django.db.models import Avg, Count, F, Aggregate
from django.urls import reverse, reverse_lazy


# Create your views here.
def index(request):
    return render(request, 'dashboard/home.html')

def register(request):
    return render(request, 'dashboard/signup.html')

@login_required
def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teacher-dashboard')
        elif request.user.is_student:
            return redirect('index')
        else:
            return redirect('index')

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
class TeacherDashboard(TemplateView):
    template_name = 'dashboard/teacher_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(TeacherDashboard, self).get_context_data(**kwargs)
        context['quizzes'] = self.request.user.quizzes.all() \
            .annotate(questions_count=Count('selected_question', distinct=True)) \
            .annotate(assigned_count=Count('assigned_quizzes', distinct=True))
        context['questions'] = self.request.user.questions.all() \
            .annotate(selected_count=Count('selected_question', distinct=True)) \
            .annotate(answer_count=Count('answers', distinct=True))
        return context

@method_decorator(login_required, name="dispatch")
class ListQuizView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/quiz_list.html'

    def get_queryset(self):
        queryset = Quiz.objects.all() \
            .annotate(questions_count=Count('selected_question', distinct=True)) \
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
        kwargs['questions'] = self.get_object().selected_question.annotate(answer_count = Count(F('question__answers')))
        return super().get_context_data(**kwargs)


    def get_success_url(self):
        return reverse('quiz-edit', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class DeleteQuizView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/quiz_delete_confirm.html'
    success_url = reverse_lazy('teacher-dashboard')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz "%s" was deleted with success!' % quiz.title)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()

@login_required
def remove_question(request,pk=None,select_pk=None):
    quiz = get_object_or_404(Quiz, pk=pk ,author=request.user)
    selected_question = SelectedQuestion.objects.get(pk=select_pk)
    question = selected_question.question
    selected_question.delete()
    messages.success(request, 'The question "%s" was removed from "%s"!' % (question.text , quiz.title) )
    return redirect('quiz-edit',pk)


@method_decorator(login_required, name='dispatch')
class SelectQuestionView(CreateView):
    model = SelectedQuestion

    def get(self,request,pk):
        quiz = get_object_or_404(Quiz, pk=pk ,author=request.user)
        some_questions = Question.objects.all()
        selected_questions = quiz.selected_question.all()
        questions = []
        selected = []
        for selected_question in selected_questions:
            selected.append(selected_question.question)
        for some_question in some_questions:
            if(some_question not in selected):
                arr = {"question":some_question,"answers":some_question.answers.all()}
                questions.append(arr)
        return render(request, 'dashboard/question_select.html', {
            'questions': questions,
            'quiz': quiz,
        })
    
    def post(self,request,pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        selected = []
        for x in request.POST:
            selected.append(x)
        selected.pop(0)
        for x in selected:
            question = get_object_or_404(Question, pk=x )
            select_question = SelectedQuestion(question=question,quiz=quiz)
            select_question.save()
        return redirect('quiz-edit',pk)


    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator(login_required, name="dispatch")
class ListQuestionView(ListView):
    model = Question
    ordering = ('text', )
    context_object_name = 'questions'
    template_name = 'dashboard/question_list.html'

    def get_queryset(self):
        queryset = Question.objects.all() \
            .annotate(answer_count=Count('answers', distinct=True)) \
            .annotate(selected_count=Count('selected_question', distinct=True))
        return queryset

@method_decorator(login_required, name="dispatch")
class CreateQuestionView(CreateView):
    model = Question
    fields = ('text',)
    template_name = 'dashboard/question_add.html'

    def form_valid(self, form):
        question = form.save(commit=False)
        question.author = self.request.user
        question.save()
        messages.success(self.request, 'You may now add answers/options to the question.')
        return redirect('question-edit', question.pk)


@method_decorator(login_required, name="dispatch")
class UpdateQuestionView(UpdateView):

    def get(self,request,pk):
        question = get_object_or_404(Question, pk=pk )
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)
        return render(request, 'dashboard/question_edit.html', {
            'question': question,
            'form': form,
            'formset': formset
        })
    
    def post(self,request,pk):
        question = get_object_or_404(Question, pk=pk)
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()  
            messages.success(request, 'Question and answers saved with success!')
        return render(request, 'dashboard/question_edit.html', {
            'question': question,
            'form': form,
            'formset': formset
        })

    def get_queryset(self):
        return self.request.user.questions.all()

    def get_success_url(self):
        return reverse('question-edit', kwargs={'pk': self.object.pk})

@method_decorator(login_required, name='dispatch')
class DeleteQuestionView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'dashboard/question_delete_confirm.html'
    success_url = reverse_lazy('teacher-dashboard')

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question "%s" was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.questions.all()