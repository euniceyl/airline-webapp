# airline-webapp

A full stack data-backed web app development project based on a given data set about air travel. This app provides functionality so that the user can
(if they have the appropriate authority for that activity): view all the airports known to the database, search up an airport by entering the AirportID, add a new airport to the database, update other fields for a particular airport, remove an airport that is in the database, and display a summary showing the various countries alongside with the number of airports that are located in that country. To protect against unauthorized access, this app enables differential roles between end users and admin users, such that end users only have viewing access to airport data, while admin users can also modify (add, update, delete) it and contains protection codes against SQL injections. Furthermore, the code implements pagination and drop-down extension features using Flask. I used HTML (front-end) and Python (back-end) were used to develop this web app, given a SQL relational schema.

Coursework from University of Sydney ISYS 2120: Data and Information Management.
