-- initdb --locale en_US.UTF-8 -D '/var/lib/postgres/data' -U bot
-- CREATE DATABASE bullet;

CREATE TABLE IF NOT EXISTS vendor
(
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bulletin
(
    id        SERIAL PRIMARY KEY,
    vendor_id SERIAL NOT NULL,
    title     TEXT   NOT NULL DEFAULT 'UNKW BULLETIN',
    timestamp TIMESTAMP,

    FOREIGN KEY (vendor_id)
	      REFERENCES vendor(id)
);

CREATE TABLE IF NOT EXISTS cve_info
(
    id          SERIAL PRIMARY KEY,
    header      TEXT        DEFAULT '',
    links       TEXT        DEFAULT '',
    description TEXT        DEFAULT '',
    affected    TEXT        DEFAULT '',
    severity    TEXT        DEFAULT '',
    weakness    TEXT        DEFAULT '',
    reported    TEXT        DEFAULT '',
    patch       TEXT        DEFAULT '',
    component   TEXT        DEFAULT '',
    spider      VARCHAR(30) DEFAULT ''
);

CREATE TABLE IF NOT EXISTS cve
(
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(30) NOT NULL DEFAULT 'CVE-UNKW',
    bulletin_id SERIAL NOT NULL,

    FOREIGN KEY (bulletin_id)
	      REFERENCES bulletin(id)
);

CREATE TABLE IF NOT EXISTS cve_info_cve
(
    id          SERIAL PRIMARY KEY,
    cve_id      SERIAL,
    cve_info_id SERIAL,

    FOREIGN KEY (cve_id)
      REFERENCES cve(id),
    FOREIGN KEY (cve_info_id)
      REFERENCES cve_info(id)
);