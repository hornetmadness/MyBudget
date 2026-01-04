# Release Process

This project uses automated versioning and release management with GitHub Actions.

## Overview

The release process is automated using three key workflows:

1. **test.yml** - Runs tests on every push and PR
2. **build.yml** - Builds and pushes Docker images to GHCR
3. **release.yml** - Automated release creation and versioning

## Versioning Strategy

This project follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

Version updates are determined by commit messages using conventional commits:

- `feat:` prefix → MINOR version bump
- `fix:` or `perf:` prefix → PATCH version bump
- `BREAKING CHANGE:` in footer → MAJOR version bump

## Commit Message Format

Use the following commit message format for proper versioning:

```
type(scope): subject

body

footer
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `perf` - Performance improvement
- `refactor` - Code refactoring without feature change
- `docs` - Documentation changes
- `chore` - Build scripts, dependencies, etc.

**Examples:**

```
feat(budgets): add overlap validation

Implement budget period overlap checking to prevent conflicting budgets.

Closes #123
```

```
fix(transactions): correct timezone handling

BREAKING CHANGE: removed naive datetime support
```

## Automated Release Workflow

### What Happens on Main Branch

When commits are pushed to `main`:

1. **Tests Run** - All tests must pass
2. **Release Please Analyzes** - Commits are checked against conventional commit format
3. **PR Created** - If commits warrant a version bump, a release PR is created
   - Updates `APP_VERSION` in `app/config.py`
   - Updates `CHANGELOG.md`
   - Provides release notes
4. **Manual Merge** - You review and merge the release PR
5. **Release Created** - GitHub release is automatically created with:
   - Semantic version tag (e.g., `v1.2.3`)
   - Release notes from CHANGELOG
   - Docker image pushed to GHCR with version tag

### Typical Release Flow

```
1. Work on feature branch
2. Create PR with conventional commits
3. Merge to main after review
4. Release Please creates release PR
5. Review and merge release PR
6. GitHub release created automatically
7. Docker image built and pushed with version tag
```

## Docker Image Tags

When a release is created, the Docker image is tagged with:

- `ghcr.io/username/mybudget:v1.2.3` (version tag)
- `ghcr.io/username/mybudget:1.2.3` (version without 'v')
- `ghcr.io/username/mybudget:main` (main branch)
- `ghcr.io/username/mybudget:main-abc123def` (main with commit SHA)

## CHANGELOG Maintenance

The `CHANGELOG.md` is automatically updated when releases are created. Changes are organized by type:

- **Features** - New functionality
- **Bug Fixes** - Bug fixes
- **Performance Improvements** - Performance enhancements
- **Code Refactoring** - Refactoring changes
- **Documentation** - Documentation updates

Miscellaneous changes (chore) are hidden by default.

## Manual Version Control

If needed, you can manually create a release:

1. Update `APP_VERSION` in `app/config.py`
2. Update `CHANGELOG.md` with release notes
3. Commit with message: `chore: release v1.2.3`
4. Create git tag: `git tag v1.2.3`
5. Push: `git push origin main --tags`

## Skipping Release Check

If you need to commit without triggering a release check, use `[skip ci]` in the commit message:

```
chore: minor cleanup [skip ci]
```

## Configuration Files

- **release-config.json** - Release Please configuration
- **.release-please-manifest.json** - Current version tracking
- **pyproject.toml** - Python project metadata
- **.github/workflows/release.yml** - Release automation workflow

## Troubleshooting

### Release PR not created

- Ensure commits use conventional commit format
- Check that the main branch exists
- Verify GitHub token permissions are correct

### Version not updating in config.py

- Release Please needs the exact format: `APP_VERSION: str = "{version}"`
- Check `release-config.json` has correct `version-file` and `version-pattern`

### Docker image not pushed

- Release PR must be merged before image builds
- Check that `main` branch builds are enabled in GitHub Actions
- Verify GHCR access is configured correctly
