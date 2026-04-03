import os, re, glob

def clean_house():
    pool_dir = "gh-pages-branch/pool/main/h/hiawatha"
    if not os.path.exists(pool_dir):
        print("Janitor: No existing repo found. Skipping cleanup.")
        return

    files = glob.glob(f"{pool_dir}/*.deb")
    if not files:
        return

    versions = set()
    for f in files:
        match = re.search(r'hiawatha_(.*?)-', os.path.basename(f))
        if match:
            versions.add(match.group(1))
    
    sorted_versions = sorted(list(versions), key=lambda x: [int(i) for i in x.split('.')])

    if len(sorted_versions) > 5:
        target = sorted_versions[0]
        print(f"🧹 Janitor: Evicting version {target} to preserve 1GB limit...")
        for f in files:
            if f"hiawatha_{target}" in f:
                os.remove(f)
                print(f"  - Deleted {os.path.basename(f)}")
    else:
        print(f"Janitor: Repo has {len(sorted_versions)} versions. Well under limit.")

if __name__ == "__main__":
    clean_house()
