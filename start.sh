#!/bin/bash

# AI Personal Finance Autopilot - Startup Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AI Personal Finance Autopilot${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if we're in the correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to start backend
start_backend() {
    echo -e "${YELLOW}Starting FastAPI backend...${NC}"
    cd backend
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
        exit 1
    fi
    
    # Start FastAPI
    echo -e "${GREEN}Backend starting on http://localhost:8000${NC}"
    echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
}

# Function to start frontend
start_frontend() {
    echo -e "${YELLOW}Starting Next.js frontend...${NC}"
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${RED}Dependencies not installed. Running npm install...${NC}"
        npm install
    fi
    
    # Start Next.js
    echo -e "${GREEN}Frontend starting on http://localhost:3000${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
}

# Start both services
start_backend
sleep 3
start_frontend

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Services Started Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for user interrupt
trap "echo -e '\n${YELLOW}Stopping services...${NC}'; kill $(cat backend.pid) $(cat frontend.pid); rm backend.pid frontend.pid; echo -e '${GREEN}Services stopped${NC}'; exit 0" INT

# Keep script running
wait
