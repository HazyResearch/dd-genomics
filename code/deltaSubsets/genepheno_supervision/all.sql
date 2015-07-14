create table genepheno_old_relations_of_interest as
  (select
    r.*
   from
    genepheno_relations_snapshot r);
create table genepheno_new_relations_of_interest as
  (select
    r.*
   from
    genepheno_relations r);
