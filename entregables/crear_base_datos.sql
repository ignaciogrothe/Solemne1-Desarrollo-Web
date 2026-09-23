-- Creacion de la base de datos y el usuario de la aplicacion.
-- Ejecutar como superusuario de PostgreSQL:
--   psql -d postgres -f entregables/crear_base_datos.sql

CREATE USER vet_user WITH PASSWORD 'vet_pass_2026';

CREATE DATABASE clinica_veterinaria
    OWNER vet_user
    ENCODING 'UTF8';

GRANT ALL PRIVILEGES ON DATABASE clinica_veterinaria TO vet_user;

-- Permite que Django cree la base de datos temporal de los tests.
ALTER USER vet_user CREATEDB;
