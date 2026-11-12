#!/usr/bin/env python3
"""Decide what this run needs to build, based on what is actually published.

Usage: plan.py <upstream_tag> <gh-pages git ref | "">

The published APT indexes on gh-pages are the source of truth: for every
(codename, arch) in .github/targets.json, if repo/dists/<codename>/main/
binary-<arch>/Packages does not already list the exact expected version, that
pair is (re)built. This makes the pipeline self-healing and removes the need
for a manual "force rebuild":

  * new upstream release        -> every pair is missing -> full build
  * debian/changelog rev bump   -> new version string    -> full build
  * new codename in targets     -> only that codename's pairs are built
  * a leg failed last run       -> only the missing pairs are retried

Writes GitHub step outputs (key=value lines) to stdout.
"""

import json
import re
import subprocess
import sys

TARGETS_FILE = ".github/targets.json"
CHANGELOG = "debian/changelog"


def effective_version(tag, changelog_path=CHANGELOG):
    """Return (deb_rev, version) for this upstream tag.

    If the top changelog entry is already for this upstream version, keep its
    Debian revision (packaging-only bumps like 12.4-1 -> 12.4-2 ship
    automatically). Otherwise this is the first packaging of a new upstream
    release, which is -1 by convention.
    """
    with open(changelog_path, encoding="utf-8") as fh:
        first = fh.readline()
    m = re.match(r"^\S+ \(([^)]+)\)", first)
    if not m:
        sys.exit(f"ERROR: cannot parse version from {changelog_path}: {first!r}")
    cl_ver = m.group(1)
    upstream, _, rev = cl_ver.rpartition("-")
    if upstream == tag and rev.isdigit():
        deb_rev = rev
    else:
        deb_rev = "1"
    return deb_rev, f"{tag}-{deb_rev}"


def published_versions(ref, codename, arch):
    """Return the set of hiawatha versions listed in a published Packages index."""
    if not ref:
        return set()
    path = f"repo/dists/{codename}/main/binary-{arch}/Packages"
    res = subprocess.run(["git", "show", f"{ref}:{path}"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        return set()
    versions, pkg = set(), None
    for line in res.stdout.splitlines():
        if line.startswith("Package: "):
            pkg = line.split(":", 1)[1].strip()
        elif line.startswith("Version: ") and pkg == "hiawatha":
            versions.add(line.split(":", 1)[1].strip())
    return versions


def main():
    if len(sys.argv) != 3:
        sys.exit(f"Usage: {sys.argv[0]} <upstream_tag> <gh-pages ref or ''>")
    tag, ref = sys.argv[1], sys.argv[2]

    with open(TARGETS_FILE, encoding="utf-8") as fh:
        cfg = json.load(fh)

    deb_rev, version = effective_version(tag)

    include, publish = [], []
    for t in cfg["targets"]:
        for arch in cfg["arches"]:
            full = f"{version}{t['suffix']}"
            have = published_versions(ref, t["codename"], arch)
            state = "published" if full in have else "MISSING"
            print(f"  {t['codename']:<10} {arch:<6} {full:<24} {state}",
                  file=sys.stderr)
            if full not in have:
                include.append({
                    "codename": t["codename"],
                    "image": t["image"],
                    "suffix": t["suffix"],
                    "arch": arch,
                })
                if t["codename"] not in publish:
                    publish.append(t["codename"])

    print(f"tag={tag}")
    print(f"deb_rev={deb_rev}")
    print(f"version={version}")
    print(f"build_needed={'true' if include else 'false'}")
    print(f"build_matrix={json.dumps({'include': include}, separators=(',', ':'))}")
    print(f"publish_codenames={json.dumps(publish, separators=(',', ':'))}")


if __name__ == "__main__":
    main()
