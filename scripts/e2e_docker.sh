#!/usr/bin/env bash
# Run the end-to-end test suite against an Open Climate Service Docker container.
#
# Builds the image from the sibling checkout, runs it with a small Rwanda extent and
# any data-source credentials from .env, points the e2e suite at it, and tears the
# container down afterwards.
#
# Overridable via environment:
#   OCS_REPO   path to the open-climate-service checkout   (default ../open-climate-service)
#   IMAGE      image tag to build/run                      (default ocs-e2e:latest)
#   PORT       host port to publish                         (default 8088)
#   KEEP       set to 1 to leave the container running for inspection
#   NO_BUILD   set to 1 to skip the image build (reuse IMAGE)
set -euo pipefail

OCS_REPO="${OCS_REPO:-../open-climate-service}"
IMAGE="${IMAGE:-ocs-e2e:latest}"
PORT="${PORT:-8088}"
CONTAINER="ocs-e2e-mk"
KEEP="${KEEP:-0}"
NO_BUILD="${NO_BUILD:-0}"

here="$(cd "$(dirname "$0")/.." && pwd)"
workdir="$(mktemp -d)"

cleanup() {
  if [ "$KEEP" = "1" ]; then
    echo ">>> Leaving container '$CONTAINER' running on http://127.0.0.1:${PORT} (KEEP=1)"
  else
    docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
  fi
  rm -rf "$workdir"
}
trap cleanup EXIT

cat > "$workdir/climate-service.yaml" <<'YAML'
id: e2e-docker
name: Rwanda (docker e2e)
extent:
  name: Rwanda
  bbox: [28.8, -2.9, 30.9, -1.0]
  country_code: RWA
data_dir: ./data
YAML

if [ "$NO_BUILD" != "1" ]; then
  echo ">>> Building $IMAGE from $OCS_REPO"
  docker build -t "$IMAGE" "$OCS_REPO"
fi

# Pass credentials (CDS / Earth Data Hub) from .env if present; harmless if absent.
env_file_arg=()
[ -f "$here/.env" ] && env_file_arg=(--env-file "$here/.env")

echo ">>> Starting container '$CONTAINER' on port $PORT"
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" \
  -p "${PORT}:8000" \
  "${env_file_arg[@]}" \
  -e CLIMATE_SERVICE_CONFIG=/app/climate-service.yaml \
  -v "$workdir/climate-service.yaml:/app/climate-service.yaml:ro" \
  "$IMAGE" >/dev/null

echo ">>> Waiting for health"
for _ in $(seq 1 60); do
  if curl -sf -m2 "http://127.0.0.1:${PORT}/health" >/dev/null; then
    echo "    healthy"
    break
  fi
  sleep 1
done

# Make the ERA5 credential gate see the same keys the container has, so that test runs
# (rather than skipping) when CDS credentials are configured.
set -a
# shellcheck disable=SC1091
[ -f "$here/.env" ] && . "$here/.env"
set +a
unset OCS_BASE_URL || true

echo ">>> Running e2e suite against the container"
OCS_E2E_BASE_URL="http://127.0.0.1:${PORT}" uv run pytest -v -m e2e
