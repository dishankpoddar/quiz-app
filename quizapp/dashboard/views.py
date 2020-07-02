from django.shortcuts import render,HttpResponse, redirect,get_object_or_404
from django.conf import settings 
from django.contrib import messages
from .forms import SignUpForm,BaseAnswerInlineFormSet,AnswerFormSet,QuestionForm,TakeQuizForm
from .models import User,Quiz,Question,Answer,SelectedQuestion,AssignedQuiz,Student
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (View,TemplateView,CreateView, DeleteView, DetailView, 
                                    ListView,UpdateView,FormView)
from django.db import transaction
from django.db.models import Avg, Count, F, Aggregate
from django.urls import reverse, reverse_lazy


# Create your views here.
def index(request):
    return render(request, 'dashboard/home.html')

@login_required
def dashboard(request):
    if request.user.is_authenticated:
        if request.user.role == User.TEACHER:
            return redirect('teacher-dashboard')
        elif request.user.role == User.STUDENT:
            return redirect('student-dashboard')
        else:
            return redirect('index')

def signup(request):
    if(request.method == 'POST'):
        form = SignUpForm(request.POST)
        if(form.is_valid()):
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account created for {username}! You can now login')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request,'dashboard/signup.html',{'form':form,'is_student':False})

@method_decorator(login_required, name="dispatch")
class StudentDashboard(TemplateView):
    template_name = 'dashboard/student_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(StudentDashboard, self).get_context_data(**kwargs)
        context['assigned_quizzes'] = self.request.user.student.assigned_quizzes.filter(status = AssignedQuiz.ASSIGNED) \
            .annotate(questions_count=Count('quiz__selected_question', distinct=True))
        context['started_quizzes'] = self.request.user.student.assigned_quizzes.filter(status = AssignedQuiz.STARTED) \
            .annotate(questions_count=Count('quiz__selected_question', distinct=True))
        context['completed_quizzes'] = self.request.user.student.assigned_quizzes.filter(status = AssignedQuiz.COMPLETED) \
            .annotate(questions_count=Count('quiz__selected_question', distinct=True))
        return context

@method_decorator(login_required, name="dispatch")
class TeacherDashboard(TemplateView):
    template_name = 'dashboard/teacher_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(TeacherDashboard, self).get_context_data(**kwargs)
        context['quizzes'] = self.request.user.teacher.quizzes.all() \
            .annotate(questions_count=Count('selected_question', distinct=True)) \
            .annotate(assigned_count=Count('assigned_quizzes', distinct=True))
        context['questions'] = self.request.user.teacher.questions.all() \
            .annotate(selected_count=Count('selected_question', distinct=True)) \
            .annotate(answer_count=Count('answers', distinct=True))
        return context

