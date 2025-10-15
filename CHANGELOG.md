# Starminder Changelog


<!--
Added for new features.
Changed for changes in existing functionality.
Deprecated for soon-to-be removed features.
Removed for now removed features.
Fixed for any bug fixes.
Security in case of vulnerabilities.
-->


## [Unreleased]


## [25.10.14] - 2025-10-14

### Changed
- Made URL fields longer
- Made star description TextField


## [25.10.13.1] - 2025-10-13

### Changed
- Refactored content generation to run via many smaller tasks and thus avoid choking for users with many stars
- Worker timeouts
- Web server settings to hopefully improve performance on the relatively low powered server

### Fixed
- Added line breaks in address in HTML email template


## [25.10.13] - 2025-10-13

### Added
- `generate_content` Django mangement command

### Changed
- worker configuration:
    - longer timeout (+ retry offset)
    - more workers (1x VCPU count)


## [25.10.12] - 2025-10-12

### Added
- email reminder support
- FAQ, fake testimonials, and a homepage blurb
- full account deletion (including GitHub app token)
- repo metadata (CoC, Contrib Guide, etc.) files

### Changed
- hourly job is now scheduled through code + DB data, not externally
- VPS specs + Granian config for more _juice!_


## [25.10.11] - 2025-10-11

### Added
- v4 soft launch edition:
    - only Atom feed support
    - lots of small TODO items remaining


## [3.0.0] - 2025-10-08

### Added
- Some files for what ended up being a false start

### Removed
- Nearly everything, in preparation for v3.
- Everything again, in preparation for v4 (to be CalVer for first release).


## [2.0.0] - 2025-01-28

### Added
- New script based version

### Removed
- Delete _all_ the files in prep for v2!


## [1.0.8] - 2019-10-15

### Changed
- Mailing address in the email templates


## [1.0.7] - 2018-01-31

### Added
- Unsubscribe info and mailing address to the email templates

### Changed
- Python runtime from 3.6.2 to 3.6.4


## [1.0.6] - 2017-08-21

### Added
- Placeholders for number and email on the main form


## [1.0.5] - 2017-08-14

### Changed
- Italicized testimonial authors.


## [1.0.4] - 2017-08-14

### Added
- Release dates to the changelog
- Fourth fake testimonial

### Removed
- First release link from the changelog because it's silly


## [1.0.3] - 2017-08-01

### Fixed
- Sentry client in the notifier script was misused, causing an error, which should no longer happen.


## [1.0.2] - 2017-08-01

### Changed
- Fixed bad release linking in the changelog.
- Fixed improper heading level for a section in the changelog.


## [1.0.1] - 2017-07-31

### Changed
- Switched from `ConfigParser` to `SafeConfigParser`.


## [1.0.0] - 2017-07-31

### Added
- Error tracking (for both the web app and notifier job) via Sentry
- Constants are now tracked in `defaults.ini`.

### Fixed
- Dead session 500s (user logs in, server gets restartet, uses saves/deletes)


## [0.3.0] - 2017-07-27

### Updated
- Better `User.__repr__` (`<User: nkantar [nik@nkantar.com]>` instead of `<User nkantar>`)
- User count in the footer is pluralized only when `!= 1`.
- Email field on the form is now blank instead of showing "None" when there's nothing in the DB.


## [0.2.0] - 2017-07-27

### Added
- Version output
- `LICENSE`
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `ISSUE_TEMPLATE.md`
- `PULL_REQUEST_TEMPLATE.md`

### Updated
- `README.rst`


## 0.1.0 - 2017-07-26

### Added
- First version suitable for public consumption.


[Unreleased]: https://github.com/nkantar/Starminder/compare/25.10.14...HEAD
[25.10.14]: https://github.com/nkantar/Starminder/compare/25.10.13.1...25.10.14
[25.10.13.1]: https://github.com/nkantar/Starminder/compare/25.10.13...25.10.13.1
[25.10.13]: https://github.com/nkantar/Starminder/compare/25.10.12...25.10.13
[25.10.12]: https://github.com/nkantar/Starminder/compare/25.10.11...25.10.12
[25.10.11]: https://github.com/nkantar/Starminder/compare/3.0.0...25.10.11
[3.0.0]: https://github.com/nkantar/Starminder/compare/2.0.0...3.0.0
[2.0.0]: https://github.com/nkantar/Starminder/compare/1.0.8...2.0.0
[1.0.8]: https://github.com/nkantar/Starminder/compare/1.0.7...1.0.8
[1.0.7]: https://github.com/nkantar/Starminder/compare/1.0.6...1.0.7
[1.0.6]: https://github.com/nkantar/Starminder/compare/1.0.5...1.0.6
[1.0.5]: https://github.com/nkantar/Starminder/compare/1.0.4...1.0.5
[1.0.4]: https://github.com/nkantar/Starminder/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/nkantar/Starminder/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/nkantar/Starminder/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/nkantar/Starminder/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/nkantar/Starminder/compare/0.3.0...1.0.0
[0.3.0]: https://github.com/nkantar/Starminder/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/nkantar/Starminder/compare/0.1.0...0.2.0
