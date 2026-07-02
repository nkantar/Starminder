from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from starminder.content.linkcheck import (
    DohTimeBudgetExceededError,
    extract_hostname,
    extract_urls,
    get_flagged_urls,
    query_family_dns,
)


# extract_urls tests


def test_extract_urls_scheme_url_in_prose() -> None:
    assert extract_urls("Check out https://example.com/docs for more") == [
        "https://example.com/docs"
    ]


def test_extract_urls_bare_domain_in_prose() -> None:
    assert extract_urls("try cheat.sh today") == ["cheat.sh"]


def test_extract_urls_does_not_double_extract() -> None:
    assert extract_urls("see https://example.com/path") == ["https://example.com/path"]


def test_extract_urls_multiple() -> None:
    assert extract_urls("cheat.sh mirror at https://cht.sh and wifiphisher.org") == [
        "https://cht.sh",
        "cheat.sh",
        "wifiphisher.org",
    ]


def test_extract_urls_ignores_bracketed_placeholders() -> None:
    assert extract_urls("Set your homepage to https://[your-domain]/api first") == []


def test_extract_urls_ignores_version_strings() -> None:
    assert extract_urls("Supports Python v3.13 and 2.0 releases") == []


def test_extract_urls_ignores_emoji_shortcodes() -> None:
    assert extract_urls("A cool project :rocket: :tada:") == []


def test_extract_urls_ignores_abbreviations() -> None:
    assert extract_urls("Fast, e.g. very fast, i.e. blazing") == []


def test_extract_urls_bare_unicode_domain() -> None:
    assert extract_urls("докс на ドメイン.jp") == ["ドメイン.jp"]


def test_extract_urls_unicode_tld() -> None:
    assert extract_urls("сайт пример.рф работает") == ["пример.рф"]


def test_extract_urls_ignores_cjk_punctuation() -> None:
    assert extract_urls("これはテストです。リンクなし") == []


def test_extract_urls_ignores_cyrillic_abbreviations() -> None:
    assert extract_urls("т.е. быстро") == []


def test_extract_urls_plain_prose() -> None:
    assert extract_urls("A plain description with no links at all") == []


def test_extract_urls_empty_string() -> None:
    assert extract_urls("") == []


# extract_hostname tests


def test_extract_hostname_full_url() -> None:
    assert extract_hostname("https://EXAMPLE.com/path") == "example.com"


def test_extract_hostname_schemeless() -> None:
    assert extract_hostname("cheat.sh") == "cheat.sh"


def test_extract_hostname_schemeless_with_path() -> None:
    assert extract_hostname("cheat.sh/some/path") == "cheat.sh"


def test_extract_hostname_strips_port_and_userinfo() -> None:
    assert extract_hostname("http://user:pass@host.example.org:8080/x") == (
        "host.example.org"
    )


def test_extract_hostname_unparseable() -> None:
    assert extract_hostname("") is None


def test_extract_hostname_bracket_scheme_url() -> None:
    assert extract_hostname("https://[your-domain") is None


def test_extract_hostname_bracket_full_url() -> None:
    assert extract_hostname("https://[your-domain]/api") is None


# query_family_dns tests


def make_doh_response(payload: dict) -> Mock:
    response = Mock()
    response.json.return_value = payload
    return response


def make_client(payload: dict) -> Mock:
    client = Mock()
    client.get.return_value = make_doh_response(payload)
    return client


def test_query_family_dns_flagged_by_answer() -> None:
    client = make_client(
        {
            "Status": 0,
            "Answer": [{"name": "wifiphisher.org", "type": 1, "data": "0.0.0.0"}],
            "Comment": ["EDE(17): Filtered"],
        }
    )

    assert query_family_dns(client, "wifiphisher.org") is True


def test_query_family_dns_clean_answer() -> None:
    client = make_client(
        {
            "Status": 0,
            "Answer": [{"name": "example.com", "type": 1, "data": "93.184.216.34"}],
        }
    )

    assert query_family_dns(client, "example.com") is False


def test_query_family_dns_no_answer() -> None:
    client = make_client({"Status": 3})

    assert query_family_dns(client, "nxdomain.example") is False


def test_query_family_dns_flagged_by_comment_only() -> None:
    client = make_client(
        {
            "Status": 0,
            "Answer": [{"name": "example.com", "type": 1, "data": "93.184.216.34"}],
            "Comment": ["EDE(17): Filtered"],
        }
    )

    assert query_family_dns(client, "example.com") is True


def test_query_family_dns_raises_on_servfail() -> None:
    client = make_client({"Status": 2})

    with pytest.raises(ValueError):
        query_family_dns(client, "example.com")


