create table budget(
    codename varchar(255) primary key,
    daily_limit integer
);

create table category(
    codename varchar(255) primary key,
    name varchar(255),
    is_base_expense boolean,
    aliases text
);

create table expense(
    id integer primary key,
    amount integer,
    created datetime,
    category_codename integer,
    raw_text text,
    FOREIGN KEY(category_codename) REFERENCES category(codename)
);

insert into category (codename, name, is_base_expense, aliases)
values
    ("products", "продукти", true, "їжф"),
    ("coffee", "напої", true, "кава, чай"),
    ("dinner", "обід", true, "їдальня, ланч, бізнес-ланч, бізнес ланч"),
    ("cafe", "кафе", true, "ресторан, рест, мак, макдональдс, МакДак, kfc, ilpatio, il patio"),
    ("transport", "заг. транспорт", false, "метро, автобус, metro"),
    ("taxi", "таксі", false, "яндекс таксі, yandex taxi"),
    ("phone", "телефон", false, "теле2, связь"),
    ("books", "книги", false, "література, літ-ра"),
    ("internet", "інтернет", false, "інет, inet"),
    ("subscriptions", "підписки", false, "підписка"),
    ("other", "іньше", true, "");

insert into budget(codename, daily_limit) values ('base', 250);