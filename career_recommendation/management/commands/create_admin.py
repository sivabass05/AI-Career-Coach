import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    help = "Create or promote the Render admin user"

    def handle(self, *args, **options):

        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL", "")
        password = os.getenv("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.ERROR(
                    "ADMIN_USERNAME or ADMIN_PASSWORD is not configured."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username
        )

        user.email = email

        user.set_password(password)

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user '{username}' created successfully."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Existing user '{username}' promoted to admin successfully."
                )
            )