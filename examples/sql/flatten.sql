drop table if exists alldata;
drop table if exists base;
drop table if exists cpt;
drop table if exists rst;

--- flatten data into single table
create temp table tmp1 as select * from job_info t1 left join file_info t2   on t1.jobid=t2.jobid;
create temp table tmp2 as select * from tmp1 t1     left join timing_info t2 on t1.jobid=t2.jobid;
create temp table tmp3 as select * from tmp2 t1     left join conf_info t2   on t1.jobid=t2.jobid;
create temp table tmp4 as select * from tmp3 t1     left join slurm_info t2  on t1.jobid=t2.jobid;

create table alldata as select * from tmp4;

drop table tmp1;
drop table tmp2;
drop table tmp3;
drop table tmp4;

-- breakout base, cpt, and rst into individual tables
create table base as select * from alldata where jobtype="BASE";
create table cpt as  select * from alldata where jobtype="CPT";
create table rst as  select * from alldata where jobtype="RST";

-- base, cpt, rst comparisons
create temp table tmpbase as select 
    jobid as base_jobid, 
    jobtype as base_jobtype,
    jobname as base_jobname,
    ranks, threads, slurm, nodeclamp,
    clockFreq, clocks, comp_name, comp_type, components, links, maxData, maxDelay, minData, minDelay, numBytes, numPorts,
    disk_usage as base_disk_usage, 
    global_max_rss as base_global_max_rss, 
    global_max_sync_data_size as base_global_max_sync_data_size, 
    global_mempool_size as base_global_mempool_size,
    local_max_rss as base_local_max_rss,
    max_build_time as base_max_build_time,
    max_mempool_size as base_max_mempool_size,
    max_run_time as base_max_run_time,
    max_total_time as base_max_total_time,
    jobstring as base_jobstring
    from base;
create temp table tmpcpt as select 
    jobid as cpt_jobid,
    friend as cpt_friend, 
    jobtype as cpt_jobtype,
    checkpoint_sim_period, checkpoint_wall_period, 
    cpt_bin, cpt_bin_size_ave, cpt_bin_size_max, cpt_bin_size_min, cpt_bin_size_total, cpt_dirs,
    disk_usage as cpt_disk_usage, 
    global_max_rss as cpt_global_max_rss, 
    global_max_sync_data_size as cpt_global_max_sync_data_size, 
    global_mempool_size as cpt_global_mempool_size,
    local_max_rss as cpt_local_max_rss,
    max_build_time as cpt_max_build_time,
    max_mempool_size as cpt_max_mempool_size,
    max_run_time as cpt_max_run_time,
    max_total_time as cpt_max_total_time,
    jobstring as cpt_jobstring
    from cpt;

create temp table tmprst as select
    jobid as rst_jobid,
    friend as rst_friend, 
    jobtype as rst_jobtype,
    cpt_num, cpt_timestamp,
    max_run_time as rst_max_run_time,
    max_total_time as rst_max_total_time,
    jobstring as rst_jobstring
    from rst;

drop table if exists basecpt;
drop table if exists cptrst;
create table basecpt as select * from tmpbase t1 left join tmpcpt t2 where t1.base_jobid=t2.cpt_friend;
create table cptrst  as select * from tmprst t1  left join tmpcpt t2 where t1.rst_friend=t2.cpt_jobid;

drop table tmpbase;
drop table tmpcpt;
drop table tmprst;

-- some final calculations
alter table basecpt add column delta_runtime;
alter table basecpt add column percent_delta_runtime;
alter table basecpt add column procs;
alter table basecpt add column links_per_proc;
alter table basecpt add column comps_per_proc;
alter table basecpt add column links_per_comp;

update basecpt set delta_runtime = cpt_max_run_time - base_max_run_time;
update basecpt set percent_delta_runtime = 100 * ( delta_runtime / base_max_run_time );
update basecpt set procs = ranks * threads;
update basecpt set links_per_proc = links / ranks;
update basecpt set comps_per_proc = components / ranks;
update basecpt set links_per_comp = links / components;

.headers on

.mode csv
.output alldata.csv
select * from alldata;
.output base.csv
select * from base;
.output cpt.csv
select * from cpt;
.output rst.csv
select * from rst;
.output basecpt.csv
select * from basecpt;
.output cptrst.csv
select * from cptrst;

.quit
