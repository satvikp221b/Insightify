DELIMITER \\
create procedure sp(IN gcrn varchar(255))
BEGIN
BEGIN
    declare crn varchar(255);
    declare term varchar(255);
	declare ins_name varchar(255);
	declare ins_id int;
	declare avgScore real;
	declare avgLoad real;
	declare avgDiff real;
	declare avgRating real;
	declare numRevs int;
    declare enrollments int;
    declare diff varchar(255);

    declare loop_flag boolean default false;
    declare cur cursor for 
    (SELECT CS.CRN, CS.YearTerm, I.Instructor_name, I.ID, AVG(E.Score)as avg_score, AVG(Reviews.WorkLoad) as avg_load, AVG(Reviews.Difficulty) as avg_diff, AVG(Reviews.Rating) as avg_rating, count(DISTINCT Reviews.ReviewId) as num_revs, count(DISTINCT E.NetId) as enrollments 
    FROM CourseSchedule CS JOIN Instructors I on (CS.instructor_id=I.ID) Join Enrollments E on (CS.CRN=E.CRN and CS.YearTerm=E.Term) Join Reviews on CS.CRN=Reviews.CRN and CS.YearTerm=Reviews.Term 
    WHERE CS.CRN = gcrn
    GROUP BY CS.CRN, CS.YearTerm,I.Instructor_name,I.ID);
    
    declare continue handler for not found set loop_flag = true;
    
    drop table if exists NewTable;
    create table NewTable(
		crn VARCHAR(255),
        term VARCHAR(255),
        ins_name VARCHAR(255),
        ins_id INTEGER,
        avgScore REAL,
        avgLoad REAL,
        avgDiff REAL,
        avgRating REAL,
        numRevs INTEGER,
        enrollments INTEGER,
        diff VARCHAR(255),
        primary key(crn,term)
    );
    
    open cur;
    cloop: loop
        fetch cur into crn, term, ins_name, ins_id, avgScore, avgLoad, avgDiff, avgRating, numRevs, enrollments;
        if(loop_flag) then
        leave cloop;
        end if;
        
        if(avgDiff >= 5) then
			set diff="Very Hard";
		elseif(avgDiff >=4) then
			set diff="Hard";
		elseif(avgDiff >=3) then
			set diff="Medium";
		else
			set diff="Easy";
        end if;
        
        insert ignore into NewTable values(crn, term, ins_name, ins_id, avgScore, avgLoad, avgDiff, avgRating, numRevs, enrollments, diff);
        
    end loop cloop;
    close cur;
    select * from NewTable;

end;
BEGIN
	declare TypeVar varchar(100);
    declare CRNVar varchar(100);
    declare CountVar INT;
	declare loop_flag boolean default false;
    declare cur cursor for 
    (select Type, count(*) as COUNT
    from Assessments A JOIN Courses C ON A.CRN=C.CRN 
    where C.CRN=gcrn
	GROUP BY Type);
    
    declare continue handler for not found set loop_flag = true;
	drop table if exists NewTable1;
    create table NewTable1(
		Type VARCHAR(255),
        Count INT
        );
    
    open cur;
    cloop: loop
        fetch cur into TypeVar,CountVar;
        if(loop_flag) then
        leave cloop;
        end if;
        
        insert ignore into NewTable1 values(TypeVar,CountVar);
        
    end loop cloop;
    close cur;
    select * from NewTable1 ORDER BY count;
end;
END;\\
DELIMITER ;