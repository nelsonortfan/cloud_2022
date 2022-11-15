#! /bin/bash

#cd /home/d_moralesa2/cloud_2022/Proyecto_cloud/flaskr && flask run -h 0.0.0.0
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

* * * * * echo "App Iniciada" >> /home/jhonsbg/log.txt
@reboot /home/d_moralesa2/cloud_2022/script.sh
