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

echo "add deploy info to Rollbar"
json_payload=$(
cat <<EOF
{
"revision": "$(git rev-parse --short HEAD)",
"environment": "$(echo $ROLLBAR_ENV)",
"rollbar_username": "<your_name>",
"comment": "$(git log -1 --pretty=format:"%s")"
}
EOF
)
curl --request POST https://api.rollbar.com/api/1/deploy \
--header "X-Rollbar-Access-Token: $(echo $ROLLBAR_TOKEN)" \
--header "Accept: application/json" \
--header "Content-Type: application/json" \
--data "$json_payload"

echo "restart burger-shop service"
sudo systemctl restart burger-shop.service
