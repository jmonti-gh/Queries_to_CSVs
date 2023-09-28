# Queries_a_CSVs
- Small project to write DB's queries to CSVs files

In a sector of the Company where I work, it was necessary to generate several csv files from queries to different DBs.
These csvs must be hosted in different directories and serve as input for a data analysis process.
Since in this sector they usually handle information in .xlsx files, I proposed that within a .xlsx they generate a 
list of the csv they require with all the necessary data to generate and build these csv according to the following format:


And I was going to generate a script in python that read line by line that .xlsx, 
called CSVs_list.xlsx, and complete the queries and writings to csv indicated there.

I built the solution in two different versions. The procedural version and the OOP.
The OOP version is more complete in terms of summary of results.
Both versions are premised on processing all the tasks indicated in the input .xlsx, 
and not stop for mistakes, just record them for each case. But complete the whole input CSVs_list.xls file


