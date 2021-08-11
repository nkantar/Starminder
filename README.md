# Starminder


## Environment variables

The following environment variables are required for Starminder to work:

| Environment variable | Description | Example |
|:-------------------- |:----------- |:------- |
| `STARMINDER_COUNT` | number of reminders per email as an integer | `3` |
| `STARMINDER_RECIPIENT` | recipient (your) email | `nik+starminder_script@nkantar.com` |
| `GH_TOKEN` | [GitHub Personal Token], no specificpermissions required | `aofh398rwa9ahg99h` |
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID, for SES | `dskfh3928hwa3ei7hf` |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key, for SES | `3r3987lr9j8lu/98rw3lj9r3/98awr3l3rh` |
| `AWS_FROM` | sender address as configured in SES | `"Starminder <notifications@starminder.xyz>"` |


[GitHub Personal Token]: https://github.com/settings/tokens "Sign in to GitHub · GitHub"
