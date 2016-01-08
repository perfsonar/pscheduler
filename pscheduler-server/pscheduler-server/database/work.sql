--
-- File for doing tests.
--

-- TODO: Remove this file from the sources when development is complete.

select boot();
--select id, name, description, version, updated, available from tool;
--select * from tool_test;


SELECT * FROM api_task_add( $$
{
    "schema": 1,
    "schedule": {
	"duration": "PT5S",
	"repeat": "PT10S",
	"max_runs": 100
    },

    "test": {
	"type": "idle",
	"spec": {
	    "schema": 1,
 	    "starting_comment": "Starting to sleep.",
	    "parting_comment": "Done sleeping."
	}
    }
}

$$, 'sleep', 0 );





\x on
-- select * from task;
\x off


--select * from run ORDER BY times;

--select count(*) from run;
--select run, start_in from schedule_upcoming LIMIT 10;

