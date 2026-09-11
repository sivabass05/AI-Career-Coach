import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    help = "Create the Render admin superuser if it does not exist"

    def handle(self, *args, **options):

        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL", "")
        password = os.getenv("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "ADMIN_USERNAME or ADMIN_PASSWORD is not configured."
                )
            )
            return

        user = User.objects.filter(
            username=username
        ).first()

        if user:
            self.stdout.write(
                self.style.SUCCESS(
                    "Admin user already exists. No changes made."
                )
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin superuser '{user.username}' created successfully."
            )
        )