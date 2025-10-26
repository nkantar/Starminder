# Starminder

**Starminder** is a GitHub starred project reminder. ⭐

If you have any number of starred projects, you probably have very little idea what's in there. **Starminder** aims to periodically remind you of some random ones, so you don't forget about them entirely.


## Usage from Docker Hub

You can run Starminder using the official Docker image from Docker Hub.

### 1. Pull the image

```bash
docker pull pcarorevuelta/starminder:latest
```

### 2. Run the container

To run the container, you will need to provide several environment variables.

```bash
docker run -d \
  -e DJANGO_SECRET_KEY="your-secret-key" \
  -e DJANGO_ALLOWED_HOSTS="your-domain.com" \
  -e DJANGO_SITE_DOMAIN_NAME="your-domain.com" \
  -e DJANGO_SITE_DISPLAY_NAME="Starminder" \
  -e DATABASE_URL="postgres://user:password@host:port/dbname" \
  -p 8000:8000 \
  pcarorevuelta/starminder:latest
```

### Environment Variables

| Variable                   | Description                                                                                                 | Required |
| -------------------------- | ----------------------------------------------------------------------------------------------------------- | -------- |
| `DJANGO_SECRET_KEY`        | A secret key for a particular Django installation. This is used to provide cryptographic signing.           | **Yes**  |
| `DJANGO_ALLOWED_HOSTS`     | A list of strings representing the host/domain names that this Django site can serve.                       | **Yes**  |
| `DJANGO_SITE_DOMAIN_NAME`  | The domain name of the site.                                                                                | **Yes**  |
| `DJANGO_SITE_DISPLAY_NAME` | The display name of the site.                                                                               | No       |
| `DATABASE_URL`             | The URL of the database.                                                                                    | **Yes**  |
| `SENTRY_DSN`               | The DSN for Sentry integration.                                                                             | No       |
| `FORWARDEMAIL_TOKEN`       | The token for ForwardEmail integration.                                                                     | No       |
| `PUSHOVER_USER_KEY`        | The user key for Pushover integration.                                                                      | No       |
| `PUSHOVER_API_TOKEN`       | The API token for Pushover integration.                                                                     | No       |
| `DJANGO_ADMIN_PREFIX`      | The prefix for the Django admin interface.                                                                  | No       |
| `GITHUB_CLIENT_ID`         | The Client ID of your GitHub OAuth application.                                                             | **Yes**  |
| `GITHUB_CLIENT_SECRET`     | The Client Secret of your GitHub OAuth application.                                                         | **Yes**  |

### SQLite Support

This image supports SQLite out of the box. If you do not provide a `DATABASE_URL`, the application will create and use a `db.sqlite3` file inside the container.

**Note:** Using SQLite is not recommended for production environments. The database will be lost if the container is removed. For persistent data, it is recommended to use a managed database and provide the `DATABASE_URL`.

#### Persisting the SQLite database

To persist the SQLite database, you can mount a volume to the path of the database file inside the container. By default, the database is created at `/app/db.sqlite3`.

You can also use the `DATABASE_URL` environment variable to specify a path for the SQLite database.

**Example using a bind mount:**

```bash
docker run -d \
  -v /path/to/your/db.sqlite3:/app/db.sqlite3 \
  -p 8000:8000 \
  pcarorevuelta/starminder:latest
```

**Example using `DATABASE_URL`:**

```bash
docker run -d \
  -e DATABASE_URL="sqlite:////data/db.sqlite3" \
  -v /path/to/your/data:/data \
  -p 8000:8000 \
  pcarorevuelta/starminder:latest
```

## Contributing

Unlike most of my projects, contributions are not explicitly encouraged, though they're not discouraged, either.


## License

[MIT](https://choosealicense.com/licenses/mit/)
