drop database if exists feedback_db;
create database if not exists feedback_db;
use feedback_db;


create table category(
    c_category varchar(255) primary key
);

create table feedback(
    f_id int auto_increment primary key,
    f_input_text mediumtext,
    f_c_predicted_category varchar(255),
    f_c_feedback_category varchar(255),

    foreign key(f_c_predicted_category) references category(c_category),
    foreign key(f_c_feedback_category) references category(c_category)
);

create table feedback_for_finetune(
    f_predictionid int primary key,
    f_input_text mediumtext,
    f_c_predicted_category varchar(255),
    f_c_feedback_category varchar(255),

    foreign key(f_c_predicted_category) references category(c_category),
    foreign key(f_c_feedback_category) references category(c_category),
    foreign key (f_predictionid) references feedback(f_id)
);

create table finetune_logs(
    fl_id int auto_increment primary key,
    timestamp TIMESTAMP
);

insert into category(c_category) values ("Books"),("Electronics"),("Household"),("Clothing & Accessories");