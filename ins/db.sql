--
-- 
--

CREATE SEQUENCE app_id_seq
    START WITH 2
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;

CREATE TABLE app (
    app_i integer DEFAULT nextval(app_id_seq) NOT NULL,
    app_n varchar(20) NOT NULL,
    app_d varchar(256),
	ver integer DEFAULT 0,
    s_time timestamp NOT NULL DEFAULT current_timestamp(),
    e_time timestamp,
	v_last varchar(1) DEFAULT 'y',
	status integer DEFAULT 0 NOT NULL,
	PRIMARY KEY (app_i, ver)
);

CREATE TABLE app_r (
	app_i integer NOT NULL,
    app_code varchar(64) NOT NULL UNIQUE KEY, -- hash code
    app_ts timestamp NOT NULL, -- timestamp
    app_dr date NOT NULL,  -- data registration
    app_v varchar(15) NOT NULL, -- version
	ver integer DEFAULT 0,
    s_time timestamp NOT NULL DEFAULT current_timestamp(),
    e_time timestamp,
	v_last varchar(1) DEFAULT 'y',
	status integer DEFAULT 0 NOT NULL,
	PRIMARY KEY (app_i, ver)
);

CREATE SEQUENCE devices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 999999
    CACHE 1;

CREATE TABLE device (
    device_i integer DEFAULT nextval(devices_id_seq) NOT NULL,
	lbl varchar(150) NOT NULL, -- name
	alt varchar(300), -- description
    h_code varchar(512) NOT NULL,  -- hash code
    org_i integer NOT NULL,
	ver integer DEFAULT 0,
    s_time timestamp NOT NULL DEFAULT current_timestamp(),
    e_time timestamp,
	v_last varchar(1) DEFAULT 'y',
	status integer DEFAULT 0 NOT NULL,
	PRIMARY KEY (device_i, ver)
);

CREATE SEQUENCE org_id_seq
    START WITH 2
    INCREMENT BY 1
    MINVALUE 0
    MAXVALUE 2147483647
    CACHE 1;


CREATE TABLE org (
    org_i integer DEFAULT nextval(org_id_seq) NOT NULL,
    org_n varchar(255) NOT NULL,  -- name
    org_c varchar(28) NOT NULL,  -- bin/iin
	ver integer DEFAULT 0,
    s_time timestamp NOT NULL DEFAULT current_timestamp(),
    e_time timestamp,
	v_last varchar(1) DEFAULT 'y',
	status integer DEFAULT 0 NOT NULL,
    PRIMARY KEY (org_i, ver)
);

CREATE TABLE user_app (
    user_i integer NOT NULL,
    app_i integer NOT NULL,
	ver integer DEFAULT 0,
	comm varchar(150),
    s_time timestamp NOT NULL DEFAULT current_timestamp(),
    e_time timestamp,
	v_last varchar(1) DEFAULT 'y',
	status integer DEFAULT 0 NOT NULL,
	PRIMARY KEY (user_i, app_i, ver)
);

CREATE TABLE user_device (
    device_i integer NOT NULL,
    user_i integer NOT NULL,
    addr_s varchar(100) NOT NULL,
    port integer,
    r_status smallint,
	ver integer DEFAULT 0,
    s_time timestamp NOT NULL,
    e_time timestamp,
	v_last varchar(1) DEFAULT 'y',
	status integer DEFAULT 0 NOT NULL,
	PRIMARY KEY (device_i, user_i, ver)
);

CREATE TABLE user_org (
    org_i integer NOT NULL,
    user_i integer NOT NULL,
	comm varchar(150),
	ver integer DEFAULT 0,
    s_time timestamp NOT NULL DEFAULT current_timestamp(),
    e_time timestamp,
	v_last varchar(1) DEFAULT 'y',
    status integer DEFAULT 0 NOT NULL,
	PRIMARY KEY (org_i, user_i, ver)
);


CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


CREATE TABLE user_p (
    user_i integer DEFAULT nextval(user_id_seq) NOT NULL,
    u_name varchar(64) NOT NULL,
    u_ln varchar(64),
    u_tel varchar(15) NOT NULL UNIQUE,
    u_email varchar(64),
    u_cred varchar(256),
    u_tz varchar(64),
    u_st varchar(64),
    u_typ smallint,
	ver integer DEFAULT 0,
    s_time timestamp NOT NULL DEFAULT current_timestamp(),
    e_time timestamp,
	v_last varchar(1) DEFAULT 'y',
	status integer DEFAULT 0 NOT NULL,
	PRIMARY KEY (user_i, ver)
);

CREATE USER 'adm'@'localhost' IDENTIFIED BY 'Sas2016@=';
GRANT ALL PRIVILEGES ON od.* TO 'adm'@'localhost';

CREATE USER 'op'@'10.200.200.9' IDENTIFIED BY 'Oper2016@=';
GRANT SELECT, INSERT, UPDATE TO 'op'@'10.200.200.9';

FLUSH PRIVILEGES;

