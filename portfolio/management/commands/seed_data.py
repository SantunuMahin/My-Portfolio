from django.core.management.base import BaseCommand
from portfolio.models import Profile, Experience, Education, SkillCategory, Skill, Project, Service


class Command(BaseCommand):
    help = 'Seeds the database with sample portfolio data'

    def handle(self, *args, **kwargs):
        # Profile
        profile, _ = Profile.objects.get_or_create(id=1, defaults={
            'name': 'Santunu Kaysar',
            'title': 'Full Stack Django Developer',
            'bio': 'I am a passionate full stack developer based in Bangladesh with a strong focus on building elegant, performant web applications using Django and modern JavaScript.\n\nI love turning ideas into reality through clean code and thoughtful design. Always learning, always building.',
            'email': 'santunukaysarmahin@example.com',
            'location': 'Dhaka, Bangladesh',
            'github_url': 'https://github.com/',
            'linkedin_url': 'https://linkedin.com/in/',
        })
        self.stdout.write(self.style.SUCCESS(f'Profile: {profile.name}'))

        # Services
        services = [
            ('Web Development', 'Building responsive, full-stack web apps with Django, REST APIs, and modern front-end tools.', 'code-slash-outline'),
            ('Database Design', 'Designing efficient relational schemas with PostgreSQL, SQLite, and query optimization.', 'server-outline'),
            ('API Development', 'Creating robust REST APIs with Django REST Framework for web and mobile clients.', 'git-branch-outline'),
            ('UI/UX Design', 'Crafting clean, user-centered interfaces with a focus on accessibility and modern aesthetics.', 'color-palette-outline'),
        ]
        for title, desc, icon in services:
            Service.objects.get_or_create(title=title, defaults={'description': desc, 'icon_name': icon})
        self.stdout.write(self.style.SUCCESS('Services seeded'))

        # Experience
        exp_data = [
            {
                'company': 'Example Tech Ltd.',
                'role': 'Junior Django Developer',
                'start_date': 'January 2024',
                'is_current': True,
                'description': 'Built and maintained Django REST APIs serving 10k+ users\nImplemented CI/CD pipelines with GitHub Actions\nCollaborated with front-end teams on React integrations',
                'order': 1,
            },
            {
                'company': 'Freelance',
                'role': 'Full Stack Developer',
                'start_date': 'June 2022',
                'end_date': 'December 2023',
                'is_current': False,
                'description': 'Delivered 15+ custom Django projects for international clients\nManaged databases, deployments and domain configurations\nDeveloped e-commerce and CMS solutions',
                'order': 2,
            },
        ]
        for data in exp_data:
            Experience.objects.get_or_create(company=data['company'], role=data['role'], defaults=data)
        self.stdout.write(self.style.SUCCESS('Experiences seeded'))

        # Education
        Education.objects.get_or_create(
            institution='University of Dhaka',
            defaults={
                'degree': 'Bachelor of Science',
                'field': 'Computer Science & Engineering',
                'start_date': '2020',
                'end_date': '2024',
                'location': 'Dhaka, Bangladesh',
            }
        )
        self.stdout.write(self.style.SUCCESS('Education seeded'))

        # Skills
        skill_data = [
            ('Backend', ['Python', 'Django', 'Django REST Framework', 'FastAPI', 'Celery']),
            ('Frontend', ['HTML5', 'CSS3', 'JavaScript', 'Bootstrap', 'HTMX']),
            ('Database', ['PostgreSQL', 'MySQL', 'SQLite', 'Redis']),
            ('DevOps & Tools', ['Git', 'GitHub Actions', 'Docker', 'Linux', 'Nginx']),
        ]
        for idx, (cat_name, skills) in enumerate(skill_data):
            cat, _ = SkillCategory.objects.get_or_create(name=cat_name, defaults={'order': idx})
            for s_idx, skill_name in enumerate(skills):
                Skill.objects.get_or_create(name=skill_name, category=cat, defaults={'order': s_idx})
        self.stdout.write(self.style.SUCCESS('Skills seeded'))

        # Projects
        project_data = [
            {
                'title': 'Portfolio Website',
                'category': 'web',
                'description': 'A full-stack Django portfolio with blog, Kanban board, Pomodoro timer, and admin CMS.',
                'tech_stack': 'Django, Python, SQLite, CSS3, JavaScript',
                'is_featured': True,
                'order': 1,
            },
            {
                'title': 'E-commerce Platform',
                'category': 'web',
                'description': 'Feature-rich e-commerce application with cart, payments, and order management.',
                'tech_stack': 'Django, PostgreSQL, Stripe, Bootstrap',
                'is_featured': True,
                'order': 2,
            },
            {
                'title': 'Sentiment Analyser',
                'category': 'ml',
                'description': 'A machine learning model for classifying tweets as positive, negative, or neutral.',
                'tech_stack': 'Python, scikit-learn, NLTK, Flask',
                'is_featured': False,
                'order': 3,
            },
        ]
        for data in project_data:
            Project.objects.get_or_create(title=data['title'], defaults=data)
        self.stdout.write(self.style.SUCCESS('Projects seeded'))

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!'))