@method_decorator(login_required, name="dispatch")
class TakeQuizView(CreateView):
    template_name = 'dashboard/quiz_take.html'

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
        total_unanswered_questions = len(unanswered_questions)
        progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
        question = unanswered_questions[0]
        return question,progress
    
    def get(self,request,pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        student = request.user.student
        question,progress= self.get_questions(student,quiz)
        assigned_quiz = get_object_or_404(AssignedQuiz, quiz=quiz,student=student)
        assigned_quiz.status = AssignedQuiz.STARTED
        assigned_quiz.save()
        form = TakeQuizForm(question=question)
        return render(request, 'dashboard/quiz_take.html', {
        'quiz' : quiz,
        'question': question,
        'form': form,
        'progress': progress
        })
    
    def post(self,request,pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        student = request.user.student
        question,progress= self.get_questions(student,quiz)
        form = TakeQuizForm(question=question, data=request.POST)
        assigned_quiz = get_object_or_404(AssignedQuiz, quiz=quiz,student=student)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.quiz = quiz
                student_answer.save()
                if len(self.get_unanswered_questions(student,quiz))>0:
                    return redirect('quiz-take', pk)
                else:
                    correct_answers = student.answered.filter(quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / (quiz.selected_question.count())) * 100.0, 2)
                    assigned_quiz.score = score
                    assigned_quiz.status = AssignedQuiz.COMPLETED
                    assigned_quiz.save()
                    if score < 50.0:
                        messages.warning(request, f'Better luck next time! Your score for the quiz {quiz.title} was {score}.')
                    else:
                        messages.success(request, f'Congratulations! You completed the quiz {quiz.title} with success! You scored {score} points.')
                    return redirect('student-dashboard')

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
        quiz.author = self.request.user.teacher
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
        kwargs['selected_questions'] = self.get_object().selected_question.annotate(answer_count = Count(F('question__answers')))
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
        messages.success(request, f'The quiz "{quiz.title}" was deleted with success!' )
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.teacher.quizzes.all()

@method_decorator(login_required, name='dispatch')
class ResultQuizView(DetailView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/quiz_result.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        assigned_quizzes = quiz.assigned_quizzes.select_related('student__user').order_by('-date')
        total_assigned_quizzes = assigned_quizzes.count()
        quiz_score = quiz.assigned_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'assigned_quizzes': assigned_quizzes,
            'total_assigned_quizzes': total_assigned_quizzes,
            'quiz_score': quiz_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.teacher.quizzes.all()

@method_decorator(login_required, name='dispatch')
class AssignQuizView(CreateView):
    model = AssignedQuiz

    def get(self,request,pk):
        quiz = get_object_or_404(Quiz, pk=pk ,author=request.user.teacher)
        students = Student.objects.all()
        selected_students = list(quiz.assigned_quizzes.select_related('student').all())
        return render(request, 'dashboard/quiz_assign.html', {
            'students' : students,
            'selected_students' : selected_students,
            'quiz': quiz,
        })
    
    def post(self,request,pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        post_data = list(request.POST)[1:]
        selected_students = quiz.assigned_quizzes.all()
        already_selected = []
        for selected_student in selected_students:
            already_selected.append(selected_student.student.pk)
        for student_pk in already_selected:
            if student_pk not in post_data:
                student = get_object_or_404(Student, pk=student_pk )
                AssignedQuiz.objects.filter(student=student,quiz=quiz).delete()
        for student_pk in post_data:
            student = get_object_or_404(Student, pk=student_pk )
            assign_quiz = AssignedQuiz(student=student,quiz=quiz)
            assign_quiz.save()
        messages.success(request, f'"{quiz.title}" assigned to student(s)!')        
        return redirect('quiz-edit',pk)


    def get_queryset(self):
        return self.request.user.teacher.quizzes.all()

@method_decorator(login_required, name='dispatch')
class SelectQuestionView(CreateView):
    model = SelectedQuestion

    def get(self,request,pk):
        quiz = get_object_or_404(Quiz, pk=pk ,author=request.user.teacher)
        some_questions = Question.objects.all()
        selected_questions = list(quiz.selected_question.select_related('question').all())
        add_questions = []
        for some_question in some_questions:
            if(some_question not in selected_questions):
                arr = {"question":some_question,"answers":some_question.answers.all()}
                add_questions.append(arr)
        return render(request, 'dashboard/question_select.html', {
            'add_questions': add_questions,
            'quiz': quiz,
        })
    
    def post(self,request,pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        post_data = list(request.POST)[1:]
        for question_pk in post_data:
            question = get_object_or_404(Question, pk=question_pk)
            select_question = SelectedQuestion(question=question,quiz=quiz)
            select_question.save()
        messages.success(request, f'Question(s) added to "{quiz.title}"!')
        return redirect('quiz-edit',pk)


    def get_queryset(self):
        return self.request.user.teacher.quizzes.all()

@login_required
def remove_question(request,pk=None,select_pk=None):
    quiz = get_object_or_404(Quiz, pk=pk ,author=request.user.teacher)
    selected_question = SelectedQuestion.objects.get(pk=select_pk)
    question = selected_question.question
    selected_question.delete()
    messages.success(request, f'The question "{question.text}" was removed from "{quiz.title}"!')
    return redirect('quiz-edit',pk)


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
        question.author = self.request.user.teacher
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
        return self.request.user.teacher.questions.all()

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
        messages.success(request, f'The question "{question.text}" was deleted with success!')
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.teacher.questions.all()