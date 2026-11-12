# Hiawatha Packaging Repository

**Automated, signed Debian/Ubuntu packages for the Hiawatha web server**

Hiawatha is a lightweight web server renowned for its robust security, elegant simplicity, and minimal resource consumption.
This repository provides up-to-date, reproducible `.deb` packages built automatically from the official upstream GitLab releases.

**Maintainer:** Chris Wadge `<cwadge@tuxhelp.org>`  
GitHub: [cwadge](https://github.com/cwadge) | GitLab: [cwadge](https://gitlab.com/cwadge)

## Quick Start (Debian / Ubuntu)
```bash
# Import the signing key (apt reads the armored .asc directly; no gpg needed)
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSLo /etc/apt/keyrings/hiawatha.asc https://cwadge.github.io/hiawatha-pkg/hiawatha.asc

# Add the repository
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/hiawatha.asc] \
  https://cwadge.github.io/hiawatha-pkg/repo $VERSION_CODENAME main" \
  | sudo tee /etc/apt/sources.list.d/hiawatha.list

# Install
sudo apt update && sudo apt install hiawatha
```

The service is enabled and started automatically on installation.

## Supported Platforms

| Distribution       | Codename | Architecture |
|--------------------|----------|--------------|
| Debian 13 (Stable) | trixie   | amd64, arm64 |
| Debian 12          | bookworm | amd64, arm64 |
| Ubuntu 26.04 LTS   | resolute | amd64, arm64 |
| Ubuntu 24.04 LTS   | noble    | amd64, arm64 |
| Ubuntu 22.04 LTS   | jammy    | amd64, arm64 |

## Security & Trust

- Every package is built in a clean Docker environment from official upstream [GitLab tags](https://gitlab.com/hsleisink/hiawatha/-/tags).
- Every package is install-tested in a pristine container of its target distro (config validated, default site served) before it is signed and published.
- After publishing, the repository's signatures, index hashes, versions and pool files are verified end to end before a release is tagged.
- Packages are signed with a dedicated [GPG key](https://cwadge.github.io/hiawatha-pkg/hiawatha.asc).
- The entire build pipeline is open source and runs publicly on [GitHub Actions](https://github.com/cwadge/hiawatha-pkg/actions).
- Source for this packaging repo: [github.com/cwadge/hiawatha-pkg](https://github.com/cwadge/hiawatha-pkg)

## Reporting Issues

- **Package-specific issues, repository problems, etc.** → [GitHub Issues](https://github.com/cwadge/hiawatha-pkg/issues)
- **Hiawatha issues** *(bugs, feature requests, etc.)* → [Hiawatha GitLab](https://gitlab.com/hsleisink/hiawatha)
- Questions? Feel free to open an issue or reach out via email.

## License
- The pipeline and repo code is licensed under the [MIT License](https://opensource.org/license/MIT).
- Hiawatha Webserver is licensed under the [GNU GPL v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).

## How the pipeline works

A daily run (plus any push touching `debian/` or `.github/targets.json`) compares the latest upstream tag against what the published APT indexes actually contain, and builds only the codename/arch pairs that are missing. That one rule covers new upstream releases, packaging revisions, newly added distros and retries of failed legs. A distro that fails to build doesn't block the others; the release is only tagged once every target is published and verified.

- **Shipping a packaging fix:** add a `debian/changelog` entry for the current upstream version with the next revision (e.g. `12.4-2`) and push. Without the revision bump, the push run warns that nothing will ship.
- **Adding a distro:** add one entry to `.github/targets.json` and push.
- **Retiring a distro:** remove its entry. reprepro may then insist on a one-time `reprepro -b repo clearvanished` on the gh-pages branch; if so, the post-publish verification fails loudly rather than silently.

## Contributing

This repo is intentionally minimal so it stays easy to maintain. PRs for the CI/CD pipeline are welcome.

The workflow is also designed to be **easily forkable** for internal use. If you want to run a private package repository for a different project, whether for internal corporate tooling or another upstream, the only things you need to change are the five-line configuration block at the top of `.github/workflows/distribution.yml`, the target list in `.github/targets.json`, and your own keypair. Everything else (Pages URL, repo links, artifact paths) derives from GitHub context automatically.

---

*Enjoy using Hiawatha!*
