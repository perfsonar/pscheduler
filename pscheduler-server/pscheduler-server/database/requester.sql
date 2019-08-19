--
-- Support for requester proxying
--


DO $$
BEGIN
    IF NOT EXISTS (SELECT * FROM auth_key_type WHERE NAME = 'requester')
    THEN
        INSERT INTO auth_key_type (name) VALUES ('requester');
    END IF;
END;
$$ LANGUAGE plpgsql;
