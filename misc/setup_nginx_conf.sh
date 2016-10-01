#! /bin/bash

FILE_PATH=$(readlink -f $0)
REPO_DIR=$(dirname $FILE_PATH)

sudo ln -f -s $REPO_DIR/water_nginx.conf  /etc/nginx/sites-available/
sudo ln -f -s $REPO_DIR/water_nginx.conf  /etc/nginx/sites-enabled/
sudo service nginx reload

