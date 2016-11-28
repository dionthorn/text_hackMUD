1. For everything to function you must first check the schema.sql file to see if it is formatting the database correctly.

2. Next you must check the setup_database.py file and ensure it's creating the admin account with the info you want and you can use the test account as well. a database.db file will be created. ex_database.db is a default database to be used for the tutorial.
	Note: you can use output_database.py to get all the values of the database

3. Run game_server.py and chat_server.py these both pull info out of the database.py file.

4. Use the game_client.py or chat_client.py and either register or login.