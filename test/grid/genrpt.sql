/*
genrpt.sql

Usage:
    sqlite3 restart-all.db < genrpt.sql

Output:
    siminfo.csv: simulation information
    chkpnt.csv:  checkpoint simulation times
    restart.csv: restart simulation times

Keys:
    simid
*/

.mode csv
.headers on
.output chkpnt.csv
select * from chkpnt t1 join siminfo t2 on t1.simid=t2.id;
.output restart.csv
select * from restart t1 join siminfo t2 on t1.simid=t2.id;
.output siminfo.csv
select * from siminfo;
.quit

