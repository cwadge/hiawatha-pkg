#!/usr/bin/env python3
"""End-to-end check of the published APT repo, as apt would see it.

Usage: verify-repo.py <repo_dir> <armored_public_key> <version>

For every (codename, arch) in .github/targets.json:
  1. InRelease carries a valid signature from our key (via gpgv).
  2. The signed SHA256 list matches the Packages / Packages.gz on disk.
  3. Packages lists hiawatha at exactly <version><suffix>.
  4. The pool file it points at exists and matches the indexed SHA256/Size.

Why this exists: apt-repo-action runs reprepro via os.system() and ignores its
exit codes, then commits and pushes regardless, recording the version in its
"loop detection" metadata. A failed include/export would therefore show a green
run AND be skipped on every retry. This turns that into a loud failure before
the release is tagged.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile

TARGETS_FILE = ".github/targets.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def signed_release(inrelease, keyring):
    """Verify InRelease and return only the signed plaintext."""
    if not os.path.isfile(inrelease):
        raise ValueError("InRelease missing (codename never exported?)")
    res = subprocess.run(
        ["gpgv", "--keyring", keyring, "--output", "-", inrelease],
        capture_output=True,
    )
    if res.returncode != 0:
        raise ValueError("bad signature: " + res.stderr.decode(errors="replace").strip())
    return res.stdout.decode()


def sha256_section(release_text):
    out, active = {}, False
    for line in release_text.splitlines():
        if not line.startswith(" "):
            active = line.startswith("SHA256:")
            continue
        if active:
            digest, size, name = line.split()
            out[name] = (digest, int(size))
    return out


def hiawatha_stanza(packages_text):
    for stanza in packages_text.split("\n\n"):
        fields = {}
        for line in stanza.splitlines():
            if line and not line.startswith(" ") and ":" in line:
                k, v = line.split(":", 1)
                fields[k] = v.strip()
        if fields.get("Package") == "hiawatha":
            return fields
    return None


def check(repo, keyring, codename, arch, expected):
    dist = os.path.join(repo, "dists", codename)
    rel = signed_release(os.path.join(dist, "InRelease"), keyring)
    sums = sha256_section(rel)

    for name in (f"main/binary-{arch}/Packages", f"main/binary-{arch}/Packages.gz"):
        if name not in sums:
            raise ValueError(f"{name} not listed in signed InRelease")
        path = os.path.join(dist, name)
        digest, size = sums[name]
        if os.path.getsize(path) != size or sha256(path) != digest:
            raise ValueError(f"{name} does not match signed InRelease (stale export?)")

    with open(os.path.join(dist, "main", f"binary-{arch}", "Packages"), encoding="utf-8") as fh:
        pkg = hiawatha_stanza(fh.read())
    if pkg is None:
        raise ValueError("hiawatha not present in Packages")
    if pkg.get("Version") != expected:
        raise ValueError(f"Packages has {pkg.get('Version')}, expected {expected}")

    deb = os.path.join(repo, pkg["Filename"])
    if not os.path.isfile(deb):
        raise ValueError(f"pool file missing: {pkg['Filename']}")
    if os.path.getsize(deb) != int(pkg["Size"]) or sha256(deb) != pkg["SHA256"]:
        raise ValueError(f"pool file does not match index: {pkg['Filename']}")


def main():
    if len(sys.argv) != 4:
        sys.exit(f"Usage: {sys.argv[0]} <repo_dir> <armored_public_key> <version>")
    repo, key, version = sys.argv[1:]

    with open(TARGETS_FILE, encoding="utf-8") as fh:
        cfg = json.load(fh)

    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        keyring = os.path.join(tmp, "key.gpg")
        subprocess.run(["gpg", "--batch", "--yes", "--dearmor", "-o", keyring, key],
                       check=True)
        for t in cfg["targets"]:
            for arch in cfg["arches"]:
                expected = f"{version}{t['suffix']}"
                label = f"{t['codename']}/{arch}"
                try:
                    check(repo, keyring, t["codename"], arch, expected)
                    print(f"  OK    {label:<16} {expected}")
                except (OSError, ValueError, KeyError) as exc:
                    failures += 1
                    print(f"::error title=APT repo verification::{label}: {exc}")

    if failures:
        sys.exit(f"{failures} repo check(s) failed")
    print("All published indexes verified.")


if __name__ == "__main__":
    main()
