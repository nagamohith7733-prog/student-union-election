"""
Management command to seed the database with test data:
- 20 student users with profiles
- 8 candidates across 4 positions
- ElectionPhase set to 'Voting'
- Random votes from students

Usage: python manage.py seed_data
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from poll.models import StudentProfile, Candidate, Vote, ElectionPhase
from django.db import transaction


class Command(BaseCommand):
    help = 'Seeds database with test users, candidates, phases, and votes for performance testing'

    POSITIONS = ['President', 'Vice President', 'Secretary', 'Treasurer']

    CANDIDATES_DATA = [
        {'name': 'Aisha Patel', 'position': 'President', 'manifesto': 'I will bring transparency and accountability to student governance. My plan includes open town halls and a digital feedback portal.'},
        {'name': 'Ravi Kumar', 'position': 'President', 'manifesto': 'Innovation and inclusivity are my priorities. I will launch a student app for direct communication with the union.'},
        {'name': 'Priya Sharma', 'position': 'Vice President', 'manifesto': 'I will bridge the gap between students and faculty. Monthly meetings and a new mentorship programme are my goals.'},
        {'name': 'Arjun Reddy', 'position': 'Vice President', 'manifesto': 'Sports, culture, and academics — I will ensure balanced representation for every student interest.'},
        {'name': 'Sneha Gupta', 'position': 'Secretary', 'manifesto': 'Documentation, communication, and organisation. I will streamline union operations with digital tools.'},
        {'name': 'Karthik Nair', 'position': 'Secretary', 'manifesto': 'I will keep every student informed with weekly newsletters and a revamped notice board system.'},
        {'name': 'Divya Menon', 'position': 'Treasurer', 'manifesto': 'Financial transparency is non-negotiable. I will publish monthly budget reports and host open audits.'},
        {'name': 'Rohan Singh', 'position': 'Treasurer', 'manifesto': 'I will fight for better fund allocation towards student clubs and welfare programmes.'},
    ]

    STUDENTS_DATA = [
        {'username': 'student01', 'email': 'student01@college.edu', 'full_name': 'Amit Verma', 'reg_no': 'REG2024001', 'course': 'Computer Science', 'year': 1},
        {'username': 'student02', 'email': 'student02@college.edu', 'full_name': 'Neha Joshi', 'reg_no': 'REG2024002', 'course': 'Electronics', 'year': 2},
        {'username': 'student03', 'email': 'student03@college.edu', 'full_name': 'Rahul Das', 'reg_no': 'REG2024003', 'course': 'Mechanical', 'year': 3},
        {'username': 'student04', 'email': 'student04@college.edu', 'full_name': 'Meera Iyer', 'reg_no': 'REG2024004', 'course': 'Civil', 'year': 1},
        {'username': 'student05', 'email': 'student05@college.edu', 'full_name': 'Vikram Rao', 'reg_no': 'REG2024005', 'course': 'Computer Science', 'year': 2},
        {'username': 'student06', 'email': 'student06@college.edu', 'full_name': 'Anjali Pillai', 'reg_no': 'REG2024006', 'course': 'Electronics', 'year': 3},
        {'username': 'student07', 'email': 'student07@college.edu', 'full_name': 'Suresh Babu', 'reg_no': 'REG2024007', 'course': 'Mechanical', 'year': 1},
        {'username': 'student08', 'email': 'student08@college.edu', 'full_name': 'Lakshmi Naidu', 'reg_no': 'REG2024008', 'course': 'Civil', 'year': 2},
        {'username': 'student09', 'email': 'student09@college.edu', 'full_name': 'Tarun Bhatt', 'reg_no': 'REG2024009', 'course': 'Computer Science', 'year': 3},
        {'username': 'student10', 'email': 'student10@college.edu', 'full_name': 'Kavya Shetty', 'reg_no': 'REG2024010', 'course': 'Electronics', 'year': 1},
        {'username': 'student11', 'email': 'student11@college.edu', 'full_name': 'Manoj Tiwari', 'reg_no': 'REG2024011', 'course': 'Mechanical', 'year': 2},
        {'username': 'student12', 'email': 'student12@college.edu', 'full_name': 'Pooja Hegde', 'reg_no': 'REG2024012', 'course': 'Civil', 'year': 3},
        {'username': 'student13', 'email': 'student13@college.edu', 'full_name': 'Deepak Chandra', 'reg_no': 'REG2024013', 'course': 'Computer Science', 'year': 1},
        {'username': 'student14', 'email': 'student14@college.edu', 'full_name': 'Swathi Rani', 'reg_no': 'REG2024014', 'course': 'Electronics', 'year': 2},
        {'username': 'student15', 'email': 'student15@college.edu', 'full_name': 'Harish Mohan', 'reg_no': 'REG2024015', 'course': 'Mechanical', 'year': 3},
        {'username': 'student16', 'email': 'student16@college.edu', 'full_name': 'Roshni Kapoor', 'reg_no': 'REG2024016', 'course': 'Civil', 'year': 1},
        {'username': 'student17', 'email': 'student17@college.edu', 'full_name': 'Ganesh Murthy', 'reg_no': 'REG2024017', 'course': 'Computer Science', 'year': 2},
        {'username': 'student18', 'email': 'student18@college.edu', 'full_name': 'Nithya Raj', 'reg_no': 'REG2024018', 'course': 'Electronics', 'year': 3},
        {'username': 'student19', 'email': 'student19@college.edu', 'full_name': 'Siddharth Jain', 'reg_no': 'REG2024019', 'course': 'Mechanical', 'year': 1},
        {'username': 'student20', 'email': 'student20@college.edu', 'full_name': 'Aparna Devi', 'reg_no': 'REG2024020', 'course': 'Civil', 'year': 2},
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing test data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Clearing existing test data...')
            Vote.objects.all().delete()
            Candidate.objects.all().delete()
            # Only delete test student users (not admin/superusers)
            test_usernames = [s['username'] for s in self.STUDENTS_DATA]
            StudentProfile.objects.filter(user__username__in=test_usernames).delete()
            User.objects.filter(username__in=test_usernames).delete()
            ElectionPhase.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared!'))

        # 1. Create students
        self.stdout.write('Creating 20 student users...')
        students = []
        for s in self.STUDENTS_DATA:
            user, created = User.objects.get_or_create(
                username=s['username'],
                defaults={'email': s['email']}
            )
            if created:
                user.set_password('Student@123')
                user.save()
            profile, _ = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'Full_name': s['full_name'],
                    'registration_number': s['reg_no'],
                    'course': s['course'],
                    'year': s['year'],
                }
            )
            students.append(user)
        self.stdout.write(self.style.SUCCESS(f'  [OK] {len(students)} students ready'))

        # 2. Create candidates
        self.stdout.write('Creating 8 candidates across 4 positions...')
        candidates_by_position = {}
        for c in self.CANDIDATES_DATA:
            candidate, _ = Candidate.objects.get_or_create(
                name=c['name'],
                position=c['position'],
                defaults={'manifesto': c['manifesto'], 'votes': 0}
            )
            candidates_by_position.setdefault(c['position'], []).append(candidate)
        self.stdout.write(self.style.SUCCESS(f'  [OK] {sum(len(v) for v in candidates_by_position.values())} candidates ready'))

        # 3. Set election phase to Voting
        self.stdout.write('Setting election phase to Voting...')
        ElectionPhase.objects.all().update(is_active=False)
        phase, _ = ElectionPhase.objects.get_or_create(
            phase='Voting',
            defaults={'is_active': True}
        )
        if not phase.is_active:
            phase.is_active = True
            phase.save()
        self.stdout.write(self.style.SUCCESS(f'  [OK] Phase set to: {phase.phase}'))

        # 4. Cast random votes (each student votes for one candidate per position)
        self.stdout.write('Casting random votes...')
        votes_created = 0
        for student in students:
            for position, candidates in candidates_by_position.items():
                # Skip if already voted for this position
                if Vote.objects.filter(voter=student, position=position).exists():
                    continue
                chosen = random.choice(candidates)
                Vote.objects.create(voter=student, candidate=chosen, position=position)
                # Use F() expression for atomic vote count update
                from django.db.models import F
                Candidate.objects.filter(id=chosen.id).update(votes=F('votes') + 1)
                votes_created += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] {votes_created} votes cast'))

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('  SEED DATA COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'  Students:   {User.objects.filter(is_staff=False).count()}')
        self.stdout.write(f'  Candidates: {Candidate.objects.count()}')
        self.stdout.write(f'  Votes:      {Vote.objects.count()}')
        self.stdout.write(f'  Phase:      {ElectionPhase.objects.filter(is_active=True).first()}')
        self.stdout.write('')
        self.stdout.write('  Login credentials for all test students:')
        self.stdout.write('  Registration No: REG2024001 through REG2024020')
        self.stdout.write('  Password:        Student@123')
        self.stdout.write(self.style.SUCCESS('=' * 50))
