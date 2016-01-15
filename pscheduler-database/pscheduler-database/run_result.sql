--
-- Table of Run Results
--


DROP TABLE IF EXISTS run_result CASCADE;
CREATE TABLE run_result (

	-- Row identifier
	id		SERIAL
			PRIMARY KEY,

	-- Run that produced this result
	run    	    	INTEGER
			REFERENCES run(id)
			ON DELETE CASCADE,

	-- What participant produced the result
	-- TODO: This must be within the range of participants for the task.
	participant	INTEGER
			NOT NULL,

	-- Result produced
	result		TEXT,

	-- Error messages
	errors		TEXT,


	-- No duplicate results per run allowed.
	UNIQUE (run, participant)
);



-- TODO: View: Runs needing results to be retrieved


-- TODO: View: Runs with all results retrieved
