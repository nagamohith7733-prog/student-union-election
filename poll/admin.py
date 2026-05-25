from django.contrib import admin
from .models import Candidate, Vote, ElectionPhase, StudentProfile
from django.utils.html import format_html

from django.contrib.auth.models import Group  # Import Group model

# Unregister Group from admin
admin.site.unregister(Group)
  
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    search_fields = ('name', 'position')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'candidate')
    search_fields = ('voter__username', 'candidate__name')

@admin.register(ElectionPhase)
class ElectionPhaseAdmin(admin.ModelAdmin):
    list_display = ('phase',)

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