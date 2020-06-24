from django.shortcuts import render,HttpResponse, redirect
from django.conf import settings 
from django.contrib import messages
from .forms import TeacherSignUpForm,StudentSignUpForm
from django.contrib.auth.decorators import login_required
# Create your views here.

# Create your views here.
def index(request):
    context = {
        "icon" : settings.MEDIA_URL+"icon.png"
    }
    return render(request, 'dashboard/home.html',context)

def register(request):
    context = {
        "icon" : settings.MEDIA_URL+"icon.png"
    }
    return render(request, 'dashboard/signup.html',context)

def dashboard(request):
    context = {
        "icon" : settings.MEDIA_URL+"icon.png"
    }
    return render(request, 'dashboard/dashboard.html',context)

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