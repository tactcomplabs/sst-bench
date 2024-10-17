create temp table cptsizes as select * from restart t1 join chkpnt t2 on t1.simid=t2.simid;
create temp table rpt as select simid, size/1000 as kb, basetime, cpttime, (cpttime-basetime) as delta,  simtime as rsttime from cptsizes;

.mode csv
.headers on
select * from siminfo limit 1;
select * from rpt;
.output siminfo.csv
select * from siminfo limit 1;
.output cptsizes.csv
select * from rpt;

.quit
