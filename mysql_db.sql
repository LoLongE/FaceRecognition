create database test;

use test;

create table student(
	stu_id varchar(20) NOT Null,
	stu_name varchar(20) NOT NUll,
	email varchar(20) ,
	tel varchar(20) ,
    dept varchar(20) ,
    grade int ,
    primary key (stu_id)
)ENGINE = InnoDB;

create table professor(
	prof_id varchar(20) Not Null,
    prof_name varchar(20),
    email varchar(20) ,
	tel varchar(20) ,
    dept varchar(20) ,
    primary key (prof_id)
)ENGINE = InnoDB;

create table course(
	course_id varchar(20),
	course_name varchar(20),
    credit int,
    prof_id varchar(20),
    primary key (course_id),
    foreign key (prof_id) references professor(prof_id) 
)ENGINE = InnoDB;

create table enroll(
	enroll_id varchar(20),
    course_id varchar(20),
    stu_id varchar(20),
    primary key (enroll_id),
    foreign key (course_id) references course(course_id),
    foreign key (stu_id) references student(stu_id)
    
)ENGINE = InnoDB;

create table attend(
	enroll_id varchar(20),
    enter_time varchar(20),
    enter_date varchar(20),
    ischeck varchar(10),
	foreign key (enroll_id) references enroll(enroll_id)
    
)ENGINE = InnoDB;



show tables;

insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20080001','Gilson','gilson@naver.com','010-6541-8628','Comp',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20090001','Nodong','ndh0506@gmail.com','010-5321-6788','Comp',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20100001','Hongik','hongik12@naver.com','010-4123-1456','Teeth',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20110001','Zerofive','zerofive05@naver.com','010-0505-7580','Comp',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20110002','byeongsang','byeongsang@naver.com','010-6789-4321','Envi',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20120001','Gwang','gwang11@naver.com','010-1234-5678','Comp',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20120002','Junho','junho11@naver.com','010-9876-0678','Comp',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20120003','yochan','yochan@naver.com','010-2222-1111','Elec',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20130001','Namhoon','namhun21@naver.com','010-9460-9790','Ict',4);
insert into student(stu_id, stu_name, email,tel,dept,grade ) VALUES('20130002','Jaehyun','jaehyun@naver.com','010-6543-2313','Comp',4);

select * from student;

insert into professor(prof_id, prof_name, email,tel,dept) VALUES('prof_1','Kiju','Ict','kiju@naver.com','010-1111-2222');
insert into professor(prof_id, prof_name, email,tel,dept) VALUES('prof_2','Woongsup','Comp','woongsup@naver.com','010-4444-5555');
insert into professor(prof_id, prof_name, email,tel,dept) VALUES('prof_3','Donald','Ict','donald@naver.com','010-3333-5555');
select * from professor;

insert into course(course_id, course_name, credit, prof_id) VALUES('cor_1','Data structure',3,'prof_1');
insert into course(course_id, course_name, credit, prof_id) VALUES('cor_2','Algorithm',3,'prof_2');
insert into course(course_id, course_name, credit, prof_id) VALUES('cor_3','Embedded',3,'prof_3');
insert into course(course_id, course_name, credit, prof_id) VALUES('cor_4','Android programming',3,'prof_1');
insert into course(course_id, course_name, credit, prof_id) VALUES('cor_5','Software engineering',3,'prof_2');

select * from course;

insert into enroll(enroll_id, course_id, stu_id) VALUES('en_1','cor_1','20090001');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_2','cor_1','20100001');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_3','cor_1','20120001');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_4','cor_1','20130001');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_5','cor_2','20090001');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_6','cor_2','20100001');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_7','cor_2','20120001');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_8','cor_2','20130001');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_9','cor_1','20120002');
insert into enroll(enroll_id, course_id, stu_id) VALUES('en_10','cor_1','20110001');

select * from enroll;

select * from attend;

select stu_name 
from student
where student.stu_id = (select enroll.stu_id 
						from enroll, attend 
						where enroll.enroll_id = attend.enroll_id and attend.ischeck = 'late');