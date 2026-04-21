SHOW DATABASES;
USE metacode_11th;

SHOW tables;

SELECT * 
FROM pokemon_prep;

DESC pokemon_prep;

/*  */

SELECT DISTINCT Name, `Type` 
FROM pokemon_prep p
WHERE `Type` IN ("GRASS", "POISON", "FIRE", "FLYING", "DRAGON");
