#!/usr/bin/env bash
# fiabeSonore — setup script for Raspberry Pi OS (Debian/Bookworm or Bullseye).
# Installs Python 3, system packages, project dependencies, enables SPI,
# then runs a quick smoke test on the imports and audio backend.
#
# Usage:  ./setup.sh
#         sudo ./setup.sh        # if not already root for apt/raspi-config

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PY_MIN_MAJOR=3
PY_MIN_MINOR=9

# ────────── helpers ──────────
info()  { printf "\033[1;34m▸\033[0m %s\n" "$*"; }
ok()    { printf "\033[1;32m✓\033[0m %s\n" "$*"; }
warn()  { printf "\033[1;33m!\033[0m %s\n" "$*"; }
fail()  { printf "\033[1;31m✗\033[0m %s\n" "$*"; exit 1; }

need_sudo() {
    if [[ $EUID -ne 0 ]]; then
        if ! command -v sudo >/dev/null 2>&1; then
            fail "Servono privilegi root, ma 'sudo' non è installato."
        fi
        SUDO="sudo"
    else
        SUDO=""
    fi
}

# ────────── 1. Python 3 ──────────
check_python() {
    info "Verifico Python 3..."
    if ! command -v python3 >/dev/null 2>&1; then
        warn "python3 non trovato. Installo..."
        $SUDO apt-get update -y
        $SUDO apt-get install -y python3 python3-pip
    fi

    local version
    version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    local major="${version%%.*}"
    local minor="${version##*.}"

    if (( major < PY_MIN_MAJOR )) || { (( major == PY_MIN_MAJOR )) && (( minor < PY_MIN_MINOR )); }; then
        fail "Python $version trovato, ma serve almeno ${PY_MIN_MAJOR}.${PY_MIN_MINOR}."
    fi
    ok "Python $version"
}

# ────────── 2. System packages ──────────
install_system_packages() {
    info "Installo pacchetti di sistema (apt)..."
    $SUDO apt-get update -y
    $SUDO apt-get install -y \
        python3-pip \
        python3-venv \
        python3-pygame \
        python3-rpi.gpio \
        vlc \
        libsdl2-mixer-2.0-0 \
        raspi-config || warn "Alcuni pacchetti non sono installabili (probabilmente non sei su Pi OS)."
    ok "Pacchetti di sistema pronti"
}

# ────────── 3. Enable SPI ──────────
enable_spi() {
    info "Verifico SPI..."
    if ! command -v raspi-config >/dev/null 2>&1; then
        warn "raspi-config non disponibile — salto attivazione SPI."
        return
    fi
    # 0 = enable in raspi-config nonint API
    $SUDO raspi-config nonint do_spi 0 || warn "Impossibile abilitare SPI via raspi-config."
    ok "SPI abilitato (riavvio consigliato se era disattivato)"
}

# ────────── 4. User groups ──────────
add_groups() {
    info "Aggiungo l'utente $USER ai gruppi spi e gpio..."
    for grp in spi gpio; do
        if getent group "$grp" >/dev/null; then
            $SUDO usermod -aG "$grp" "$USER" || warn "Impossibile aggiungere $USER a $grp."
        fi
    done
    ok "Gruppi aggiornati (logout/login per rendere effettivo)"
}

# ────────── 5. Python deps (venv — PEP 668) ──────────
install_python_deps() {
    local req="$SCRIPT_DIR/requirements.txt"
    [[ -f "$req" ]] || fail "requirements.txt non trovato in $SCRIPT_DIR"

    if [[ ! -d "$VENV_DIR" ]]; then
        info "Creo virtualenv in $VENV_DIR (con --system-site-packages per ereditare pygame/RPi.GPIO da apt)..."
        python3 -m venv --system-site-packages "$VENV_DIR" \
            || fail "Creazione venv fallita. Manca python3-venv? (apt install python3-venv)"
    else
        info "Virtualenv già presente in $VENV_DIR — riuso."
    fi

    info "Aggiorno pip e installo le dipendenze nel venv..."
    "$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
    "$VENV_DIR/bin/pip" install -r "$req" || fail "Installazione dipendenze fallita."
    ok "Dipendenze installate nel venv"
}

# ────────── 6. Smoke test ──────────
smoke_test() {
    local py="$VENV_DIR/bin/python3"
    [[ -x "$py" ]] || fail "Python del venv non trovato: $py"

    info "Smoke test: import dei moduli chiave (via venv)..."
    "$py" - <<'PY' || fail "Import dei moduli fallito."
import importlib, sys
modules = ["pygame", "vlc", "mfrc522", "RPi.GPIO"]
missing = []
for m in modules:
    try:
        importlib.import_module(m)
        print(f"  ✓ {m}")
    except Exception as e:
        print(f"  ✗ {m}: {e}")
        missing.append(m)
sys.exit(1 if missing else 0)
PY
    ok "Tutti i moduli importati correttamente"

    info "Smoke test: backend audio (pygame.mixer)..."
    "$py" - "$SCRIPT_DIR/match0.wav" <<'PY' || warn "Audio non verificato (controlla speaker/HDMI/jack)."
import sys, time, pygame
wav = sys.argv[1]
pygame.mixer.init()
pygame.mixer.music.load(wav)
pygame.mixer.music.play()
time.sleep(1.0)
pygame.mixer.music.stop()
pygame.mixer.quit()
print("  ✓ audio playback ok")
PY
    ok "Setup completato"
}

# ────────── main ──────────
main() {
    info "fiabeSonore — setup"
    need_sudo
    check_python
    install_system_packages
    enable_spi
    add_groups
    install_python_deps
    smoke_test

    echo
    ok "Tutto pronto."
    echo "  • Riavvia se SPI è stato appena abilitato:   sudo reboot"
    echo "  • Esegui il player (dal venv):               .venv/bin/python3 rfidReader.py"
    echo "  • Oppure attiva il venv:                     source .venv/bin/activate"
    echo "  • Programma una card:                        .venv/bin/python3 program_card.py <file>"
    echo "  • Systemd: fiabesonore.service punta già a .venv/bin/python3"
    echo "    (controlla WorkingDirectory se il path di deploy è diverso)"
}

main "$@"
