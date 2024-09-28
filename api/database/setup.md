MONGO:

https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/#std-label-install-mdb-community-ubuntu

za pomocą skryptu:
mongodb.add_models()

Terminal:
mongosh

MYSQL:

https://stackoverflow.com/questions/39281594/error-1698-28000-access-denied-for-user-rootlocalhost

chmod +x mysqlsetup.sh
./mysqlsetup.sh

sudo mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'twoje_haslo';
FLUSH PRIVILEGES;

sudo systemctl restart mysql

Terminal:
sudo mysql -u root -p
hasło: root

aby użyć tabeli
USE LEGO;
