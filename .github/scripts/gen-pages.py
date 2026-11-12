#!/usr/bin/env python3
"""Generate GitHub Pages index files for the Hiawatha packaging repository.

Called by the finalize job in distribution.yml. Writes index.html and
repo/index.html into <out_dir> (the gh-pages worktree). Distro rows and
download links come from .github/targets.json.

Usage: gen-pages.py <pages_url> <key_file> <tag> <version> <out_dir>
"""

import html
import json
import os
import sys

TARGETS_FILE = ".github/targets.json"


def main():
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} <pages_url> <key_file> <tag> <version> <out_dir>",
              file=sys.stderr)
        sys.exit(1)

    pages_url, key_file, tag, version, out_dir = sys.argv[1:]

    with open(TARGETS_FILE, encoding="utf-8") as fh:
        cfg = json.load(fh)
    arches = cfg["arches"]
    pool_base = f"{pages_url}/repo/pool/main/h/hiawatha"
    github_repo   = os.environ.get("GITHUB_REPOSITORY", "")
    upstream_path = os.environ.get("UPSTREAM_GITLAB_PATH", "hsleisink/hiawatha")

    def dl(t, arch):
        href = f"{pool_base}/hiawatha_{version}{t['suffix']}_{arch}.deb"
        return f'<a class="dl" href="{html.escape(href)}">{arch}</a>'

    rows = "\n".join(
        f"""          <tr>
            <td>{html.escape(t['label'])}</td><td><code>{t['codename']}</code></td>
            <td>{' '.join(dl(t, a) for a in arches)}</td>
          </tr>"""
        for t in cfg["targets"]
    )
    arch_badge = " &middot; ".join(arches)

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hiawatha Packages</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#f4f5f7;color:#1a1d23;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;line-height:1.6}}
    @media(prefers-color-scheme:dark){{body{{background:#0f1117;color:#e2e8f0}}}}
    header{{background:#fff;border-bottom:1px solid #e2e4e9;padding:1.5rem 2rem}}
    @media(prefers-color-scheme:dark){{header{{background:#1a1d23;border-color:#2a2d35}}}}
    h1{{font-size:1.4rem;font-weight:600}}
    .sub{{color:#6b7280;font-size:.88rem;margin-top:.25rem}}
    .badge{{display:inline-block;background:#ecfeff;color:#0e7490;border-radius:4px;font-size:.75rem;font-weight:600;padding:1px 8px;margin-right:3px}}
    @media(prefers-color-scheme:dark){{.badge{{background:#164e63;color:#67e8f9}}}}
    .wrap{{max-width:820px;margin:0 auto;padding:1.25rem 2rem}}
    h2{{font-size:.95rem;font-weight:600;margin:1.5rem 0 .6rem;text-transform:uppercase;letter-spacing:.04em;color:#6b7280}}
    .card{{background:#fff;border:1px solid #e2e4e9;border-radius:10px;padding:1.25rem;margin-bottom:1rem}}
    @media(prefers-color-scheme:dark){{.card{{background:#1a1d23;border-color:#2a2d35}}}}
    pre{{background:#1e2130;color:#e2e8f0;border-radius:6px;padding:1rem 1.1rem;overflow-x:auto;font-size:.82rem;font-family:'SF Mono','Fira Code',monospace;line-height:1.6;margin-top:.75rem}}
    .note{{color:#6b7280;font-size:.88rem;margin-top:.6rem}}
    table{{width:100%;border-collapse:collapse;font-size:.88rem}}
    th{{text-align:left;padding:6px 10px;background:#f4f5f7;border:1px solid #e2e4e9;color:#6b7280;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em}}
    @media(prefers-color-scheme:dark){{th{{background:#0f1117;border-color:#2a2d35}}}}
    td{{padding:8px 10px;border:1px solid #e2e4e9}}
    @media(prefers-color-scheme:dark){{td{{border-color:#2a2d35}}}}
    code{{background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:.85em;font-family:'SF Mono','Fira Code',monospace}}
    @media(prefers-color-scheme:dark){{code{{background:#2a2d35}}}}
    .dl{{display:inline-block;background:#2563eb;color:#fff;border-radius:4px;padding:2px 12px;font-size:.8rem;font-weight:500;margin:2px;text-decoration:none}}
    .dl:hover{{background:#1d4ed8}}
    ul{{padding-left:1.2rem;color:#6b7280;font-size:.9rem;line-height:1.9}}
    footer{{border-top:1px solid #e2e4e9;padding:1rem 2rem;color:#6b7280;font-size:.82rem;margin-top:.25rem}}
    @media(prefers-color-scheme:dark){{footer{{border-color:#2a2d35}}}}
    footer a{{color:#6b7280}}
    .sep{{margin:0 8px;opacity:.4}}
  </style>
</head>
<body>
  <header>
    <h1>Hiawatha Packages</h1>
    <p class="sub">Automated signed .deb packages, built daily from upstream GitLab releases.
      &nbsp;<span class="badge">v{tag}</span><span class="badge">{arch_badge}</span></p>
  </header>
  <div class="wrap">
    <h2>Quick start</h2>
    <div class="card">
<pre># Import the signing key (apt reads the armored .asc directly; no gpg needed)
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSLo /etc/apt/keyrings/hiawatha.asc {pages_url}/{key_file}

# Add the repository
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/hiawatha.asc] \\
  {pages_url}/repo $VERSION_CODENAME main" \\
  | sudo tee /etc/apt/sources.list.d/hiawatha.list

# Install
sudo apt update &amp;&amp; sudo apt install hiawatha</pre>
      <p class="note">The service is enabled and started automatically on installation.</p>
    </div>
    <h2>Direct downloads &nbsp;<span style="text-transform:none;letter-spacing:0;font-weight:400">v{version}</span></h2>
    <div class="card">
      <p class="note" style="margin-bottom:.75rem">For one-off installation without configuring the repository.
        After downloading: <code>sudo dpkg -i hiawatha_*.deb &amp;&amp; sudo apt-get install -f</code></p>
      <table>
        <thead><tr><th>Distribution</th><th>Codename</th><th>Downloads</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <h2>Security &amp; trust</h2>
    <div class="card">
      <ul>
        <li>Packages built in clean Docker containers from official upstream GitLab tags.</li>
        <li>Signed with a dedicated GPG public key:
          <a href="{key_file}" style="color:#2563eb">{key_file}</a></li>
        <li>Build pipeline is fully open source and runs publicly on GitHub Actions.</li>
      </ul>
    </div>
  </div>
  <footer>
    Maintained by <a href="https://github.com/{github_repo.split('/')[0] if '/' in github_repo else github_repo}">{"cwadge" if not github_repo else github_repo.split("/")[0]}</a><span class="sep">&middot;</span>
    <a href="https://github.com/{github_repo}">Packaging source</a><span class="sep">&middot;</span>
    <a href="https://gitlab.com/{upstream_path}">Hiawatha upstream</a><span class="sep">&middot;</span>
    <a href="https://github.com/{github_repo}/issues">Report an issue</a>
  </footer>
</body>
</html>
"""

    repo_index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hiawatha APT Repository</title>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
         max-width:600px;margin:5rem auto;padding:0 1.5rem;
         color:#1a1d23;line-height:1.6}
    @media(prefers-color-scheme:dark){body{color:#e2e8f0;background:#0f1117}}
    code{background:#f1f5f9;padding:2px 6px;border-radius:3px;font-size:.88em}
    @media(prefers-color-scheme:dark){code{background:#1e2130}}
    a{color:#2563eb}
  </style>
</head>
<body>
  <h1 style="font-size:1.4rem;font-weight:600;margin-bottom:.75rem">APT Repository</h1>
  <p>This is a machine-readable APT package repository, not a regular website.
     Add it to your system using the instructions on the
     <a href="../">Hiawatha packaging homepage</a>, then run
     <code>apt update &amp;&amp; apt install hiawatha</code>.</p>
  <p style="margin-top:1rem;color:#6b7280;font-size:.9rem">
    Browsing directly? This URL serves package metadata consumed by apt,
    not human-readable content.
  </p>
</body>
</html>
"""

    os.makedirs(os.path.join(out_dir, "repo"), exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    with open(os.path.join(out_dir, "repo", "index.html"), "w", encoding="utf-8") as f:
        f.write(repo_index_html)

    print(f"Generated index.html and repo/index.html for v{version}")


if __name__ == "__main__":
    main()
