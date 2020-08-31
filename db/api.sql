CREATE SCHEMA IF NOT EXISTS api;

CREATE TYPE api.enum_spending_cols AS ENUM ('date', 'amount', 'currency');

--
CREATE OR REPLACE FUNCTION api.fun_add_spending(a_amount bigint, a_currency int, a_reason varchar, a_date bigint,
                                                _id OUT bigint)
  RETURNS bigint
  LANGUAGE plpgsql AS
$fun$
BEGIN
  ASSERT (a_amount NOTNULL AND a_currency NOTNULL AND a_date NOTNULL);
  IF a_date > extract(EPOCH FROM now()) + 1 THEN
    RAISE SQLSTATE 'R0001'; -- Invalid time
  ELSEIF ((SELECT pkey_id FROM tbl.currency WHERE pkey_id = a_currency_id) ISNULL) THEN
    RAISE SQLSTATE 'R0003'; -- Invalid currency code
  END IF;
  INSERT INTO tbl.spending(amount, fkey_currency, reason, date)
  VALUES (a_amount, a_currency, a_reason, a_date)
  RETURNING pkey_id INTO STRICT _id;
END
$fun$;

CREATE OR REPLACE FUNCTION api.fun_delete_spending(a_spending_id bigint)
  RETURNS void
  LANGUAGE plpgsql AS
$fun$
BEGIN
  ASSERT (a_spending_id NOTNULL);
  IF ((SELECT pkey_id FROM tbl.spending WHERE pkey_id = a_spending_id) ISNULL) THEN
    RAISE SQLSTATE 'R0002'; -- Spending doesn't exist
  END IF;
  DELETE FROM tbl.spending WHERE pkey_id = a_spending_id;
END
$fun$;

CREATE OR REPLACE FUNCTION api.fun_update_spending(a_spending_id bigint, a_amount bigint, a_currency_id int,
                                                   a_reason varchar, a_date bigint)
  RETURNS void
  LANGUAGE plpgsql AS
$fun$
BEGIN
  ASSERT (a_spending_id NOTNULL);
  IF a_date > extract(EPOCH FROM now()) + 1 THEN
    RAISE SQLSTATE 'R0001'; -- Invalid time
  ELSEIF ((SELECT pkey_id FROM tbl.spending WHERE pkey_id = a_spending_id) ISNULL) THEN
    RAISE SQLSTATE 'R0002'; -- Spending doesn't exist
  ELSEIF ((SELECT pkey_id FROM tbl.currency WHERE pkey_id = a_currency_id) ISNULL) THEN
    RAISE SQLSTATE 'R0003'; -- Invalid currency code
  END IF;
  UPDATE tbl.spending
  SET amount        = a_amount,
      fkey_currency = a_currency_id,
      reason        = a_reason,
      date          = a_date
  WHERE pkey_id = a_spending_id;
END
$fun$;

CREATE OR REPLACE FUNCTION api.fun_get_all_spendings(a_order_col api.enum_spending_cols DEFAULT 'date')
  RETURNS table
          (
            "spendingId"   bigint,
            "amount"       bigint,
            "currencyCode" varchar,
            "reason"       varchar,
            "date"         bigint
          )
  LANGUAGE plpgsql
AS
$fun$
BEGIN
  RETURN QUERY SELECT sp.pkey_id,
                      sp.amount,
                      cur.code,
                      sp.reason,
                      sp.date::bigint
               FROM tbl.spending sp
                      JOIN tbl.currency cur
                           ON sp.fkey_currency = cur.pkey_id
               ORDER BY CASE a_order_col WHEN 'date' THEN sp.date END DESC,
                        CASE a_order_col WHEN 'amount' THEN sp.amount END DESC,
                        CASE a_order_col WHEN 'currency' THEN cur.code END ASC;
END;
$fun$;

CREATE OR REPLACE FUNCTION api.fun_get_spending_by_currency(a_currency_id int,
                                                            a_order_col api.enum_spending_cols DEFAULT 'date')
  RETURNS table
          (
            "spendingId" bigint,
            "amount"     bigint,
            "reason"     varchar,
            "date"       bigint
          )
  LANGUAGE plpgsql
AS
$fun$
BEGIN
  IF ((SELECT pkey_id FROM tbl.currency WHERE pkey_id = a_currency_id) ISNULL) THEN
    RAISE SQLSTATE 'R0003'; -- Invalid currency code
  END IF;
  RETURN QUERY SELECT sp.pkey_id,
                      sp.amount,
                      sp.reason,
                      sp.date::bigint
               FROM tbl.spending sp
                      JOIN tbl.currency cur
                           ON sp.fkey_currency = cur.pkey_id
               WHERE cur.pkey_id = a_currency_id::smallint
               ORDER BY CASE a_order_col WHEN 'date' THEN sp.date END DESC,
                        CASE a_order_col WHEN 'amount' THEN sp.amount END DESC,
                        CASE a_order_col WHEN 'currency' THEN cur.code END ASC;
END
$fun$;
