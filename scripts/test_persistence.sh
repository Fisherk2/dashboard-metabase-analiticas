#!/bin/bash
# =============================================================================
# test_persistence.sh — F4-06: Roundtrip persistencia (destructivo, opt-in)
# =============================================================================
# Propósito: Validar que el proyecto es reproducible desde cero:
#   make destroy → make setup → make metabase-setup → make test
#
# ⚠️  DESTRUCTIVO: Borra volúmenes de Docker y datos de PostgreSQL.
#     Solo ejecutar en entorno local. NO usar en CI automático.
#
# Uso:
#   ALLOW_DESTRUCTIVE=1 ./scripts/test_persistence.sh
#
# Exit code:
#   0 si el roundtrip completo pasa
#   1 si falla algún paso
# =============================================================================

set -Eeuo pipefail

# ─── Guard: solo si ALLOW_DESTRUCTIVE está activo ──────────
if [[ "${ALLOW_DESTRUCTIVE:-0}" != "1" ]]; then
    echo "ERROR: ALLOW_DESTRUCTIVE no está activo." >&2
    echo "Este script ejecuta 'make destroy' y borra todos los datos." >&2
    echo "Para ejecutar: ALLOW_DESTRUCTIVE=1 $0" >&2
    exit 1
fi

# ─── Timestamps ─────────────────────────────────────────────
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
START_TIME=$(date +%s)

log_info()  { echo "[$(date '+%H:%M:%S')] INFO:  $*"; }
log_error() { echo "[$(date '+%H:%M:%S')] ERROR: $*" >&2; }

# ─── Trap para cleanup ─────────────────────────────────────
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Roundtrip falló en el paso: ${CURRENT_STEP:-inicial}"
    fi
    exit "$exit_code"
}
trap cleanup EXIT

# ─── Ejecutar un paso con logging ──────────────────────────
run_step() {
    local step_name="$1"
    shift
    CURRENT_STEP="$step_name"
    log_info "Paso: $step_name"
    "$@" || {
        log_error "Falló: $step_name"
        return 1
    }
}

# ─── Verificar Docker ──────────────────────────────────────
if ! command -v docker &>/dev/null; then
    log_error "Docker no encontrado. Instalar Docker Desktop o Docker Engine."
    exit 1
fi

if ! docker info &>/dev/null; then
    log_error "Docker daemon no está corriendo."
    exit 1
fi

# ─── Roundtrip ──────────────────────────────────────────────
cd "$PROJECT_DIR"

log_info "=== INICIO ROUNDTRIP ==="

run_step "make destroy"   make destroy
run_step "make setup"     make setup
run_step "make mv-refresh" make mv-refresh
run_step "make metabase-setup" make metabase-setup
run_step "make test"      make test

# Tiempo total
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

log_info "=== ROUNDTRIP COMPLETADO ==="
log_info "Tiempo total: ${MINUTES}m ${SECONDS}s"
