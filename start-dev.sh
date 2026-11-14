#!/bin/bash
# FieldShift - Development Startup Script (Linux/macOS)
# Usage: ./start-dev.sh [--install-deps] [--backend-only] [--frontend-only]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

INSTALL_DEPS=false
BACKEND_ONLY=false
FRONTEND_ONLY=false

for arg in "$@"; do
    case $arg in
        --install-deps) INSTALL_DEPS=true ;;
        --backend-only) BACKEND_ONLY=true ;;
        --frontend-only) FRONTEND_ONLY=true ;;
    esac
done

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    FieldShift - Dev Startup                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${CYAN}🔍 Vérification des prérequis...${NC}"

    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js non trouvé. Installez Node.js 18+ depuis https://nodejs.org${NC}"
        exit 1
    fi
    echo -e "  ${NC}✓ Node.js $(node --version)${NC}"

    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python non trouvé. Installez Python 3.11+ depuis https://python.org${NC}"
        exit 1
    fi
    echo -e "  ${NC}✓ $(python3 --version)${NC}"
    echo ""
}

# Install frontend dependencies
install_frontend_deps() {
    echo -e "${CYAN}📦 Installation dépendances Frontend...${NC}"
    cd "$FRONTEND_DIR"
    if [ ! -d "node_modules" ]; then
        npm install
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Échec npm install${NC}"
            exit 1
        fi
    else
        echo -e "  ${NC}✓ node_modules déjà présent${NC}"
    fi
    cd "$PROJECT_ROOT"
    echo ""
}

# Install backend dependencies
install_backend_deps() {
    echo -e "${CYAN}📦 Installation dépendances Backend...${NC}"
    cd "$BACKEND_DIR"

    if [ ! -d "venv" ]; then
        echo -e "  ${NC}Création environnement virtuel...${NC}"
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Échec création venv${NC}"
            exit 1
        fi
    fi

    echo -e "  ${NC}Installation requirements.txt...${NC}"
    ./venv/bin/pip install --upgrade pip -q
    ./venv/bin/pip install -r requirements.txt -q
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Échec pip install${NC}"
        exit 1
    fi

    if [ ! -f ".env" ]; then
        echo -e "  ${YELLOW}Création .env depuis .env.example...${NC}"
        cp .env.example .env
    fi

    cd "$PROJECT_ROOT"
    echo ""
}

# Start backend
start_backend() {
    echo -e "${CYAN}🚀 Démarrage Backend (FastAPI)...${NC}"
    cd "$BACKEND_DIR"
    ./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo -e "  ${GREEN}✓ Backend démarré (PID: $BACKEND_PID)${NC}"
    echo -e "  ${NC}📍 http://localhost:8000${NC}"
    echo -e "  ${NC}📚 Docs: http://localhost:8000/docs${NC}"
    cd "$PROJECT_ROOT"
    echo ""
}

# Start frontend
start_frontend() {
    echo -e "${CYAN}🚀 Démarrage Frontend (Vite)...${NC}"
    cd "$FRONTEND_DIR"
    npm run dev -- --host &
    FRONTEND_PID=$!
    echo -e "  ${GREEN}✓ Frontend démarré (PID: $FRONTEND_PID)${NC}"
    echo -e "  ${NC}📍 http://localhost:5173${NC}"
    cd "$PROJECT_ROOT"
    echo ""
}

# Cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Arrêt des processus...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "  ${NC}✓ Backend arrêté${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "  ${NC}✓ Frontend arrêté${NC}"
    fi
    echo -e "${GREEN}👋 Au revoir !${NC}"
}

trap cleanup EXIT INT TERM

# Main
check_prerequisites

if [ "$INSTALL_DEPS" = true ] || [ ! -d "$FRONTEND_DIR/node_modules" ] || [ ! -d "$BACKEND_DIR/venv" ]; then
    install_frontend_deps
    install_backend_deps
fi

if [ "$FRONTEND_ONLY" = false ]; then
    start_backend
fi

if [ "$BACKEND_ONLY" = false ]; then
    start_frontend
fi

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✨ FieldShift est prêt !                                     ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  Frontend:  http://localhost:5173                            ║${NC}"
echo -e "${GREEN}║  Backend:   http://localhost:8000                            ║${NC}"
echo -e "${GREEN}║  API Docs:  http://localhost:8000/docs                       ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  Appuyez sur Ctrl+C pour arrêter                             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"

# Wait for Ctrl+C
wait