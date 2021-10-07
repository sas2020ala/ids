#!/bin/bash

D=/etc/nginx/sites-available

if [ ! "$1" = "" ]
then
  echo "Install prerequests..."

  sudo apt update && sudo apt upgrade
  sudo apt-get install -y build-essential
  sudo apt install -y libmariadb-dev
  sudo apt install -y python3-pip
  sudo apt install -y python3.8-venv

  echo "Create service ..."

  sudo cp ids.service /etc/systemd/system/ids.service
  sudo systemctl start ids.service

  echo "Create file and copy to /etc/nginx/sites-available/ ..."

  FILE=$1

  if test -f "$FILE"; then
    rm ids
  fi

  touch "$FILE"

  echo "
  server {
      listen 80;
      server_name $1.odoovan.com;

     location / {
          include uwsgi_params;
          uwsgi_pass unix:/home/admin/ids/$1.sock;
      }
  }" >> "$FILE"

  sudo cp "$FILE" "$D/ids"

  if test -f "/etc/nginx/sites-enabled/ids"; then
    sudo rm /etc/nginx/sites-enabled/ids
  fi

  sudo ln -s "$D/ids" /etc/nginx/sites-enabled
  sudo systemctl restart nginx
  sudo ufw allow 'Nginx Full'
else
  echo "Please enter server name: bash nginx.sh 'server name'"
fi