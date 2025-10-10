from allauth.socialaccount.models import SocialToken
from django_q.tasks import schedule

from starminder.content.models import Entry, Post
from starminder.implementations.factory import ProviderLiteral, get_implementation


def start_job(provider: ProviderLiteral, social_token: SocialToken) -> None:
    implementation_class = get_implementation(provider=provider)
    implementation = implementation_class(access_token=social_token.token)
    entry_data_list = implementation.generate_entries()

    user = social_token.account.user
    post = Post.objects.create(user=user)

    for entry_data in entry_data_list:
        Entry.objects.create(
            post=post,
            provider=provider,
            provider_id=entry_data.provider_id,
            owner=entry_data.owner,
            owner_id=entry_data.owner_id,
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
            provider=token.account.provider,
            social_token=token,
        )
