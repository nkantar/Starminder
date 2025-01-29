from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE, Model, OneToOneField
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    pass

    def __str__(self) -> str:
        return self.email


class UserProfile(Model):
    user = OneToOneField("core.CustomUser", on_delete=CASCADE)

    def __str__(self) -> str:
        return f"Profile for {self.user.email}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs) -> None:
    UserProfile.objects.get_or_create(user=instance)
