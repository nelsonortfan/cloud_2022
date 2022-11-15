#! /bin/bash

cd ..
cd krishtiand/
mkdir Proyecto_Cloud
cd Proyecto_Cloud/
sudo apt install git
y
git clone https://github.com/nelsonortfan/cloud_2022.git
cd cloud_2022/
cd Proyecto_cloud/
cd flaskr/
sudo apt install python3-pip
y
pip install flask==2.1.0
pip install flask_restful
pip install flask-jwt-extended
pip install flask_sqlalchemy  
pip install flask-cors
pip install marshmallow-sqlalchemy
pip install google-cloud-speech
pip install google-cloud-storage
pip install google-cloud-bigquery
pip install google-cloud-texttospeech
pip install psycopg2-binary 
python3 -m flask run


