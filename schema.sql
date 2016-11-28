create table reg_users (
    uuid        INTEGER PRIMARY KEY AUTOINCREMENT,
    username    text unique not null,
    password    text not null,
    creation    date not null
);

create table user_info (
    uuid        INTEGER PRIMARY KEY AUTOINCREMENT,
    uipa        text unique not null,
    ucre        int not null,
    ucpu        int not null,
    uram        int not null,
    uhdd        int not null,
    ussd        int not null,
    unet        int not null,
    ulog        text not null
);
