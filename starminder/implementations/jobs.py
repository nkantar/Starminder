from allauth.socialaccount.models import SocialToken
from django_q.tasks import schedule

from starminder.content.models import Entry, Post
from starminder.implementations.factory import ProviderLiteral, get_implementation


def start_job(provider: ProviderLiteral, social_token: str, user_id: int) -> None:
    implementation_class = get_implementation(provider=provider)
    implementation = implementation_class(access_token=social_token)
    entry_data_list = implementation.generate_entries()

    post = Post.objects.create(user_id=user_id)

    for entry_data in entry_data_list:
        Entry.objects.create(
            post=post,
            provider=provider,
            provider_id=entry_data.provider_id,
            owner=entry_data.owner,
            owner_id=entry_data.owner_id,
            name=entry_data.name,
            description=entry_data.description,
            star_count=entry_data.star_count,
            repo_url=entry_data.repo_url,
            project_url=entry_data.project_url,
        )


def start_jobs() -> None:
    tokens = SocialToken.objects.all()

    for token in tokens:
        schedule(
            "starminder.implementations.jobs.start_job",
            token.account.provider,
            token.token,
            token.account.user.id,
        )