def test_query_family_dns_raises_on_error_status() -> None:
    client = make_client({})
    client.get.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
        "boom", request=Mock(), response=Mock()
    )

    with pytest.raises(httpx.HTTPStatusError):
        query_family_dns(client, "example.com")


def test_query_family_dns_queries_correct_endpoint() -> None:
    client = make_client({"Status": 0})

    query_family_dns(client, "example.com")

    call_args = client.get.call_args
    assert call_args[0][0] == "https://family.cloudflare-dns.com/dns-query"
    assert call_args[1]["params"] == {"name": "example.com", "type": "A"}
    assert call_args[1]["headers"] == {"Accept": "application/dns-json"}


def test_query_family_dns_punycodes_idn() -> None:
    client = make_client({"Status": 0})

    query_family_dns(client, "ドメイン.jp")

    assert client.get.call_args[1]["params"]["name"] == "xn--eckwd4c7c.jp"


def test_query_family_dns_uses_idna_2008() -> None:
    client = make_client({"Status": 0})

    query_family_dns(client, "faß.de")

    # IDNA 2003 would mangle this to fass.de — the wrong domain
    assert client.get.call_args[1]["params"]["name"] == "xn--fa-hia.de"


def test_query_family_dns_passes_unencodable_domain_raw() -> None:
    client = make_client({"Status": 0})

    query_family_dns(client, "bad..domain")

    assert client.get.call_args[1]["params"]["name"] == "bad..domain"


# get_flagged_urls tests


@pytest.fixture
def mock_client():
    with patch("starminder.content.linkcheck.httpx.Client") as mock_client_class:
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = None
        mock_client_class.return_value = client
        yield client


@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_flags_flagged_hostname(mock_query, mock_client) -> None:
    mock_query.return_value = True

    result = get_flagged_urls(["https://wifiphisher.org"])

    assert result == {"https://wifiphisher.org"}


@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_keeps_clean_hostname(mock_query, mock_client) -> None:
    mock_query.return_value = False

    result = get_flagged_urls(["https://example.com"])

    assert result == set()


@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_flags_unextractable_hostname(mock_query, mock_client) -> None:
    result = get_flagged_urls([""])

    assert result == {""}
    mock_query.assert_not_called()


@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_flags_bracket_urls(mock_query, mock_client) -> None:
    urls = ["https://[your-domain", "https://[your-domain]/api"]

    result = get_flagged_urls(urls)

    assert result == set(urls)
    mock_query.assert_not_called()


@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_flags_on_query_error(mock_query, mock_client) -> None:
    mock_query.side_effect = httpx.ConnectError("boom")

    result = get_flagged_urls(["https://example.com"])

    assert result == {"https://example.com"}


@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_deduplicates_hostnames(mock_query, mock_client) -> None:
    mock_query.return_value = True

    result = get_flagged_urls(["https://example.com/one", "https://example.com/two"])

    assert result == {"https://example.com/one", "https://example.com/two"}
    mock_query.assert_called_once()


@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_does_not_retry_errored_hostname(
    mock_query, mock_client
) -> None:
    mock_query.side_effect = httpx.ConnectError("boom")

    result = get_flagged_urls(["https://example.com/one", "https://example.com/two"])

    assert result == {"https://example.com/one", "https://example.com/two"}
    mock_query.assert_called_once()


@patch("starminder.content.linkcheck.sentry_sdk")
@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_budget_exhaustion(
    mock_query, mock_sentry, mock_client, monkeypatch
) -> None:
    monkeypatch.setattr("starminder.content.linkcheck.DOH_TIME_BUDGET", -1)

    result = get_flagged_urls(["https://example.com", "https://cheat.sh"])

    assert result == {"https://example.com", "https://cheat.sh"}
    mock_query.assert_not_called()

    mock_sentry.capture_exception.assert_called_once()
    call_args = mock_sentry.capture_exception.call_args
    error = call_args[0][0]
    assert isinstance(error, DohTimeBudgetExceededError)
    assert call_args[1]["extras"] == {
        "skipped_urls": ["https://example.com", "https://cheat.sh"]
    }


@patch("starminder.content.linkcheck.sentry_sdk")
@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_no_sentry_within_budget(
    mock_query, mock_sentry, mock_client
) -> None:
    mock_query.side_effect = [True, False, httpx.ConnectError("boom")]

    get_flagged_urls(
        ["https://wifiphisher.org", "https://example.com", "https://cheat.sh", ""]
    )

    mock_sentry.capture_exception.assert_not_called()


@patch("starminder.content.linkcheck.query_family_dns")
def test_get_flagged_urls_empty_input(mock_query, mock_client) -> None:
    result = get_flagged_urls([])

    assert result == set()
    mock_query.assert_not_called()
