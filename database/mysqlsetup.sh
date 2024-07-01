sudo systemctl start mysql

sudo mysql -u root -e "CREATE DATABASE LEGO;"

sudo mysql -u root LEGO < database_init.sql

sudo mysql -u root LEGO < sql/colors.sql
sudo mysql -u root LEGO < sql/sets.sql
sudo mysql -u root LEGO < sql/parts.sql
sudo mysql -u root LEGO < sql/inventory_parts.sql