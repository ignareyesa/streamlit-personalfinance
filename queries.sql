create table users (
    id integer AUTO_INCREMENT PRIMARY KEY,
    email varchar(50) UNIQUE,
    username varchar(50) UNIQUE,
    name varchar(100),
    pass char(60)
);