#!/bin/bash
# run a yum update, create a webserver with a test page
yum -y update
echo "`date` Auto Scaling Group Launch">>/root/message.txt
yum -y install httpd
sed -i "s/Listen 80/Listen 0.0.0.0:80/" /etc/httpd/conf/httpd.conf
systemctl start httpd
echo "cdk">/var/www/html/index.html
