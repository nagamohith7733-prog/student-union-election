from django.contrib import admin
from .models import Candidate, Vote, ElectionPhase, StudentProfile
from django.utils.html import format_html

from django.contrib.auth.models import User, Group  # Import User and Group model
from django.contrib.auth.admin import UserAdmin
from django import forms

# Unregister Group from admin
admin.site.unregister(Group)

# Custom form to allow adding Users without typing a password
class NoPasswordUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set a default password automatically
        user.set_password("Student@123")
        if commit:
            user.save()
        return user

class CustomUserAdmin(UserAdmin):
    add_form = NoPasswordUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email')}
        ),
    )

# Replace the default User admin with our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
  
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    search_fields = ('name', 'position')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'candidate', 'position', 'voted_at')
    search_fields = ('voter__username', 'candidate__name', 'position')
    list_filter = ('position', 'voted_at')
    actions = ['delete_selected_votes', 'reset_all_votes']

    def delete_selected_votes(self, request, queryset):
        """Delete selected votes and update candidate vote counts."""
        for vote in queryset:
            vote.candidate.votes = max(0, vote.candidate.votes - 1)
            vote.candidate.save()
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Deleted {count} vote(s) and updated candidate counts.")
    delete_selected_votes.short_description = "Delete selected votes (updates candidate counts)"

    def reset_all_votes(self, request, queryset):
        """Delete ALL votes and reset all candidate vote counts to 0."""
        Vote.objects.all().delete()
        Candidate.objects.all().update(votes=0)
        self.message_user(request, "All votes deleted and candidate counts reset to 0.")
    reset_all_votes.short_description = "RESET ALL VOTES (deletes everything, resets counts)"

@admin.register(ElectionPhase)
class ElectionPhaseAdmin(admin.ModelAdmin):
    list_display = ('phase', 'is_active')
    list_editable = ('is_active',)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user','email', 'Full_name', 'registration_number', 'year', 'course', 'profile_image_tag')
    readonly_fields = ['profile_image_tag']
    list_filter = ('user__is_active',)
    def profile_image_tag(self, obj):
        if obj.profile_pic:
            return format_html('<img src="{}" style="height: 60px; border-radius: 5px;" />', obj.profile_pic.url)
        return "No Image"

    profile_image_tag.short_description = 'Profile Picture'
    def email(self, obj):
        return obj.user.email

    email.short_description = 'Email'
    def is_active(self, obj):
        return obj.user.is_active
    is_active.boolean = True
    is_active.short_description = 'Active?'