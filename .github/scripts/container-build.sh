#!/bin/bash
# Runs inside the target distro container with the workspace mounted at /work.
# Required env: VERSION (e.g. 12.4-1), SUFFIX (e.g. ~deb13u1), CODENAME.
# Leaves the main .deb (not dbgsym) in /work/out/.
set -euo pipefail
: "${VERSION:?}" "${SUFFIX:?}" "${CODENAME:?}"
export DEBIAN_FRONTEND=noninteractive
cd /work

apt-get update -qq
apt-get install -y -qq --no-install-recommends devscripts >/dev/null
# debian/control is the single source of build deps (pulls build-essential too).
apt-get build-dep -y -qq --no-install-recommends ./ >/dev/null

# Changelog: if the top entry is already this exact revision (a packaging bump
# written by hand), keep its text and only retarget version suffix + codename.
# Otherwise this is a new upstream release: prepend a proper entry so that
# `apt changelog hiawatha` doesn't show the previous release's notes.
CL_VER=$(dpkg-parsechangelog -S Version)
if [ "$CL_VER" = "$VERSION" ]; then
  sed -i "1s/^\([^ ]*\) ([^)]*) [^;]*;/\1 (${VERSION}${SUFFIX}) ${CODENAME};/" debian/changelog
else
  MAINT=$(sed -n 's/^Maintainer: //p' debian/control)
  DEBFULLNAME="${MAINT% <*}"
  DEBEMAIL="${MAINT##*<}"; DEBEMAIL="${DEBEMAIL%>}"
  export DEBFULLNAME DEBEMAIL
  dch --newversion "${VERSION}${SUFFIX}" --distribution "$CODENAME" \
      --force-distribution "New upstream release ${VERSION%-*}."
fi
echo "--- changelog head ---"
sed -n '1,3p' debian/changelog

dpkg-buildpackage -us -uc -b

# dpkg-buildpackage writes to the parent dir (/ here, not host-visible).
mkdir -p /work/out
cp -v ../hiawatha_*.deb /work/out/
