#!/bin/bash

echo "Start deploy script"

set -e


echo "Add Work dir"
ENV_DIR=/opt/StarBurger/
WORK_DIR=/opt/StarBurger/star-burger

echo "Activate env"
cd $ENV_DIR
source  .venv/bin/activate

cd $WORK_DIR

echo "Download last updated fises from repo"
git pull origin master

echo "Install python requirements"
pip install -r requirements.txt

echo "Build frontend"
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Make Django-python migrations"
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "restart burger-shop service"
sudo systemctl restart burger-shop.service
