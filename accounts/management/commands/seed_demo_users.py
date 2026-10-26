from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Department, Profile


class Command(BaseCommand):
    help = "Seed or reset default demo accounts (Admin, HOD, Faculty) for testing and deployment."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding default demo departments and accounts..."))

        # 1. Departments
        dept_biot, _ = Department.objects.get_or_create(
            code="BIOT",
            defaults={"name": "Biotechnology", "degree": "B.Tech"}
        )
        dept_cse, _ = Department.objects.get_or_create(
            code="CSE",
            defaults={"name": "Computer Science & Engineering", "degree": "B.Tech"}
        )

        users_to_seed = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin@123",
                "first_name": "System",
                "last_name": "Administrator",
                "role": Profile.ROLE_ADMIN,
                "department": None,
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "hod_biot",
                "email": "hod.biot@example.com",
                "password": "hod@123",
                "first_name": "Dr. Ramesh",
                "last_name": "Sharma",
                "role": Profile.ROLE_HOD,
                "department": dept_biot,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "faculty1",
                "email": "faculty.biot@example.com",
                "password": "fac@123",
                "first_name": "Prof. Priya",
                "last_name": "Nair",
                "role": Profile.ROLE_FACULTY,
                "department": dept_biot,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "hod_cse",
                "email": "hod.cse@example.com",
                "password": "hod@123",
                "first_name": "Dr. Ananya",
                "last_name": "Verma",
                "role": Profile.ROLE_HOD,
                "department": dept_cse,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "faculty_cse",
                "email": "faculty.cse@example.com",
                "password": "fac@123",
                "first_name": "Prof. Suresh",
                "last_name": "Kumar",
                "role": Profile.ROLE_FACULTY,
                "department": dept_cse,
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        for item in users_to_seed:
            user, created = User.objects.get_or_create(
                username=item["username"],
                defaults={
                    "email": item["email"],
                    "first_name": item["first_name"],
                    "last_name": item["last_name"],
                    "is_staff": item["is_staff"],
                    "is_superuser": item["is_superuser"],
                    "is_active": True,
                }
            )
            # Ensure password is set correctly
            user.set_password(item["password"])
            user.is_active = True
            user.is_staff = item["is_staff"]
            user.is_superuser = item["is_superuser"]
            user.first_name = item["first_name"]
            user.last_name = item["last_name"]
            user.save()

            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "role": item["role"],
                    "department": item["department"],
                }
            )
            profile.role = item["role"]
            profile.department = item["department"]
            profile.save()

            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} {item['role']}: username='{item['username']}' | password='{item['password']}'"
                )
            )

        self.stdout.write(self.style.SUCCESS("All demo accounts are ready!"))
