import re
import time
from urllib.parse import urlsplit

import httpx
from httpx_retries import Retry, RetryTransport
import idna
from loguru import logger
import sentry_sdk


FAMILY_DOH_URL = "https://family.cloudflare-dns.com/dns-query"
BLOCKED_ANSWERS = {"0.0.0.0", "::"}
DOH_TIME_BUDGET = 60  # seconds per reminder

SCHEME_URL_RE = re.compile(r"""https?://[^\s<>"')\[\]]+""", re.IGNORECASE)
# labels are unicode letters/digits (matching url-regex-safe's breadth); the
# last label must be all letters so version strings and decimals don't match
BARE_DOMAIN_RE = re.compile(r"\b(?:[^\W_](?:[\w-]*[^\W_])?\.)+[^\W\d_]{2,}\b")


class DohTimeBudgetExceededError(Exception):
    pass


def extract_urls(text: str) -> list[str]:
    """Extract URL-ish tokens, including bare domains, the way spam scanners do."""
    urls = SCHEME_URL_RE.findall(text)
    remainder = SCHEME_URL_RE.sub(" ", text)
    urls.extend(BARE_DOMAIN_RE.findall(remainder))
    return urls


def extract_hostname(url: str) -> str | None:
    # urlsplit and the hostname property both raise ValueError on bracketed
    # input, e.g. placeholder text like "https://[your-domain]/api"
    try:
        split = urlsplit(url)
        if not split.hostname:
            # GitHub homepage values are often schemeless, e.g. "cheat.sh"
            split = urlsplit(f"//{url}")
        return split.hostname
    except ValueError:
        return None


def query_family_dns(client: httpx.Client, domain: str) -> bool:
    # IDNA 2008 first (matches modern registry encodings, e.g. faß.de),
    # stdlib IDNA 2003 as fallback; unencodable domains go through raw and
    # any resulting DoH error lands in the fail-closed handler
    try:
        domain = idna.encode(domain).decode("ascii")
    except idna.IDNAError:
        try:
            domain = domain.encode("idna").decode("ascii")
        except UnicodeError:
            pass

    response = client.get(
        FAMILY_DOH_URL,
        params={"name": domain, "type": "A"},
        headers={"Accept": "application/dns-json"},
    )
    response.raise_for_status()
    data = response.json()

    # 0 is NOERROR and 3 is NXDOMAIN; anything else (e.g. SERVFAIL) means no
    # verdict, so raise into the fail-closed handler rather than read as clean
    status = data.get("Status")
    if status not in (0, 3):
        raise ValueError(f"DoH query for {domain} returned status {status}")

    answers = data.get("Answer") or []
    comments = data.get("Comment") or []

    return any(answer.get("data") in BLOCKED_ANSWERS for answer in answers) or any(
        "EDE(17)" in comment for comment in comments
    )


def get_flagged_urls(urls: list[str]) -> set[str]:
    """Return the subset of urls considered unsafe for outgoing email.

    Fails closed: a URL is flagged if its hostname is filtered by Cloudflare
    Family DNS, if no hostname can be extracted, if the check errors, or if
    the time budget runs out before it can be checked.
    """
    if not urls:
        return set()

    flagged_urls = set()
    verdicts: dict[str, bool] = {}
    skipped_urls = []
    deadline = time.monotonic() + DOH_TIME_BUDGET

    httpx_transport = RetryTransport(retry=Retry(total=3, backoff_factor=0.5))
    with httpx.Client(transport=httpx_transport, timeout=5) as client:
        for url in urls:
            hostname = extract_hostname(url)

            if hostname is None:
                logger.warning(f"No hostname in {url}, omitting from email")
                flagged_urls.add(url)
                continue

            if hostname not in verdicts:
                if time.monotonic() > deadline:
                    logger.warning(
                        f"DoH time budget exhausted, omitting {url} from email"
                    )
                    flagged_urls.add(url)
                    skipped_urls.append(url)
                    continue

                try:
                    verdicts[hostname] = query_family_dns(client, hostname)
                except Exception:
                    logger.exception(
                        f"Family DNS check failed for {hostname}, omitting from email"
                    )
                    verdicts[hostname] = True

            if verdicts[hostname]:
                logger.info(f"Omitting {url} from email (hostname {hostname})")
                flagged_urls.add(url)

    if skipped_urls:
        sentry_sdk.capture_exception(
            DohTimeBudgetExceededError(
                f"DoH time budget ({DOH_TIME_BUDGET}s) exceeded, "
                f"failed closed on {len(skipped_urls)} unchecked URLs"
            ),
            extras={"skipped_urls": skipped_urls},
        )

    return flagged_urls
