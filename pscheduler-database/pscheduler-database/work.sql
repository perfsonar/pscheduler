--
-- File for doing tests.
--

-- TODO: Remove this file from the sources when development is complete.

\c pscheduler

select boot();

DELETE FROM task;
DELETE FROM run;

SELECT * FROM api_task_post( $$
{
    "schema": 1,

    "test": {
	"type": "idle",
	"spec": {
	    "schema": 1,
	    "duration": "PT5S",
 	    "starting-comment": "Starting to sleep.",
	    "parting-comment": "Done sleeping."
	}
    },

    "tool": "sleep",

    "schedule": {
	"repeat": "PT10S",
	"max_runs": 50
    },


    "archives": [
        { "name": "bitbucket", "data": {} },
        { "name": "failer",    "data": {} }
    ]

}
$$, 0);


CREATE OR REPLACE FUNCTION junk()
RETURNS VOID
AS $$
DECLARE
    task RECORD;
    proposal RECORD;
    new_run UUID;
BEGIN

    SELECT INTO task * FROM task LIMIT 1;

    SELECT INTO proposal * FROM api_proposed_times(task.uuid) LIMIT 1;
    RAISE NOTICE 'Proposed % to %', proposal.lower, proposal.upper;

    proposal.lower := proposal.lower; -- + 'PT2H'::INTERVAL;
    RAISE NOTICE 'Scheduling at %', proposal.lower;
    new_run := api_run_post(task.uuid, proposal.lower);

END;
$$ LANGUAGE plpgsql; 

select junk();
select junk();
select junk();
select junk();
select junk();
select junk();

SELECT * FROM run;

DROP FUNCTION junk();


-- SELECT array_to_json(array_agg(apt.*))
-- FROM  api_propose_times(
--     (SELECT uuid FROM task),
--     '2016-02-10T00:00:00'::TIMESTAMP WITH TIME ZONE,
--     '2016-02-10T00:01:00'::TIMESTAMP WITH TIME ZONE
-- ) apt;


-- select api_tools_for_test($$
-- {
-- 	"type": "idle",
-- 	"spec": {
-- 	    "schema": 1,
--             "duration": "PT5S",
-- 	    "starting-comment": "Beginning to do nothing.",
-- 	    "parting-comment": "Done a whole lot of nothing."
-- 	}
-- }
-- $$);












-- \x on
-- -- select * from task;
-- \x off
-- 
-- 
-- --select * from run ORDER BY times;
-- 
-- --select count(*) from run;
-- --select run, start_in from schedule_upcoming LIMIT 10;
