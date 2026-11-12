#!/bin/bash
# Runs inside a pristine target distro container with the built deb at /debs.
# Gate before signing/publishing: the package must install with the distro's
# own dependencies, ship a config wigwam accepts, and actually serve HTTP.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y -qq /debs/hiawatha_*.deb >/dev/null
dpkg-query -W -f='installed ${Package} ${Version}\n' hiawatha

echo "--- wigwam -q ---"
wigwam -q

# Docker images ship a policy-rc.d that blocks postinst from starting
# services, so start it by hand unless postinst already did.
PIDFILE=/run/hiawatha.pid
if ! { [ -s "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; }; then
  /usr/sbin/hiawatha
fi

fetch() {
  exec 3<>/dev/tcp/127.0.0.1/80
  printf 'GET / HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n' >&3
  head -n1 <&3
}
STATUS=""
for _ in $(seq 1 20); do
  STATUS=$( (fetch) 2>/dev/null ) && [ -n "$STATUS" ] && break
  sleep 0.5
done
echo "--- HTTP: ${STATUS:-<no response>} ---"
case "$STATUS" in
  *" 200 "*) echo "Smoke test passed." ;;
  *) echo "::error::hiawatha did not serve the default page"; exit 1 ;;
esac
