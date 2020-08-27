-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2020-08-26 14:52:18.67

-- sequences
-- Sequence: seq_spending_id
CREATE SEQUENCE tbl.seq_currency_id
      NO MINVALUE
      NO MAXVALUE
      NO CYCLE
;

CREATE SEQUENCE tbl.seq_spending_id
      NO MINVALUE
      NO MAXVALUE
      NO CYCLE
;

-- tables
-- Table: currency
CREATE TABLE tbl.currency (
    pkey_id smallint  NOT NULL DEFAULT nextval('tbl.seq_currency_id'),
    currency varchar(256)  NOT NULL,
    code varchar(3)  NOT NULL,
    CONSTRAINT currency_pk PRIMARY KEY (pkey_id)
);

CREATE UNIQUE INDEX uidx_currency_id on tbl.currency (pkey_id ASC);

CREATE UNIQUE INDEX uidx_currency_code on tbl.currency (code ASC);

-- Table: spending
CREATE TABLE tbl.spending (
    pkey_id bigint  NOT NULL DEFAULT nextval('tbl.seq_spending_id'),
    amount bigint  NOT NULL,
    fkey_currency smallint  NOT NULL,
    reason varchar(2048)  NULL,
    date oid  NOT NULL,
    timestamp oid  NOT NULL DEFAULT EXTRACT(EPOCH FROM (NOW()))::bigint,
    CONSTRAINT spending_pk PRIMARY KEY (pkey_id)
);

CREATE UNIQUE INDEX uidx_spending_id on tbl.spending (pkey_id ASC);

-- foreign keys
-- Reference: spending_currency (table: spending)
ALTER TABLE tbl.spending ADD CONSTRAINT spending_currency
    FOREIGN KEY (fkey_currency)
    REFERENCES tbl.currency (pkey_id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- End of file.

