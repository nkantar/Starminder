import pytest
from django.contrib.auth import get_user_model

from starminder.core.forms import UserProfileConfigForm
from starminder.core.models import UserProfile

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def user_profile(user):
    return user.user_profile


@pytest.mark.django_db
class TestUserProfileConfigForm:
    def test_form_with_valid_data(self, user_profile):
        form_data = {
            "max_entries": 10,
            "day_of_week": UserProfile.MONDAY,
            "hour_of_day": 12,
            "include_archived": True,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert form.is_valid()

    def test_form_with_every_day(self, user_profile):
        form_data = {
            "max_entries": 5,
            "day_of_week": UserProfile.EVERY_DAY,
            "hour_of_day": 9,
            "include_archived": True,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert form.is_valid()

    def test_form_with_min_max_entries(self, user_profile):
        form_data = {
            "max_entries": 1,
            "day_of_week": UserProfile.TUESDAY,
            "hour_of_day": 0,
            "include_archived": True,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert form.is_valid()

    def test_form_with_max_hour(self, user_profile):
        form_data = {
            "max_entries": 5,
            "day_of_week": UserProfile.WEDNESDAY,
            "hour_of_day": 23,
            "include_archived": True,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert form.is_valid()

    def test_form_with_zero_max_entries_invalid(self, user_profile):
        form_data = {
            "max_entries": 0,
            "day_of_week": UserProfile.MONDAY,
            "hour_of_day": 12,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert not form.is_valid()
        assert "max_entries" in form.errors

    def test_form_with_negative_max_entries_invalid(self, user_profile):
        form_data = {
            "max_entries": -5,
            "day_of_week": UserProfile.MONDAY,
            "hour_of_day": 12,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert not form.is_valid()
        assert "max_entries" in form.errors

    def test_form_with_invalid_day_of_week(self, user_profile):
        form_data = {
            "max_entries": 5,
            "day_of_week": 99,
            "hour_of_day": 12,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert not form.is_valid()
        assert "day_of_week" in form.errors

    def test_form_with_negative_hour_invalid(self, user_profile):
        form_data = {
            "max_entries": 5,
            "day_of_week": UserProfile.MONDAY,
            "hour_of_day": -1,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert not form.is_valid()
        assert "hour_of_day" in form.errors

    def test_form_with_hour_above_23_invalid(self, user_profile):
        form_data = {
            "max_entries": 5,
            "day_of_week": UserProfile.MONDAY,
            "hour_of_day": 24,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert not form.is_valid()
        assert "hour_of_day" in form.errors

    def test_form_has_correct_fields(self):
        form = UserProfileConfigForm()
        assert "reminder_email" in form.fields
        assert "max_entries" in form.fields
        assert "day_of_week" in form.fields
        assert "hour_of_day" in form.fields
        assert "include_archived" in form.fields
        assert len(form.fields) == 5

    def test_form_max_entries_widget_has_min_attribute(self):
        form = UserProfileConfigForm()
        widget_attrs = form.fields["max_entries"].widget.attrs
        assert "min" in widget_attrs
        assert widget_attrs["min"] == 0

    def test_form_hour_of_day_widget_has_min_max_attributes(self):
        form = UserProfileConfigForm()
        widget_attrs = form.fields["hour_of_day"].widget.attrs
        assert "min" in widget_attrs
        assert widget_attrs["min"] == 0
        assert "max" in widget_attrs
        assert widget_attrs["max"] == 23

    def test_form_has_correct_labels(self):
        form = UserProfileConfigForm()
        assert form.fields["reminder_email"].label == "Reminder email address"
        assert form.fields["max_entries"].label == "Maximum entries per reminder"
        assert form.fields["day_of_week"].label == "Day of week"
        assert form.fields["hour_of_day"].label == "Hour of day (0-23)"

    def test_form_save_updates_profile(self, user_profile):
        initial_max_entries = user_profile.max_entries
        form_data = {
            "max_entries": initial_max_entries + 5,
            "day_of_week": UserProfile.FRIDAY,
            "hour_of_day": 18,
            "include_archived": True,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert form.is_valid()

        saved_profile = form.save()
        assert saved_profile.max_entries == initial_max_entries + 5
        assert saved_profile.day_of_week == UserProfile.FRIDAY
        assert saved_profile.hour_of_day == 18

    def test_form_with_all_day_choices(self, user_profile):
        valid_days = [
            UserProfile.EVERY_DAY,
            UserProfile.MONDAY,
            UserProfile.TUESDAY,
            UserProfile.WEDNESDAY,
            UserProfile.THURSDAY,
            UserProfile.FRIDAY,
            UserProfile.SATURDAY,
            UserProfile.SUNDAY,
        ]

        for day in valid_days:
            form_data = {
                "max_entries": 5,
                "day_of_week": day,
                "hour_of_day": 12,
                "include_archived": True,
            }
            form = UserProfileConfigForm(data=form_data, instance=user_profile)
            assert form.is_valid(), f"Form should be valid for day {day}"

    def test_form_without_instance(self):
        form = UserProfileConfigForm()
        assert form.instance is not None
        assert isinstance(form.instance, UserProfile)

    def test_form_with_missing_required_field(self, user_profile):
        form_data = {
            "max_entries": 5,
            "hour_of_day": 12,
        }
        form = UserProfileConfigForm(data=form_data, instance=user_profile)
        assert not form.is_valid()
        assert "day_of_week" in form.errors

    def test_form_with_empty_data(self, user_profile):
        form = UserProfileConfigForm(data={}, instance=user_profile)
        assert not form.is_valid()
        assert "max_entries" in form.errors
        assert "day_of_week" in form.errors
        assert "hour_of_day" in form.errors
