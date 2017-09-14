This is steps to congfigure and run a python web application on linux server (Ubuntu).

  - IP: 35.176.105.33
  - URL: http://ec2-35-176-105-33.eu-west-2.compute.amazonaws.com/

## Walkthrough

####   1. Create New User and give it sudo permision

  1. create user grader
        - sudo adduser grader
        it gets some info from me like fullname, room number, work phone, home phone and other
  2. create new file in sudoers.d with the username  
      - sudo nano /etc/sudoers.d/grader
      - copy this in it "grader ALL=(ALL) NOPASSWD:ALL"

####   2. Change time Zone
- sudo dpkg-reconfigure tzdata
		- SELECT "None of the above" then "UTC"

####   3. Install Apache2 to serve a Python mod_wsgi application
1. update the packages
    - sudo apt-get update  
2. install apache
    - sudo apt-get install apache2 
2. install Mod_wsg and enable it
    - sudo apt-get install libapache2-mod-wsgi python-dev
    - sudo a2enmod wsgi 
    (you will get the message "Module wsgi already enabled")

#### 4. Clone your flask "catalog" App
1. install git
    - sudo apt-get install git 
2. Clone the project
    - sudo mkdir catalog
    - cd catalog
    - sudo git clone https://github.com/Ammar299/catalog.git catalog
    - move the wsgi file to the upper folder
    - sudo mv /var/www/catalog/catalog/catalog.wsgi /var/www/catalog/

####   5. Install flask and needed modules
1. install pip
    - sudo apt-get install python-pip 
2. install virtualenv 
    - sudo pip install virtualenv 
3. create and activate virtualenv  
    - sudo virtualenv venv
    - source venv/bin/activate
4. Install flask and modules  
    - sudo pip install Flask
    - sudo pip install httplib2 oauth2client sqlalchemy psycopg2 sqlalchemy_utils requests Flask-Login werkzeug


####   6.  Configure and Enable a New Virtual Host
1. create new config file 
    - sudo nano /etc/apache2/sites-available/catalog.conf
2. copy this
    - <VirtualHost *:80>
    ServerName 35.176.105.33
    ServerAlias  ec2-35-176-105-33.eu-west-2.compute.amazonaws.com
    ServerAdmin admin@35.176.105.33
    WSGIDaemonProcess catalog python-path=/var/www/catalog:/var/www/catalog/venv/lib/python2.7/site-packages
    WSGIProcessGroup catalog
    WSGIScriptAlias / /var/www/catalog/catalog.wsgi
    <Directory /var/www/catalog/catalog/>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/catalog/catalog/static
    <Directory /var/www/catalog/catalog/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
3. enable the virtual host 
    - sudo a2ensite catalog
	it will tell you "Enabling site catalog. To activate the new configuration, you need to run: service apache2 reload"
4. restart Apache
    -  sudo service apache2 restart

####   7. Install PostgreSQL and create the database
1. install PostgreSQL
    - sudo apt-get install postgresql postgresql-contrib
2. Create a PostgreSQL user and Database
    - sudo -u postgres createuser -P catalog
    - sudo -u postgres createdb -O catalog catalog
3. Setup catalog application DataBase and add Intial Data
    - sudo python database_setup.py
    - sudo python data.py


> catalog now is up and running ypu can use reach it on the server url

####   8. Set up LightSail FireWall and (UFW)
1. Setup LightSail FireWall
    - Go to networking tap and add tcp ports 123 (NTP) , 2200 (new SSH)
2. setup ufw
    - sudo ufw default deny incoming
    - sudo ufw default allow outgoing
    - sudo ufw allow www
    - sudo ufw allow ntp
	- sudo ufw allow 2200/tcp
    - sudo ufw enable (Firewall is active and enabled on system startup)

####   9. Change SSH Port to 2200 and Disable root remote login
1. sudo nano /etc/ssh/sshd_config
2. change port from 22 to 2200
3. PermitRootLogin no
4. sudo service ssh restart
5. exit then use ssh with the new port ssh -p 2200 grader@35.176.105.33

#### 10. Create SSH Key and upload it in Lightsail account ssh keys
1. in your local machine create ssh public and private keys
    - ssh-keygen
2. open your lightsail account and upload the public key in the Region

### 11. Set up grader ssh keys
1. cd /home/grader/
2. sudo mkdir .ssh
3. sudo touch .ssh/authorized_keys
4. copy public key content and past in authorized_keys
    - sudo nano .ssh/authorized_keys
5. set file permissons
    - sudo chmod 700 .ssh
    - sudo chmod 644 .ssh/authorized_keys
6. force ssh key connection edi this file "PasswordAuthantication" to no
    - sudo nano /etc/ssh/sshd_config
    - sudo service ssh restart
7. to use ssh you must add path to private key on ssh command
	- ssh grader@35.176.105.33 -p 2200 -i PATH TO KEY
8. to update all available packages
    - sudo apt update
    - sudo apt upgrade
