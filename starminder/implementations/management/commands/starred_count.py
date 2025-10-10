from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken
from github import Github


class Command(BaseCommand):
    help = "Fetch the number of starred projects for a user"

    def add_arguments(self, parser):
        parser.add_argument("token_id", type=int, help="SocialToken ID to use")

    def handle(self, *args, **options):
        token_id = options["token_id"]

        try:
            social_token = SocialToken.objects.get(id=token_id)
        except SocialToken.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"No SocialToken found with ID {token_id}")
            )
            return

        github = Github(social_token.token)
        user = github.get_user()
        starred_count = user.get_starred().totalCount

        self.stdout.write(
            self.style.SUCCESS(f"User has {starred_count} starred repositories")
        )
