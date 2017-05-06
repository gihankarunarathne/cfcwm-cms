/* 
 * CFCWM database for Weather Data Store - create_cfcwm.sql.
 * You need to run this script with an authorized user.
 * $ mysql -h <host> -u <username> -p < create_mysql.sql
 * You can ommit the -h <host> part if the server runs on your localhost.
 */

CREATE DATABASE IF NOT EXISTS curw;

SELECT 'Show Databases ::';
SHOW DATABASES;                -- List the name of all the databases in this server
SELECT '\n';


