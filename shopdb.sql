CREATE DATABASE IF NOT EXISTS shopdb;
USE shopdb;


-- SELECT descricao as role, email, password
-- from shopdb.roles, shopdb.utilizadores
-- where roleId = roles.id;



-- #1 ROLES
CREATE TABLE IF NOT EXISTS roles (
    id INT(11) NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    descricao VARCHAR(100) NOT NULL
);


-- #2 CATEGORIAS
CREATE TABLE IF NOT EXISTS categorias (
    id INT(11) NOT NULL AUTO_INCREMENT,
    descricao VARCHAR(250) NOT NULL,
    PRIMARY KEY (id)
);


-- #3 PRODUTOS
CREATE TABLE IF NOT EXISTS produtos (
    id INT(11) NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    descricao VARCHAR(250) NOT NULL,
    preco FLOAT NOT NULL,
    image_url VARCHAR(100) NOT NULL,
    categoriaId INT(11),
    FOREIGN KEY (categoriaId) REFERENCES categorias(id)
);


-- #4 UTILIZADORES
CREATE TABLE IF NOT EXISTS utilizadores (
    id INT(11) NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    roleId INT(11) NOT NULL,
    FOREIGN KEY (roleId) REFERENCES roles(id)
);


-- #5 CLIENTES
CREATE TABLE IF NOT EXISTS clientes (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    nome VARCHAR(100) NOT NULL,
    morada VARCHAR(100) NOT NULL,
    utilizadorId INT(11) NOT NULL,
    FOREIGN KEY (utilizadorId) REFERENCES utilizadores(id)
);


-- #6 ENCOMENDAS
CREATE TABLE IF NOT EXISTS encomendas (
    id INT(11) NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    dataEncomenda DATE NOT NULL,
    total FLOAT NOT NULL,
    clienteId INT(11) NOT NULL,
    FOREIGN KEY (clienteId) REFERENCES clientes(id)
);


-- #7 LINHAS_ENCOMENDA
CREATE TABLE IF NOT EXISTS linhas_encomenda (
    id INT(11) NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id),
    quantidade INT(11) NOT NULL,
    encomendaId INT(11) NOT NULL,
    produtoId INT(11) NOT NULL,
    FOREIGN KEY (encomendaId) REFERENCES encomendas(id),
    FOREIGN KEY (produtoId) REFERENCES produtos(id)
);

-- SET FOREIGN_KEY_CHECKS=0
-- SET FOREIGN_KEY_CHECKS=1

