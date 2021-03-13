{% load url_format %}Hi {{ profile.username }},

Here are your reminders for {{ today }}:
{% for repo in profile.random_starred %}
- {{ repo.owner.login }}/{{ repo.name }}{% if repo.description %} - {{ repo.description }}{% endif %}
    - {% url_format link_format repo.html_url repo.html_url repo.html_url %}
{% if repo.homepage %}    - {% url_format link_format repo.homepage repo.homepage repo.homepage %}
{% endif %}    - {{ repo.stargazers_count }} stargazer{% if repo.stargazers_count != 1 %}s{% endif %}{% endfor %}

See you next time!

Cheers, Starminder

To unsubscribe, please go to {% url_format link_format "https://starminder.xyz" "https://starminder.xyz" "https://starminder.xyz" %}, log in, and delete your account.

WeWork (c/o Nik Kantar, Starminder), 10000 Washington Blvd, 6th Floor, Culver City, CA 90232, USA
