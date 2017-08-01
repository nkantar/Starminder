from datetime import datetime
import random

import github3
from jinja2 import Environment, PackageLoader, select_autoescape
import parsenvy
from raven import Client
import redis
from rq import Queue
from sqlalchemy import or_

from starminder import db, User
from helpers import send_email


REDIS_URL = parsenvy.str('REDIS_URL')
SENTRY_DSN = parsenvy.str('SENTRY_DSN')


q = Queue(connection=redis.from_url(REDIS_URL))

client = Client(SENTRY_DSN)

env = Environment(
    loader=PackageLoader('starminder', 'templates'),
    autoescape=select_autoescape(['html', 'txt'])
)

now = datetime.utcnow()
hour = now.hour
day = now.weekday()
users = (db.session.query(User).filter(User.time == hour,
                                       or_(User.day == -1, User.day == day))
                               .all())

for user in users:

    if user.email is None:
        error_message = 'User {0} ({1}) has no email address.'.format(
            user.github_username,
            user.id
        )
        client.captureMessage(error_message)

    gh = github3.login(token=user.github_token)
    gh_user = gh.user()
    all_stars = list(gh_user.iter_starred())
    if len(all_stars) >= user.number:
        limit = user.number
    else:
        limit = len(all_stars)
    stars = random.sample(all_stars, limit)

    html_template = env.get_template('email.html')
    text_template = env.get_template('email.txt')

    html_rendered = html_template.render(user=user, stars=stars, now=now)
    text_rendered = text_template.render(user=user, stars=stars, now=now)

    subject = '[Starminder] Reminders for {0}'.format(now.strftime('%Y-%m-%d'))

    q.enqueue(send_email,
              email=user.email,
              subject=subject,
              text=text_rendered,
              html=html_rendered)
