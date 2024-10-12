CREATE TEMP TABLE times(name, time, kb);
INSERT INTO times SELECT "base", basetime, 0 FROM chkpnt;
INSERT INTO times SELECT "cpt", cpttime, 0 FROM chkpnt;

CREATE TEMP TABLE rst(cptnum, simtime, size);
INSERT INTO rst SELECT SUBSTR(cptname,1,INSTR(cptname,'_')-1) as cptnum, simtime, size FROM restart order by CAST(cptnum as INTEGER);

INSERT INTO times SELECT "rst"||cptnum, simtime, size/1000 FROM rst;

.headers on
SELECT * FROM siminfo;
SELECT * FROM times;

.mode csv
.output siminfo.csv
SELECT * FROM siminfo;
.output times.csv
SELECT * FROM times;

.quit

