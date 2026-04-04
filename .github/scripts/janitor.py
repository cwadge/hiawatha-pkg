import os
import re
import glob
import subprocess


def clean_house():
    pool_dir = "gh-pages-branch/pool/main/h/hiawatha"
    repo_dir = "gh-pages-branch"

    if not os.path.exists(pool_dir):
        print("Janitor: No existing repo found. Skipping cleanup.")
        return

    files = glob.glob(f"{pool_dir}/*.deb")
    if not files:
        return

    versions = set()
    for f in files:
        # Match the upstream version component only — stop at the first hyphen
        # so that 12.0 does not incorrectly match 12.0.1 (startswith check below
        # enforces the hyphen boundary as well, but the regex must be anchored
        # to the basename to avoid matching directory components).
        match = re.search(r'hiawatha_(\d[\d.]*)-', os.path.basename(f))
        if match:
            versions.add(match.group(1))

    sorted_versions = sorted(versions, key=lambda x: [int(i) for i in x.split('.')])

    if len(sorted_versions) > 5:
        target = sorted_versions[0]
        print(f"Janitor: Evicting version {target} to stay under 1 GB limit...")
        evicted = []
        for f in files:
            # Use startswith on the basename with a trailing hyphen so that a
            # version like 12.0 cannot accidentally match 12.0.1 files.
            if os.path.basename(f).startswith(f"hiawatha_{target}-"):
                os.remove(f)
                evicted.append(f)
                print(f"  Deleted {os.path.basename(f)}")

        if evicted:
            subprocess.run(["git", "-C", repo_dir, "add", "-A"], check=True)
            subprocess.run(
                ["git", "-C", repo_dir, "commit",
                 "-m", f"Janitor: evict v{target} to stay under 1 GB limit"],
                check=True,
            )
    else:
        print(f"Janitor: {len(sorted_versions)} version(s) in pool. No eviction needed.")


if __name__ == "__main__":
    clean_house()
