CREATE TABLE `curw`.`variable` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `variable` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `curw`.`type` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `type_UNIQUE` (`type` ASC)
);

CREATE TABLE `curw`.`unit` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `unit` VARCHAR(45) NOT NULL,
  `rate` INT NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `curw`.`source` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `source` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `source_UNIQUE` (`source` ASC)
);

CREATE TABLE `curw`.`station` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);

CREATE TABLE `curw`.`run` (
  `id` VARCHAR(64) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `start_date` DATETIME NOT NULL,
  `end_date` DATETIME NOT NULL,
  `station` INT NOT NULL,
  `variable` INT NOT NULL,
  `unit` INT NOT NULL,
  `type` INT NOT NULL,
  `source` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `station_idx` (`station` ASC),
  INDEX `variable_idx` (`variable` ASC),
  INDEX `unit_idx` (`unit` ASC),
  INDEX `type_idx` (`type` ASC),
  INDEX `source_idx` (`source` ASC),
  CONSTRAINT `station`
    FOREIGN KEY (`station`)
    REFERENCES `curw`.`station` (`id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `variable`
    FOREIGN KEY (`variable`)
    REFERENCES `curw`.`variable` (`id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `unit`
    FOREIGN KEY (`unit`)
    REFERENCES `curw`.`unit` (`id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `type`
    FOREIGN KEY (`type`)
    REFERENCES `curw`.`type` (`id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `source`
    FOREIGN KEY (`source`)
    REFERENCES `curw`.`source` (`id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE
);

CREATE TABLE `curw`.`data` (
  `id` VARCHAR(64) NOT NULL,
  `time` DATETIME NOT NULL,
  `value` DECIMAL(8,3) NOT NULL,
  PRIMARY KEY (`id`, `time`),
  CONSTRAINT `id`
    FOREIGN KEY (`id`)
    REFERENCES `curw`.`run` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

INSERT INTO curw.variable VALUES 
  (1, 'Rain'),
  (2, 'Discharge'),
  (3, 'Temp'),
  (4, 'WL');

INSERT INTO curw.type VALUES 
  (1, 'Observed'),
  (2, 'Forecast');

INSERT INTO source VALUES 
  (1, 'HEC-HMS'),
  (2, 'SHER'),
  (3, 'WRF'),
  (4, 'FLO2D'),
  (5, 'EPM');

INSERT INTO curw.station (id, name, x, y)
VALUES
  (1, 'Attanagalla', 7.111666667, 0.0),
  (2, 'Colombo', 0.0, 0.0),
  (3, 'Daraniyagala', 6.924444444, 80.33805556),
  (4, 'Glencourse', 6.978055556, 80.20305556),
  (5, 'Hanwella', 6.909722222, 80.08166667),
  (6, 'Holombuwa', 7.185166667, 80.26480556),
  (7, 'Kitulgala', 6.989166667, 80.41777778),
  (8, 'Norwood', 6.835638889, 80.61466667);

INSERT INTO curw.unit (id, unit, rate)
VALUES
  (1, 'mm', 1),
  (2, 'mm', 5),
  (3, 'mm', 10),
  (4, 'mm', 15),
  (5, 'mm', 20),
  (6, 'mm', 30),
  (7, 'mm', 45),
  (8, 'mm', 60),
  (9, 'm3', 1);





