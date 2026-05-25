from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile, Candidate
import re
from django.core.exceptions import ValidationError

# Student Registration Form
class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    # Add all student profile fields here
    Full_name = forms.CharField(max_length=100)
    registration_number = forms.CharField(max_length=12)
    course = forms.CharField(max_length=100)
    year = forms.IntegerField()
    profile_pic = forms.ImageField(required=False)
    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
        # Add (5, 'Fifth Year') if needed for your program
    ]
    year = forms.ChoiceField(choices=YEAR_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def clean_registration_number(self):
        reg_no = self.cleaned_data.get('registration_number')
        if StudentProfile.objects.filter(registration_number=reg_no).exists():
            raise ValidationError("This registration number is already in use")
        return reg_no
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data    

   
class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'position', 'manifesto', 'photo']
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class StudentProfileForm(forms.ModelForm):
    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'), 
        (3, 'Third Year'),
    ]
    
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    
    class Meta:
        model = StudentProfile
        fields = ['course', 'year', 'profile_pic']  # Only editable fields
        
    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic')
        if profile_pic:
            if profile_pic.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError("Image file too large ( > 2MB )")
            if not profile_pic.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise forms.ValidationError("Only JPG/PNG files are allowed")
        return profile_pic


class RegistrationLoginForm(forms.Form):
    registration_number = forms.CharField(max_length=12)
    password = forms.CharField(widget=forms.PasswordInput)