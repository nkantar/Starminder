# Contributing to Starminder

Thanks for your interest in _**Starminder**_!


## Project Status

_**Starminder**_ is currently in early development. While I’m not actively soliciting contributions at this stage, I’m open to thoughtful proposals and improvements. Please understand that:
- The architecture and design patterns may shift as the project evolves
- Response times on issues and pull requests may vary
- Some contributions might not align with the current direction and may be declined

If you’re thinking about making a code contribution, please open an issue first to discuss your ideas before investing substantial time.


## Ways to Contribute


### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment details (OS, Python version, etc.)


### Suggesting Enhancements

Feature requests are welcome! Please open an issue describing:
- The problem you’re trying to solve
- Your proposed solution
- Any alternative approaches you’ve considered


### Code Contributions

If you’d like to contribute code:

1. **Fork and clone** the repository
2. **Create a branch** for your changes ([very important!](https://davidism.com/github-pull-request-pitfalls/#use-a-new-branch-not-main "GitHub Pull Request Pitfalls | David Lord"))
3. **Make your changes** following the code quality standards below
4. **Test thoroughly** and ensure all checks pass
5. **Submit a pull request** with a clear description of your changes


## Code Quality Standards

All code contributions must pass the following checks:

```bash
just formatcheck # Check code formatting
just lint        # Check for linting issues
just typecheck   # Type checking
just test        # Run tests
just djangocheck # Django system checks
```

You can auto-fix many linting issues with:
```bash
just lintfix
```


## Development Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run migrations:
   ```bash
   just migrate
   ```

3. Set up job schedules:
   ```bash
   just schedulejobs
   ```

4. Run the development server:
   ```bash
   just devserve
   ```

5. Run the worker:
   ```bash
   just worker
   ```


## Architecture Guidelines

- The project comprises three Django apps:
  - `core`: reusable and foundational models and views
  - `implementations`: provider-specific details
  - `content`: generated data
- Most models should subclass `core.models.TimestampedModel`


## Questions?

Feel free to open an issue for any questions about contributing. I appreciate your understanding of the project’s early-stage nature.
