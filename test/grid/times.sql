/*
times.sql

Usage:
    sqlite3 restart-all.db < times.sql

Output:
    siminfo.csv:   simulation information
    times.csv:     collected simulation times
    fulltimes.csv: times with simulation parameters and component count

Keys:
    simid
*/


CREATE TEMP TABLE times(simid, name, time, kb);
INSERT INTO times SELECT simid, "base", basetime, 0 FROM chkpnt;
INSERT INTO times SELECT simid, "cpt", cpttime, 0 FROM chkpnt;

CREATE TEMP TABLE rst(simid, cptnum, simtime, size);
INSERT INTO rst SELECT simid, SUBSTR(cptname,1,INSTR(cptname,'_')-1) as cptnum, simtime, size FROM restart order by CAST(cptnum as INTEGER);

INSERT INTO times SELECT simid, "rst"||cptnum, simtime, size/1000 FROM rst;

CREATE TEMP TABLE fulltimes AS SELECT * FROM times t1 JOIN siminfo t2 ON t1.simid = t2.id;
ALTER TABLE fulltimes ADD COLUMN comps;
UPDATE fulltimes SET comps=x+y;


.headers on
.mode csv
.output siminfo.csv
SELECT * FROM siminfo;
.output times.csv
SELECT * FROM times;
.output fulltimes.csv
SELECT * FROM fulltimes;

.quit

