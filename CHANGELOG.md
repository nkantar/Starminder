# Starminder Changelog


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


[Unreleased]: https://github.com/nkantar/Starminder/compare/1.0.8...HEAD
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
