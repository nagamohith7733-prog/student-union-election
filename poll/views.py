from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, StudentProfileForm, CandidateForm
from .models import Candidate, Vote, StudentProfile
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Count
from .models import Vote, Candidate, ElectionPhase
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserUpdateForm, StudentProfileForm
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
import time
import logging
logger = logging.getLogger(__name__)
from django.http import JsonResponse
from django.conf import settings as django_settings

# Home Page
def home(request):
    return render(request, 'poll/home.html')


# Student Registration
def register(request):
    if request.method == 'POST':
        register_type = request.POST.get('register_type', 'user')
        
        if register_type == 'admin':
            admin_secret = request.POST.get('admin_secret_code')
            if admin_secret != django_settings.ADMIN_SECRET_CODE:
                messages.error(request, "Invalid Admin Secret Code.")
                return render(request, 'poll/register.html', {'form': StudentRegistrationForm()})
                
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'poll/register.html', {'form': StudentRegistrationForm()})
                
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return render(request, 'poll/register.html', {'form': StudentRegistrationForm()})
                
            # Create Admin User
            user = User.objects.create_superuser(username=username, email=email, password=password)
            messages.success(request, "Admin Registration successful! Please login.")
            return redirect('login')
            
        else:
            form = StudentRegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Create User
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password']
                    )
                    
                    # Create StudentProfile
                    StudentProfile.objects.create(
                        user=user,
                        Full_name=form.cleaned_data['Full_name'],
                        registration_number=form.cleaned_data['registration_number'],
                        course=form.cleaned_data['course'],
                        year=form.cleaned_data['year'],
                        profile_pic=form.cleaned_data.get('profile_pic')
                    )
                    
                    messages.success(request, "Registration successful! Please login.")
                    return redirect('login')
                    
                except IntegrityError:
                    messages.error(request, "This registration number is already registered")
                    return render(request, 'poll/register.html', {'form': form})
                    
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'poll/register.html', {'form': form})
    
#reg no login

# Student Login
@csrf_protect
def user_login(request):
    if request.method == 'POST':
        login_type = request.POST.get('login_type', 'user')
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')

        if login_type == 'admin':
            user = authenticate(username=identifier, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin:index')
            else:
                messages.error(request, "Invalid Admin Credentials.")
        else:
            try:
                profile = StudentProfile.objects.get(registration_number=identifier)
                user = authenticate(username=profile.user.username, password=password)
                if user:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid Password.")
            except StudentProfile.DoesNotExist:
                messages.error(request, "Registration number not found.")

    return render(request, 'poll/login.html')

@login_required
def dashboard(request):
    try:
        student_profile, created = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'Full_name': request.user.username,
                'registration_number': 'TEMP123',
                'course': 'Unknown',
                'year': 1
            }
        )
        
        profile_pic_url = None
        if student_profile.profile_pic:
            profile_pic_url = f"{student_profile.profile_pic.url}?v={int(time.time())}"

    except Exception as e:
        profile_pic_url = None
        messages.warning(request, "Please complete your profile information")

    phase = ElectionPhase.objects.order_by('-id').first()
    candidates = Candidate.objects.all()
    votes = Vote.objects.filter(voter=request.user)
    voted_positions = [vote.position for vote in votes]
    
    # Calculate winners if in Results phase
    winners = {}
    if phase and phase.phase == "Result":
        for candidate in candidates.order_by('-votes'):
            position = candidate.position
            if position not in winners or candidate.votes > winners[position].votes:
                winners[position] = candidate

    context = {
        'candidates': candidates,
        'phase': phase,
        'voted_positions': voted_positions,
        'profile_pic_url': profile_pic_url,
        'winners': winners  # Make sure this line has a comma after it if there are more items
    }
    return render(request, 'poll/dashboard.html', context)
# Voting View
@login_required
def vote(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    current_phase = ElectionPhase.objects.order_by('-id').first()

    if not current_phase or current_phase.phase != 'Voting':
      messages.error(request, "Voting is not active right now.")
      return redirect('dashboard')

    # Check if already voted for this position
    if Vote.objects.filter(voter=request.user, position=candidate.position).exists():
        messages.error(request, f"You have already voted for {candidate.position}!")
        return redirect('dashboard')

    Vote.objects.create(voter=request.user, candidate=candidate, position=candidate.position)
    candidate.votes += 1
    candidate.save()

    messages.success(request, f"Successfully voted for {candidate.name}!")
    return redirect('dashboard')

# Logout
def user_logout(request):
    logout(request)
    return redirect('home')

# Admin Panel: Add Candidate
@login_required
def add_candidate(request):
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate added successfully!")
            return redirect('dashboard')
    else:
        form = CandidateForm()

    return render(request, 'add_candidate.html', {'form': form})

# Admin Panel: Change Phase
@login_required
def change_phase(request, phase_name):
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')

    # Ensure we're using the correct model
    ElectionPhase.objects.all().update(is_active=False)
    
    # Create or update the phase
    phase, created = ElectionPhase.objects.get_or_create(
        phase=phase_name,
        defaults={'is_active': True}
    )
    
    if not created:
        phase.is_active = True
        phase.save()

    # Explicitly maintain user session
    request.session['phase_changed'] = True
    request.session.modified = True

    messages.success(request, f"{phase_name} phase is now active!")
    return redirect('admin:index')  # Redirect back to admin instead of dashboard
def results(request):
    # Debug: Print all phases
    print("All phases:", list(ElectionPhase.objects.all().values()))
    
    # Get the current active phase
    phase = ElectionPhase.objects.filter(is_active=True).first()
    print("Active phase:", phase)
    
    # If we're not in Results phase, redirect with message
    if not phase or phase.phase != "Result":
        print("Not in results phase or no active phase")
        messages.warning(request, "Results are not available yet!")
        return redirect('dashboard')
    
    # Get all candidates with their votes
    candidates = Candidate.objects.all().order_by('-votes')
    print("Candidates:", list(candidates.values('name', 'position', 'votes')))
    
    # Calculate winners - one per position
    winners = {}
    for candidate in candidates:
        position = candidate.position
        if position not in winners or candidate.votes > winners[position].votes:
            winners[position] = candidate
    
    print("Winners:", {k: v.name for k, v in winners.items()})
    
    context = {
        'phase': phase,
        'results': [{'candidate': c, 'votes': c.votes} for c in candidates],
        'winners': winners
    }
    
    return render(request, 'poll/results.html', context)
@login_required
def edit_profile(request):
    if request.method == 'POST':
        student = get_object_or_404(StudentProfile, user=request.user)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=request.user.studentprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
        else:
            # Print form errors for debugging
            print("User Form Errors:", user_form.errors)
            print("Profile Form Errors:", profile_form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = StudentProfileForm(instance=request.user.studentprofile)

    return render(request, 'poll/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, "Your password has been updated successfully!")
            return redirect('dashboard')
        else:
            # Add debug prints
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors below.")
            # Return with form errors instead of redirecting
            return render(request, 'poll/password.html', {'form': form})
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'poll/password.html', {'form': form})
