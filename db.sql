create table categories (
    id integer primary key,
    name char(60) not null,
    ordering int not null
);

create table spendings (
    id integer primary key,
    amount integer not null,
    category_id integer,
    spending_date timestamp default current_timestamp not null,
    foreign key(category_id) references categories(id)
);

insert into categories (name, ordering) values
    ('бензин', 10),
    ('продукты', 20),
    ('готовая еда', 30),
    ('развлечения', 40),
    ('обучение', 50),
    ('вредные привычки', 60);
