# inFocus_BIOME_protobuf_parser
For parsing the inFocus BIOMEs in iOS 16 and above and combining them with knowlegeC.db for analysis

# THIS SCRIPT WILL EXECUTE THE QUEIRIES BELOW TO PARSE OUT DATA FOR THE SELECTED APPLICATION.
# APPLICATION: inFocus BIOME parser (as of 2023-04-03)
# DATABASES REQUIRED: inFocus Apple BIOM files (and OPTIONAL: knowledgeC.db)
#
#       /private/var/db/biome/streams/restricted/_DKEvent.App.inFocus/local

This works by looking for any file with "SEGB" in the first 256 bytes then looking in those files for the "/app/inFocus".  From there it parses and decodes based on where it finds the that string it produces a SQLite database with the results including the file and decimal offset the parsing started from for each record.  It saves these in the SQLite database and a TSV file.  It gives the option to import data from the knowledteC ZOBJECT table which is decided to make it useful for analysis.  It keeps a log file of the querys used and all the files and locatiosn the data was parsed from for later court purposes if needed.  
