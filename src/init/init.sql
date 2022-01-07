------------------------------
-- Base de donnée Aptitudes --
------------------------------

---------------------------
--    Drop all tables    --
---------------------------

drop table if exists Evaluations;
drop table if exists Validations;
drop table if exists Aptitudes;
drop table if exists Competences;
drop table if exists Domaines;
drop table if exists Matieres;
drop table if exists Syllabus;
drop table if exists Enseignant;
drop table if exists Etudiant;
drop table if exists SyllabusMatieres;

---------------------------
--   Create all tables   -- 
---------------------------

--------------------
--    Etudiant    --
--------------------
CREATE TABLE Etudiant(
    etudiant_id VARCHAR(255) PRIMARY KEY NOT NULL,
    etudiant_nom VARCHAR(20),
    etudiant_prenom VARCHAR(20)
);

----------------------
--    Enseignant    --
----------------------
CREATE TABLE Enseignant(
    enseignant_id INT PRIMARY KEY NOT NULL,
    enseignant_nom VARCHAR(20),
    enseignant_prenom VARCHAR(20)
);
--------------------
--    Syllabus    --
--------------------
CREATE TABLE Syllabus(
    syllabus_id INT PRIMARY KEY NOT NULL,
    syllabus_nom VARCHAR(20),
    etudiant_id VARCHAR(255),
    FOREIGN KEY(etudiant_id) REFERENCES Etudiant(etudiant_id)
);
--------------------
--    Matieres    --
--------------------
CREATE TABLE Matieres(
    matieres_id INT PRIMARY KEY NOT NULL,
    matieres_nom VARCHAR(20),
    enseignant_id INT,
    FOREIGN KEY(enseignant_id) REFERENCES Enseignant(enseignant_id)
);

CREATE TABLE SyllabusMatieres(
    matiere_id INT,
    syllabus_id INT,
    FOREIGN KEY(matiere_id) REFERENCES Matieres(matiere_id),
    FOREIGN KEY(syllabus_id) REFERENCES Syllabus(syllabus_id)
);

--------------------
--    Domaines    --
--------------------
CREATE TABLE Domaines(
    domaines_id INT PRIMARY KEY NOT NULL,
    domaines_nom VARCHAR(40)
);
-----------------------
--    Competences    --
-----------------------
CREATE TABLE Competences(
    competences_id VARCHAR(255) PRIMARY KEY NOT NULL,
    domaines_id INT,
    competences_nom VARCHAR(40),
    competences_seuil FLOAT,
    FOREIGN KEY(domaines_id) REFERENCES Domaines(domaines_id)
);
---------------------
--    Aptitudes    --
---------------------
CREATE TABLE Aptitudes(
    aptitudes_id INT PRIMARY KEY NOT NULL,
    competences_id VARCHAR(255),
    aptitudes_nom VARCHAR(40),
    FOREIGN KEY(competences_id) REFERENCES Competences(competences_id)
);
----------------------
--    Evaluations    --
----------------------
CREATE TABLE Evaluations(
    evaluations_id INT PRIMARY KEY NOT NULL,
    matiere_id INT,
    aptitudes_id INT,
    evaluations_nom VARCHAR(40),
    FOREIGN KEY(matiere_id) REFERENCES Matieres(matiere_id),
    FOREIGN KEY(aptitudes_id) REFERENCES Aptitudes(aptitudes_id)
);
-----------------------
--    Validations    --
-----------------------
CREATE TABLE Validations(
    validations_id INT PRIMARY KEY NOT NULL,
    aptitudes_id INT,
    evaluations_id INT,
    etudiant_id VARCHAR(255),
    validation_resultat NUMBER(1),
    CONSTRAINT ck_validation_validres CHECK (validation_resultat IN (0,1,2,3)),
    -- 0 -> non validé
    -- 1 -> presque aquis
    -- 2 -> aquis
    -- 3 -> maitrisé
    FOREIGN KEY(aptitudes_id) REFERENCES Aptitudes(aptitudes_id),
    FOREIGN KEY(evaluations_id) REFERENCES Evaluations(evaluations_id),
    FOREIGN KEY(etudiant_id) REFERENCES Etudiant(etudiant_id)
);