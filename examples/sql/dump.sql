.tables
.headers on
.mode csv

.output job_info.csv
select * from job_info;

.output conf_info.csv
select * from conf_info;

.output file_info.csv
select * from file_info;

.output timing_info.csv
select * from timing_info;

.output slurm_info.csv
select * from slurm_info;

.quit



