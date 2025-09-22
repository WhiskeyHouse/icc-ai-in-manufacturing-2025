\connect postgres;

SELECT 'CREATE DATABASE "whk-spark" WITH OWNER = admin'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'whk-spark')\gexec

SELECT 'CREATE DATABASE "ignitionreporting" WITH OWNER = admin'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ignitionreporting')\gexec

SELECT 'CREATE DATABASE "ignition" WITH OWNER = admin'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ignition')\gexec

SELECT 'CREATE DATABASE "whk-wms" WITH OWNER = admin'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'whk-wms')\gexec

SELECT 'CREATE DATABASE "whk-mes" WITH OWNER = admin'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'whk-mes')\gexec