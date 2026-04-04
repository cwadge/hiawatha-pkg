# Hiawatha Packaging Repository

**Automated, signed Debian/Ubuntu packages for the Hiawatha web server**

Hiawatha is a secure, lightweight web server with a focus on security,
simplicity, and low resource usage. This repository provides up-to-date,
reproducible `.deb` packages built automatically from upstream GitLab releases.

- Debian Stable, Debian Old Stable, Ubuntu LTS (22.04, 24.04)
- Fully signed with maintainer GPG key
- Transparent CI/CD on GitHub Actions

**Maintainer:** Chris Wadge `<cwadge@tuxhelp.org>`  
GitHub: [cwadge](https://github.com/cwadge) | GitLab: [cwadge](https://gitlab.com/cwadge)

## Quick Start (Debian / Ubuntu)
```bash
# Import the signing key
curl -fsSL https://cwadge.github.io/hiawatha-pkg/hiawatha.asc \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/hiawatha.gpg > /dev/null

# Add the repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hiawatha.gpg] \
  https://cwadge.github.io/hiawatha-pkg/repo $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hiawatha.list

# Install
sudo apt update && sudo apt install hiawatha
```

The service is enabled and started automatically on installation.

**Supported codenames:** `trixie` · `bookworm` · `noble` · `jammy`

## Supported Platforms

| Distribution       | Codename | Architecture |
|--------------------|----------|--------------|
| Debian 13 (Stable) | trixie   | amd64, arm64 |
| Debian 12          | bookworm | amd64, arm64 |
| Ubuntu 24.04 LTS   | noble    | amd64, arm64 |
| Ubuntu 22.04 LTS   | jammy    | amd64, arm64 |

## Security & Trust

- Every package is built in a clean Docker environment from official upstream GitLab tags.
- Packages are signed with a dedicated [GPG key](https://cwadge.github.io/hiawatha-pkg/hiawatha.asc).
- The entire build pipeline is open source and runs publicly on GitHub Actions.
- Source for this packaging repo: [github.com/cwadge/hiawatha-pkg](https://github.com/cwadge/hiawatha-pkg)

## Reporting Issues

- **Package-specific issues, installation problems, etc.** → [GitHub Issues](https://github.com/cwadge/hiawatha-pkg/issues)
- **Hiawatha itself** *(bugs, feature requests, etc.)* → [Hiawatha GitLab](https://gitlab.com/hsleisink/hiawatha)
- Questions? Feel free to open an issue or reach out via email.

## License
The CI/CD and repo code is licensed under the [MIT License](https://opensource.org/license/MIT). Hiawatha Webserver is licensed under the [GNU GPL v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).

## Contributing

This repo is intentionally minimal so it stays easy to maintain. PRs for the CI/CD pipeline are welcome.

The workflow is also designed to be **easily forkable** for internal use. If you want to run a private package repository for a different project, whether for internal corporate tooling or another upstream, the only values you need to change are a five-line configuration block at the top of `.github/workflows/distribution.yml`. Everything else (Pages URL, repo links, artifact paths) derives from GitHub context automatically.

---

*Enjoy using Hiawatha!*
