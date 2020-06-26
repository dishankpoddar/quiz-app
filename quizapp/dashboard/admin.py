from django.contrib import admin
from .models import (User,Quiz,Student,Teacher,AssignedQuiz,Question,Answer,SelectedQuestion)

# Register your models here.
admin.site.register(User)
admin.site.register(Quiz)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(AssignedQuiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(SelectedQuestion)
