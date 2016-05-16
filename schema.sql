drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  qr text not null,
  name text not null,
  lang text not null,
  place text,
  memo text,
  start text not null,
  goal text
);