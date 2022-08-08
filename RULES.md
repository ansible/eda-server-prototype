

Ben's rules for writing performant database applications

These are lessons that I have learned over a decade of writing Django and other
Python web applications dealing with large amounts of data.  They might be
unusual and controversial, so that's why I am wrote them down here.  They are
not rules that we must follow in this project.  They are a guide for if and
when we need to scale to large amounts of data or have fast database
operations.

1. Think in sets and do bulk operations.  A single entry is a set of one.   The
   cost of a single insert or update is similar to the cost of a bulk insert or
   update since most of the cost of database writes are updating indicies.

2. Know what SQL statement that you want to send to the database first.  Use
   tools to generate that SQL second. ORMs generate really slow SQL unless you
   are very careful and know what you are doing.

3. Don't override the save function.  This prevents #1.  Don't use most of ORM
   features since they conflict with #1.

4. Get the data into the database as fast as possible without processing it.
   Don't leave the user waiting for processing before responding that you
   recevied the data.  Receive and write the data quickly and then process
   it later.   Make separate tables for incoming data and processed data.
   Don't add indicies to incoming data tables.   Provide and API or event
   that lets them know that the data has been processed.

5. Process the data in the database.  The database manipulates data many times
   faster and scales better than Python applications.  Create and temporary
   tables if needed and drop them when you are done with the operations.

6. Create reporting tables. If you need to generate reports, create another set
   of paritioned tables for those reports and ONLY do read, bulk inserts, and
   drop table partition operations on them.  Don't report out of the relational
   tables since it will be way too slow.

7. Write correct queries first and optimize them second if needed.  Some queries
   will be slow due to the structure of the relational data.  This can be fixed
   by reorganizing the data into reporting tables.  Optimizing can take much longer
   than writing the slow correct query and you'll need the slow query anyway to know
   that your optimized query is correct.  Besides it is fun to get 10x and 100x speed-ups.
