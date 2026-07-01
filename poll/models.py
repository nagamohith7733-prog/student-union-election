from django.db import models
from django.contrib.auth.models import User

# Student Profile Extension
class StudentProfile(models.Model):
    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
        # (5, 'Fifth Year') if needed
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Full_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=12, unique=True)
    course = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png')
    updated_at = models.DateTimeField(auto_now=True)  # Add this field

    def save(self, *args, **kwargs):
        # Delete old file when updating
        if self.pk:
            old = StudentProfile.objects.get(pk=self.pk)
            if old.profile_pic and old.profile_pic != self.profile_pic:
                old.profile_pic.delete(save=False)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.user.username
    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"
# Candidate Model
class Candidate(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, db_index=True)
    manifesto = models.TextField()
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.position}"

# Voting Record
class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='vote_records')
    position = models.CharField(max_length=100, db_index=True)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'position')  # DB-level duplicate vote prevention
        indexes = [
            models.Index(fields=['voter', 'position']),
        ]

    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.name} ({self.position})"

# Election Phase Controller

# Remove the entire Phase class and keep only:
class ElectionPhase(models.Model):
    PHASE_CHOICES = [
        ('Nomination', 'Nomination'),
        ('Voting', 'Voting'),
        ('Result', 'Result'),
    ]
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='Nomination')
    is_active = models.BooleanField(default=True)  # Make sure this exists

    def __str__(self):
        return self.phase