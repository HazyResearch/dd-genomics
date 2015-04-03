--
-- Name: array_accum(anyelement); Type: AGGREGATE; Schema: public; Owner: senwu
--

-- NOTE: need to change owner name below...
CREATE AGGREGATE array_accum(anyelement) (
    SFUNC = array_append,
    STYPE = anyarray,
    INITCOND = '{}'
);

ALTER AGGREGATE public.array_accum(anyelement) OWNER TO senwu;
