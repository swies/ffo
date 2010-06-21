create database ffo default character set = 'utf8';
use ffo;

create table users (
    id int auto_increment primary key,
    lower_name varchar(250) unique,
    password varchar(250),
    display_name varchar(250),
    claimed_at datetime,
    claimed_by_ip varchar(15)
) engine='innoDB', character set = 'utf8';

create table posts (
    id int auto_increment primary key,
    linkhash varchar(250),
    author varchar(250),
    title text,
    link text,
    summary text,
    tags text,
    posted_at datetime,
    checks integer default 0,
    comments integer default 0,
    key (linkhash)
) engine='innoDB', character set = 'utf8';

create table comments (
    id int auto_increment primary key,
    post_id integer,
    user_id integer,
    comment text,
    created_at datetime,
    key (post_id),
    foreign key (post_id) references posts(id),
    foreign key (user_id) references users(id)
) engine='innoDB', character set = 'utf8';

create table checks (
    post_id integer,
    user_id integer,
    created_at datetime,
    primary key (post_id, user_id),
    foreign key (post_id) references posts(id),
    foreign key (user_id) references users(id)
) engine='innoDB', character set = 'utf8';
