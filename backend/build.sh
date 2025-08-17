#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Step 1: Migrate the 'bingo' app FIRST. This creates the custom user table
# and solves the race condition.
echo "Running bingo migrations..."
python manage.py migrate bingo

# Step 2: Migrate all other apps. Now they can safely link to the user table.
echo "Running remaining migrations..."
python manage.py migrate

# Step 3: Now that all tables exist, create the superuser.
echo "Creating superuser..."
python manage.py create_superuser_from_env