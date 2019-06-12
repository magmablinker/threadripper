CREATE DATABASE threadrip;
USE threadrip;

CREATE TABLE threads (
  thread_no INT NOT NULL,
  thread_title TEXT NOT NULL,
  PRIMARY KEY(thread_no)
);

CREATE TABLE comments (
  cid INT AUTO_INCREMENT NOT NULL,
  tid INT NOT NULL,
  comment TEXT NULL,
  PRIMARY KEY(cid),
  FOREIGN KEY(tid) REFERENCES threads(thread_no)
  ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE images (
  iid INT AUTO_INCREMENT NOT NULL,
  cid INT NOT NULL,
  image MEDIUMTEXT NULL,
  PRIMARY KEY(iid),
  FOREIGN KEY(cid) REFERENCES comments(cid)
  ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE USER 'threadripper'@'localhost' IDENTIFIED BY '1337';
GRANT ALL ON threadrip.* TO 'threadripper'@'localhost';
