
-- CREATE FUNCTION public.addtexto(blkhash character varying, texto character varying) RETURNS integer
--    LANGUAGE plpgsql
--    AS $$
--BEGIN
--	INSERT INTO texto (idbloque,texto) VALUES (blkhash,texto);
--	UPDATE bloque SET apariciones=apariciones+1 WHERE hash=blkhash;
--    commit;
--    return 0;
--end
--$$;


--ALTER FUNCTION public.addtexto(blkhash character varying, texto character varying) OWNER TO captcha;

--
-- Name: getbloques(integer, integer, integer); Type: FUNCTION; Schema: public; Owner: captcha
--

--CREATE FUNCTION public.getbloques(hoja integer, idx integer, nblock integer) RETURNS TABLE(hash character varying, i0 integer, j0 integer, i1 integer, j1 integer)
--    LANGUAGE sql
--    AS $$ 	
--	SELECT hash,i0,j0,i1,j1
--    FROM bloque 
--    where (i0,idhoja) in (select i0,idhoja
--                            from bloque 
--                            where idhoja=hoja and indice=idx)
--     AND indice >=idx-nBlock and indice <=idx+nBlock;
-- $$;

--ALTER FUNCTION public.getbloques(hoja integer, idx integer, nblock integer) OWNER TO captcha;


-- CREATE FUNCTION public.urldecode_arr(url text) RETURNS text
--     LANGUAGE plpgsql IMMUTABLE STRICT
--     AS $_$
-- DECLARE ret text;
-- BEGIN
--  BEGIN
--     WITH STR AS (
--       SELECT
--       -- array with all non encoded parts, prepend with '' when the string start is encoded
--       case when $1 ~ '^%[0-9a-fA-F][0-9a-fA-F]' 
--            then array[''] 
--            end 
--       || regexp_split_to_array ($1,'(%[0-9a-fA-F][0-9a-fA-F])+', 'i') plain,
--       -- array with all encoded parts
--       array(select (regexp_matches ($1,'((?:%[0-9a-fA-F][0-9a-fA-F])+)', 'gi'))[1]) encoded
--     )
--     SELECT  string_agg(plain[i] || coalesce( convert_from(decode(replace(encoded[i], '%',''), 'hex'), 'utf8'),''),'')
--     FROM STR, 
--       (SELECT  generate_series(1, array_upper(encoded,1)+2) i FROM STR)blah
--     INTO ret;
--   EXCEPTION WHEN OTHERS THEN  
--     raise notice 'failed: %',url;
--     return $1;
--   END;   
--   RETURN coalesce(ret,$1); -- when the string has no encoding;
-- END;
-- $_$;
------------------------------------------------------------------------------

--CREATE DATABASE microfilm;

------------------------------------------------------------------------------

CREATE TABLE bloque (
    id integer PRIMARY KEY,
    idhoja integer,
    fila integer NOT NULL,
    indice integer NOT NULL,
    i0 integer NOT NULL,
    j0 integer NOT NULL,
    i1 integer NOT NULL,
    j1 integer NOT NULL,
    hash character varying(64),
    apariciones integer DEFAULT 0 NOT NULL
);

------------------------------------------------------------------------------

CREATE TABLE texto (
    id integer PRIMARY KEY NOT NULL,
    idbloque character varying(64),
    texto character varying(256)
);

------------------------------------------------------------------------------

CREATE TABLE hoja (
    id integer PRIMARY KEY NOT NULL,
    numero integer NOT NULL,
    idrollo integer NOT NULL,
    path character varying(1024) NOT NULL,
    hash character varying(64),
    apariciones integer DEFAULT 0 NOT NULL
);

------------------------------------------------------------------------------

CREATE TABLE rollo (
    id integer PRIMARY KEY NOT NULL,
    numero integer,
    anio integer,
    path character varying(1024)
);

------------------------------------------------------------------------------
