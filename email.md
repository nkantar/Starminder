Hi **{{ user_name }}**,

Here are your reminders for **{{ today }}**:
{% if stars|length %}{% for star in stars %}
- [**{{ star.full_name }}**]({{ star.url }}){% if star.description %} - {{ star.description }}{% endif %}
{% if star.homepage %}    - [{{ star.homepage }}]({{ star.homepage }})
{% endif %}    - {{ star.stargazers_count }} stargazer{% if star.stargazers_count != 1 %}s{% endif %}
    - {{ star.watchers_count }} watcher{% if star.watchers_count != 1 %}s{% endif %}{% endfor %}{% else %}You have no stars.{% endif %}

See you next time!

_Cheers, Starminder_

---

You are receiving this email because you set up Starminder in your GitHub account. Your fork is at [{{ fork_url }}]({{ fork_url }}) and the main project is at [https://github.com/nkantar/Starminder](https://github.com/nkantar/Starminder).
