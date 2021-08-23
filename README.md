# Starminder

_**Starminder**_ is a GitHub starred project reminder. ⭐

If you have any number of starred projects, you probably have very little idea what's in there.
_Starminder_ aims to periodically remind you of some random ones, so you don't forget about them entirely.

It functions as a script run via GitHub Actions.
You fork the repo, update the cron schedule, set the requisite environment variables, and off it goes! 🚀


## Installation

### Amazon SES Email Sending

If you're using the built-in Amazon SES implementation, follow these steps:

1. Generate personal GitHub token
2. Configure a domain and access keys in AWS
3. Fork the project
4. Set the following secrets in your fork's settings:
    - `STARMINDER_COUNT`: number of reminders per email as an integer, e.g., `3`
    - `STARMINDER_RECIPIENT`: recipient (your) email, e.g., `nik+starminder_script@nkantar.com`
    - `GH_TOKEN`: [GitHub Personal Token], no specific permissions required, e.g., `aofh398rwa9ahg99h`
    - `AWS_ACCESS_KEY_ID`: AWS Access Key ID, for SES, e.g., `dskfh3928hwa3ei7hf`
    - `AWS_SECRET_ACCESS_KEY`: AWS Secret Access Key, for SES, e.g., `3r3987lr9j8lu/98rw3lj9r3/98awr3l3rh`
    - `AWS_FROM`: sender address as configured in SES, e.g., `"Starminder <notifications@starminder.xyz>"`
5. Edit the schedule in `.github/workflows/run_starminder.yml` as desired
6. Occasionally refresh your fork from upstream, possibly using the GitHub UI
7. Enjoy! 🎉

### Custom Email Sending

If you want to send emails via a service other than Amazon SES, these are the steps:

1. Generate personal GitHub token
2. Set up your preferred email service
3. Fork the project
4. Write a custom `send_email` implementation (see [Custom Email Sending Implementation] below)
5. Set the following secrets in your fork's settings:
    - `STARMINDER_COUNT`: number of reminders per email as an integer, e.g., `3`
    - `STARMINDER_RECIPIENT`: recipient (your) email, e.g., `nik+starminder_script@nkantar.com`
    - `GH_TOKEN`: [GitHub Personal Token], no specific permissions required, e.g., `aofh398rwa9ahg99h`
6. Edit the schedule in `.github/workflows/run_starminder.yml` as desired
7. Add whichever secrets your implementation requires
8. Occasionally refresh your fork from upstream, possibly using the GitHub UI
9. Enjoy! 🎉


## Uninstallation

1. Delete your fork
2. Decommission your Amazon SES or other email service setup as appropriate
3. Enjoy! 🎉


## Custom Email Sending Implementation

_Starminder_ supports Amazon SES out of the box.
If you'd like to use a different email service, you're responsible for the implementation, but that's an explicitly supported feature.

Broad steps:

1. Create a file called `custom.py`
2. In said file create a function called `send_email`
3. Ensure said function accepts the following string arguments, in this order:
    1. `text`: text email body
    2. `html`: HTML email body
    3. `subject`: email subject
    4. `recipient`: email recipient
4. If your custom implementation requires additional dependencies, create a file called `custom_requirements.txt`
5. If applicable, in said file define your dependencies as expected by `pip install -r`


## FAQ

_Frequently Asked Questions_…or _Frankly, Anticipated Questionscommentsorconcerns_…

- _What happened to the web app?_ I got tired of feeling guilty about not maintaining it.
- _Are you concerned this will turn off potential users?_ I'm not concerned about it, but I absolutely expect it to be the case.
- _This is anoying._ `¯\_(ツ)_/¯`


## Contributing

Unlike most of my projects, contributions are not explicitly encouraged, though they're not discouraged, either.


## License

[MIT](https://choosealicense.com/licenses/mit/)


[Custom Email Sending Implementation]: #custom-email-sending-implementation "Custom Email Sending Implementation"
