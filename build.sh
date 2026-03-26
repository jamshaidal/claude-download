#!/bin/bash
echo "Building Video Downloader for Production..."
echo ""

# Build frontend
echo "[1/2] Building React frontend..."
cd frontend
npm install
npm run build
if [ $? -ne 0 ]; then
    echo "ERROR: Frontend build failed"
    exit 1
fi
cd ..

echo ""
echo "[2/2] Backend is ready (no build step required)"
echo ""
echo "Build complete!"
echo ""
echo "To test locally:"
echo "  cd backend && python app.py"
echo "  Then open http://localhost:5000"
echo ""
echo "To deploy, follow DEPLOYMENT.md instructions"