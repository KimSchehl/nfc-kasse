#!/bin/bash
cd /var/www/kasse
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
