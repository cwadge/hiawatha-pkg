import os
import re
import gzip
import glob
import subprocess

# gh-pages worktree root (created by the finalize job via `git worktree add`).
REPO_DIR = "gh-pages-branch"

# apt-repo-action publishes under its repo_folder input, which defaults to
# "repo", relative to the gh-pages root. So the reprepro pool lives at
# repo/pool/main/h/hiawatha — NOT pool/... at the branch root. Omitting the
# "repo/" prefix makes the pool dir look missing on every run, which silently
# turns this whole janitor into a no-op and lets the pool grow unbounded.
POOL_DIR = os.path.join(REPO_DIR, "repo", "pool", "main", "h", "hiawatha")
DISTS_DIR = os.path.join(REPO_DIR, "repo", "dists")

# Keep this many upstream versions in the pool before evicting the oldest.
KEEP = 5


def referenced_in_index(basename):
    """True if any published Packages index still lists this .deb.

    A codename whose recent builds have been failing stays pinned to an older
    version in its index while the others advance. Without this check, once that
    old version becomes the oldest of >KEEP, the janitor would delete the very
    file that codename's index still points at, giving those users 404s / hash
    mismatches on `apt install`. Skipping still-referenced files avoids that.
    """
    if not os.path.isdir(DISTS_DIR):
        return False
    for root, _dirs, files in os.walk(DISTS_DIR):
        for name in files:
            if name == "Packages":
                opener, path = open, os.path.join(root, name)
            elif name == "Packages.gz":
                opener, path = gzip.open, os.path.join(root, name)
            else:
                continue
            try:
                with opener(path, "rt", encoding="utf-8", errors="ignore") as fh:
                    if basename in fh.read():
                        return True
            except OSError:
                continue
    return False


def clean_house():
    if not os.path.exists(POOL_DIR):
        print("Janitor: No existing repo found. Skipping cleanup.")
        return

    files = glob.glob(f"{POOL_DIR}/*.deb")
    if not files:
        return

    versions = set()
    for f in files:
        # Match the upstream version component only — stop at the first hyphen
        # so that 12.0 does not incorrectly match 12.0.1 (the startswith check
        # below enforces the hyphen boundary as well, but the regex must be
        # anchored to the basename to avoid matching directory components).
        match = re.search(r'hiawatha_(\d[\d.]*)-', os.path.basename(f))
        if match:
            versions.add(match.group(1))

    sorted_versions = sorted(versions, key=lambda x: [int(i) for i in x.split('.')])

    if len(sorted_versions) <= KEEP:
        print(f"Janitor: {len(sorted_versions)} version(s) in pool. No eviction needed.")
        return

    target = sorted_versions[0]
    print(f"Janitor: Evicting version {target} to stay under 1 GB limit...")
    evicted = []
    for f in files:
        base = os.path.basename(f)
        # Use startswith on the basename with a trailing hyphen so that a
        # version like 12.0 cannot accidentally match 12.0.1 files.
        if not base.startswith(f"hiawatha_{target}-"):
            continue
        if referenced_in_index(base):
            print(f"  Skipping {base} — still referenced by a live Packages index.")
            continue
        os.remove(f)
        evicted.append(f)
        print(f"  Deleted {base}")

    if evicted:
        subprocess.run(["git", "-C", REPO_DIR, "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", REPO_DIR, "commit",
             "-m", f"Janitor: evict v{target} to stay under 1 GB limit"],
            check=True,
        )


if __name__ == "__main__":
    clean_house()
