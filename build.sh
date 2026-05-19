#!/usr/bin/env bash
set -e

echo "========================================="
echo "   EduCore ERP - Render Build Script"
echo "========================================="

echo ""
echo ">>> Step 1: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo ">>> Step 2: Collecting static files..."
python manage.py collectstatic --no-input

echo ""
echo ">>> Step 3: Running database migrations..."
python manage.py migrate

echo ""
echo ">>> Step 4: Creating default admin user..."
python manage.py create_admin

echo ""
echo ">>> Step 5: Loading default time slots..."
python manage.py load_timeslots

echo ""
echo "========================================="
echo "   Build Complete! Server starting..."
echo "========================================="
