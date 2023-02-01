----------------------------------
-- Creación de la base de datos --
----------------------------------

drop database RateMyShow;
create database RateMyShow;
use RateMyShow;


------------------------
-- Creación de tablas --
------------------------

CREATE TABLE `Users` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`username` VARCHAR(255) NOT NULL UNIQUE,
	`password` VARCHAR(255) NOT NULL,
	`email` VARCHAR(255) NOT NULL UNIQUE,
	`phone` VARCHAR(255) UNIQUE,
	`birthDate` DATE NOT NULL,
	`registerDate` DATETIME NOT NULL,
	`avatarId` INT NOT NULL,
	`name` VARCHAR(255) NOT NULL,
	`surname` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Titles` (
	`id` VARCHAR(255) NOT NULL,
	`titleType` INT NOT NULL,
	`primaryTitle` VARCHAR(255) NOT NULL,
	`originalTitle` VARCHAR(255) NOT NULL,
	`startYear` INT NOT NULL,
	`endYear` INT NOT NULL,
	`runtimeMinutes` INT NOT NULL,
	`language` VARCHAR(255) NOT NULL,
	`cover` TEXT,
	`description` TEXT,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Ratings` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`posterId` INT NOT NULL,
	`titleId` VARCHAR(255) NOT NULL,
	`rating` FLOAT NOT NULL,
	`addedDate` DATETIME NOT NULL,
	`comment` TEXT,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Participants` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`titleId` VARCHAR(255) NOT NULL,
	`personId` VARCHAR(255) NOT NULL UNIQUE,
	`category` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Names` (
	`id` VARCHAR(255) NOT NULL,
	`name` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `ParticipantCategories` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`category` VARCHAR(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE `GenreTypes` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`genre` VARCHAR(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Tokens` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`userId` INT NOT NULL,
	`token` VARCHAR(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Followers` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`followerId` INT NOT NULL,
	`followedId` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Avatars` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`avatar` VARCHAR(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE `TitleTypes` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Genres` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`titleId` VARCHAR(255) NOT NULL,
	`genreId` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Favorites` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`userId` INT NOT NULL,
	`titleId` VARCHAR(255) NOT NULL,
	`addedDate` DATETIME NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Pending` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`userId` INT NOT NULL,
	`titleId` VARCHAR(255) NOT NULL,
	`addedDate` DATETIME NOT NULL,
	PRIMARY KEY (`id`)
);

---------------------
-- Claves foráneas --
---------------------

ALTER TABLE `Users` ADD CONSTRAINT `Users_fk0` FOREIGN KEY (`avatarId`) REFERENCES `Avatars`(`id`);

ALTER TABLE `Titles` ADD CONSTRAINT `Titles_fk0` FOREIGN KEY (`titleType`) REFERENCES `TitleTypes`(`id`);

ALTER TABLE `Ratings` ADD CONSTRAINT `Ratings_fk0` FOREIGN KEY (`posterId`) REFERENCES `Users`(`id`);

ALTER TABLE `Ratings` ADD CONSTRAINT `Ratings_fk1` FOREIGN KEY (`titleId`) REFERENCES `Titles`(`id`);

ALTER TABLE `Participants` ADD CONSTRAINT `Participants_fk0` FOREIGN KEY (`titleId`) REFERENCES `Titles`(`id`);

ALTER TABLE `Participants` ADD CONSTRAINT `Participants_fk1` FOREIGN KEY (`personId`) REFERENCES `Names`(`id`);

ALTER TABLE `Participants` ADD CONSTRAINT `Participants_fk2` FOREIGN KEY (`category`) REFERENCES `ParticipantCategories`(`id`);

ALTER TABLE `Tokens` ADD CONSTRAINT `Tokens_fk0` FOREIGN KEY (`userId`) REFERENCES `Users`(`id`);

ALTER TABLE `Followers` ADD CONSTRAINT `Followers_fk0` FOREIGN KEY (`followerId`) REFERENCES `Users`(`id`);

ALTER TABLE `Followers` ADD CONSTRAINT `Followers_fk1` FOREIGN KEY (`followedId`) REFERENCES `Users`(`id`);

ALTER TABLE `Genres` ADD CONSTRAINT `Genres_fk0` FOREIGN KEY (`titleId`) REFERENCES `Titles`(`id`);

ALTER TABLE `Genres` ADD CONSTRAINT `Genres_fk1` FOREIGN KEY (`genreId`) REFERENCES `GenreTypes`(`id`);

ALTER TABLE `Favorites` ADD CONSTRAINT `Favorites_fk0` FOREIGN KEY (`userId`) REFERENCES `Users`(`id`);

ALTER TABLE `Favorites` ADD CONSTRAINT `Favorites_fk1` FOREIGN KEY (`titleId`) REFERENCES `Titles`(`id`);

ALTER TABLE `Pending` ADD CONSTRAINT `Pending_fk0` FOREIGN KEY (`userId`) REFERENCES `Users`(`id`);

ALTER TABLE `Pending` ADD CONSTRAINT `Pending_fk1` FOREIGN KEY (`titleId`) REFERENCES `Titles`(`id`);

------------------------------------------------------------------
-- Importar datos de archivos TSV (deben estar en la ruta /db/) --
------------------------------------------------------------------

LOAD DATA LOCAL INFILE '/db/GenreTypes.tsv'
INTO TABLE GenreTypes
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/db/TitleTypes.tsv'
INTO TABLE TitleTypes
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/db/ParticipantCategory.tsv'
INTO TABLE ParticipantCategories
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/db/Names.tsv'
INTO TABLE Names
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/db/Titles.tsv'
INTO TABLE Titles
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/db/Genres.tsv'
INTO TABLE Genres
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE '/db/Participants.tsv'
INTO TABLE Participants
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


------------------------------------
-- Se añade el avatar por defecto --
------------------------------------

insert into Avatars values(1, "Pollito");
insert into Avatars values(2, "Abeja");
insert into Avatars values(3, "Ajolote");
insert into Avatars values(4, "Koala");
insert into Avatars values(5, "Leon");
insert into Avatars values(6, "Oveja");
insert into Avatars values(7, "Tortuga");
insert into Avatars values(8, "Pajaro");
insert into Avatars values(9, "Vaca");
insert into Avatars values(10, "Zorro");
insert into Avatars values(11, "Tigre");
insert into Avatars values(12, "Oso");
insert into Avatars values(13, "Rana");
insert into Avatars values(14, "Vaca2");
insert into Avatars values(15, "Pajaro2");
insert into Avatars values(16, "Panda");
insert into Avatars values(17, "Hipopotamo");
insert into Avatars values(18, "Zorro2");
insert into Avatars values(19, "Ciervo");
insert into Avatars values(20, "Nutria");