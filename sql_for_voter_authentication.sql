create database electionAutomation;
use electionAutomation;
create table voter(
	voterId varchar(9) primary key,
    voterName varchar(200),
    dob date,
    fatherName varchar(200),
    gender char,
    photoSet longblob
);

create table address(
	voterId varchar(9) primary key,
    door varchar(50),
    street varchar(50),
    area varchar(50),
    landmark varchar(50),
    city varchar(50),
    district varchar(50),
    state varchar(50),
    pin varchar(7),
    phone varchar(13),
    foreign key (voterId) references voter(voterId)
);

create table voteStatus(
	voterId varchar(9) primary key,
    electionDate date,
    voteStatus bool,
    foreign key (voterId) references voter(voterId)
);