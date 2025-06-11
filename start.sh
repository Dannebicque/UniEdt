#!/bin/bash

# Lancer l'API Python (adapter le chemin et la commande si besoin)
cd edt-api
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
API_PID=$!
cd ..

# Lancer le front (adapter la commande si besoin)
cd edt-front
# npm install
npm run dev &
FRONT_PID=$!
cd ..

# Attendre que l'utilisateur arrête le script
echo "API Python (port 8000) et front lancés."
echo "Appuyez sur Ctrl+C pour arrêter."
wait $API_PID $FRONT_PID
