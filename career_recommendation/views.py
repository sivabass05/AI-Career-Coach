from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserSkillAssessment

def login_view(request):
    if request.method == 'POST':
        u_input = request.POST.get('username')
        p_input = request.POST.get('password')
        
        # Email aaha irundha username-a kandupidikkum
        username_to_use = u_input
        if '@' in u_input:
            try:
                user_obj = User.objects.get(email=u_input)
                username_to_use = user_obj.username
            except User.DoesNotExist:
                pass

        user = authenticate(request, username=username_to_use, password=p_input)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard') # Dashboard-kku redirect aagum
        else:
            messages.error(request, 'Invalid Username/Email or Password!')
            return render(request, 'login.html')
            
    return render(request, 'login.html')
