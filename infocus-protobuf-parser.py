# THIS SCRIPT WILL EXECUTE THE QUEIRIES BELOW TO PARSE OUT DATA FOR THE SELECTED APPLICATION.
# APPLICATION: inFocus BIOME parser (as of 2023-04-03)
# DATABASES REQUIRED: inFocus Apple BIOM files (and OPTIONAL: knowledgeC.db)
#
#       /private/var/db/biome/streams/restricted/_DKEvent.App.inFocus/local
#           
#
# Version 1.0
# Date  2023-04-03
# Copyright (C) 2023 - Aaron Dee Roberts
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can view the GNU General Public License at <http://www.gnu.org/licenses/>
#

import sys
import os
import datetime
import re
import struct # for date decode
import sqlite3


#FOR MAKING BYTE ARRAY STRING OUT OF HEX STRING IF NEEDED.
def hex_format(hex_string): 
    sep_count = 0
    sh_str = ""
    sep_dic = []
    while sep_count < len(separator):
        sep_dic.append(hex_string[sep_count:sep_count + 2])  # Separate the separator bytes into a dictionary
        sep_count += 2  # to allow for additions needed for byte array

    for sep_loop in sep_dic:
        sh_str = sh_str + '\\x' + sep_loop
        # print(sh_str)
    return sh_str

# FOR DECODING THE PACKED BYTE WITH 5/3 DIVISION.  
def byte_5_3_decode(hex_offset):

    bits = bin(int(hex_offset.hex(),16))[2:].zfill(8)
    #print(f'Bits: {bits}')
    lbit = bits[0:5]
    rbit = bits[5:8]
    
    #DEFINE THE VALUES FOR THE BITS
    lbit_v_dic = {1:16, 2:8, 3:4, 4:2, 5:1}
    rbit_v_dic = {1:4, 2:2, 3:1}
    
    # ASSIGN THE PIECES OF THE BIT STRING
    lbit_dic = {}
    lbit_dic[1] = int(lbit[0:1])
    lbit_dic[2] = int(lbit[1:2])
    lbit_dic[3] = int(lbit[2:3])
    lbit_dic[4] = int(lbit[3:4])
    lbit_dic[5] = int(lbit[4:5])
    rbit_dic = {}
    rbit_dic[1] = int(rbit[0:1])
    rbit_dic[2] = int(rbit[1:2])
    rbit_dic[3] = int(rbit[2:3])

    
    v_count = 1
    lt_count = 0
    rt_count = 0
    
    for l_val in lbit_dic.items():
        key_v = lbit_dic[v_count]
        if key_v == 1:
            lt_count = lt_count + lbit_v_dic[v_count]

        v_count += 1
    
    v_count = 1 # Set it back to 1 for the left side.
    
    for r_val in rbit_dic.items():
        key_v = rbit_dic[v_count]
        if key_v == 1:
            rt_count = rt_count + rbit_v_dic[v_count]
            
        v_count += 1
    
    return lt_count, rt_count

# FOR GETTING THE LENGTH VALUE OF ON BYTE
def pb_string_len_decode(hexoffset):
    hexoffset_u = hexoffset.hex()
    hexoffset_u = bytearray.fromhex(hexoffset_u).hex() # HEX VALUE OF STRING SIZE
    hexoffset_val = int(hexoffset_u, 16) # INTEGER VALUE OF STRING SIZE
    return hexoffset_val

# FOR DECODING BASE 16 HEX TO DECIMAL
def hex_to_decimal(hexdata):
    h = hexdata.hex()
    d = int(h, base = 16)
    return d

# FOR DECODING 64 BIT HEX DATE TIME
def biom_date_decode(hexdata):
    hexdata_i = float(struct.unpack('<d',hexdata)[0])#proper decoding into seconds since 2001-01-01 #[0] is for the touple assignment
    x = datetime.datetime(2001, 1, 1) + datetime.timedelta(seconds=hexdata_i)
    hexdata_t = x.strftime('%Y-%m-%d %H:%M:%S')
    # hexdata_t = x.strftime('%Y-%m-%d %H:%M:%S.%f')
    return hexdata_i, hexdata_t



def read_bioms(bytes_to_search, buf_file):

	dic_hits = [] # Dictionary holding the hit locations for inFocus (Will error if not pre-definded)
	global r_counter  # Assign it to count the records within this function and hold the number globally (assignment at end of function)

	# READ THE FILE INTO MEMORY
	bf = open(buf_file, 'rb')
	buf = bf.read()
	bf.close()

	# GET THE SIZE OF THE BUF (READ FILE)
	buf_size = len(buf)

	for match in re.finditer(in_focus_bytes, buf):
		dic_hits.append(match.start())
	
	logging.info('')
	logging.info(f'File: {buf_file}')
	logging.info(f'Hits (decimal): {dic_hits}')
	logging.info('')

	# ITERATE THROUGH THE HITS AND PARSE THE RECORD
	for hit in dic_hits:

		# GET THE STREAM NAME (IN FOCUS)
		zstreamname_t = buf[hit:hit + len(in_focus_bytes)].decode()

		int_pos = hit + len(in_focus_bytes)

		int_pos += 15 

		# GET THE START DATE HEX
		zstartdate_b = buf[int_pos:int_pos + 8]
		zstartdate_i, zstartdate_t = biom_date_decode(zstartdate_b)

		int_pos += 9


		# GET THE END DATE HEX
		zenddate_b = buf[int_pos:int_pos + 8]
		zenddate_i, zenddate_t = biom_date_decode(zenddate_b)


		int_pos += 24 # SKIP PAST THE SET SIZE BYTES WE DON'T NEED

		# GET THE PACKED BYTE, UNPACK IT, AND GET IT'S VALUES (FOR THE ZVALUESTRING)
		# Not needed for THIS code but may for others.  It's kept here in case of modifications where it's needed.
		st_pb = buf[int_pos:int_pos + 1] # Get the current position through the next (add 1)
		lt_c, rt_c = byte_5_3_decode(st_pb) # Call the procedure to decode


		int_pos +=1 # MOVE PAST THE PACKED BYTE

		# GET THE BYTE HOLDING THE LENGTH OF THE ZVALUESTRI	NG
		st_pb_val = pb_string_len_decode(buf[int_pos:int_pos +1])


		int_pos += 1 # MOVE PAST THE LENGTH BYTE

		# GET THE ZVALUESTRING
		zvaluestring_t = buf[int_pos:int_pos + st_pb_val].decode()


		int_pos = int_pos + st_pb_val # MOVE PAST THE ZVALUESTRING
		st_pb_val = 0 # Reseet just in case

		# GET THE PACKED BYTE FOR THE NEXT THING.  
		# OR...JUST MOVE PAST THAT ONE AND GET THE STRING LENGTH
		int_pos += 1

		# GET THE LENGTH OF THE NEXT STRING
		st_pb_val = pb_string_len_decode(buf[int_pos:int_pos +1])

		int_pos += 1 # Move past this length designator

		# GET THAT LONG GUID
		zuuid_t = buf[int_pos:int_pos + st_pb_val].decode()

		int_pos = int_pos + st_pb_val # MOVE PAST THE zuuid STRING
		int_pos += 13 # Move past the static size items that are of no apparent forensic values
		st_pb_val = 0 # Reset just in case

		st_pb_val = pb_string_len_decode(buf[int_pos:int_pos +1]) # Get the string length
		int_pos += 1 # Move past the value offset

        # GET THE TRANSITION
		try:
			ztransition_t = buf[int_pos:int_pos + st_pb_val].decode()
		except:
			ztransition_t = '' # ERRORS AT 3996 if not here
			#stop = input('NO TRANSITION.  PRESS KEY TO CONTINUE')

		# MOVE THE POSITION PAST THE ZTRANSITION
		int_pos += st_pb_val


		st_pb_val = 0

		sec_i = zenddate_i - zstartdate_i


        # DISPLAY THE RECORS AS THEY ARE FOUND TO SHOW SOMETHING IS GOING ON (turned off for optimization)
		#print('================ NEW RECORD ===================')
		#print(f'IN FILE: {buf_file}')
		#print(f'HIT:  {hit}')
		#print('VARIABLES')
		#print(f'ZSTREAMNAME: {zstreamname_t}')
		#print(f'ZSTARTDATE: {zstartdate_i}, {zstartdate_t}')
		#print(f'ZENDDATE: {zenddate_i}, {zenddate_t}')
		#print(f'SECONDS: {sec_i}')
		#print(f'ZVALUESTRING: {zvaluestring_t}')
		#print(f'ZUUID: {zuuid_t}')
		#print(f'ZTRANSITION: {ztransition_t}')

		# SET THE INSERT RECORD QUERY
		sql_insert = f"""INSERT INTO BIOME_INFOCUS (ZVALUEINTEGER, ZSTREAMNAME, ZSTARTDATE, ZSTARTDATE_T, 
		ZENDDATE, ZENDDATE_T, SECONDS, ZVALUESTRING, ZUUID, ZTRANSITION, FILENAME, LOCATION_D)
		VALUES ('',"{zstreamname_t}", '{zstartdate_i}', '{zstartdate_t}', '{zenddate_i}', '{zenddate_t}', '{sec_i}', '{zvaluestring_t}',
		'{zuuid_t}', '{ztransition_t}', '{buf_file}', '{hit}')"""

		sql_cur.execute(sql_insert)

		# OUTPUT THE RECORD TO THE TSV FILE
		global tsv_output
		tsv_output.write(f'{zstreamname_t}\t{zstartdate_i}\t{zstartdate_t}\t{zenddate_i}\t{zenddate_t}\t{zvaluestring_t}\t{zuuid_t}\t{ztransition_t}\t{buf_file}\t{hit}\n')

		# ADD ONE TO THE COUNTER FOR THE RECORDS TOTAL
		r_counter += 1

        

def check_file_segb(biome_file_name):

    segb = b'\x53\x45\x47\x42'

    with open(biome_file_name, 'rb') as mf:
        fc = mf.read(256)

    tf_loc = fc.find(segb)

    if tf_loc != -1: # - 1 meaning nothing was found
        tf = True
    else:
        tf = False

    return tf, tf_loc
    


def import_knowledgec():
	
	print('If you wish to specify a path for the knowledgeC.db, you may')
	print('do so here.  If the knowledgeC.db is in the current folder,')
	print('(same folder as this script) you can just hit enter.  If not')
	print('You\'ll need to specify where it is, including the filename')
	print()
	
	err_lock = 1 # Equals 0 if file exists (see below)
	
	while err_lock == 1:
		
		kc_ret = input('INPUT:   ')
		print()
		
		if kc_ret == "": 
			kc = 'knowledgeC.db'
			# print(f'{kc} in the current directing is being used')
		else:
			kc = kc_ret
		
		if os.path.isfile(kc) is True:
			err_lock = 0
		else:
			print(f'{kc} does not exist. Specify a file that exists')
			print()
			
		kc_ret = None
		
	print(f'Using {kc} to import the data from.')
	print()
	
		
	logging.info('========================================')
	logging.info('====== Building database tables ========')
	logging.info('========================================')
	logging.info('')
	
	
	sqlquery = f"""ATTACH DATABASE '{kc}' AS KC"""
	
	sql_cur.execute(sqlquery)
	
	logging.info('QUERY TO ATTACH DATABASE:')
	logging.info(sqlquery)
	logging.info('')
	
	print(f'{kc} attached as "KC" in {of_db}')

	sqlquery = """CREATE TABLE IF NOT EXISTS'ZOBJECT_IMPORT' AS 
	SELECT Z_PK, ZVALUEINTEGER, ZSTARTDATE, ZENDDATE, ZUUID, 
	ZSTREAMNAME, ZVALUESTRING FROM KC.ZOBJECT ORDER BY ZSTARTDATE"""
	
	sql_cur.execute(sqlquery)
	
	logging.info('QUERY USED TO IMPORT TABLE DATA:')
	logging.info(sqlquery)
	logging.info('')
	
	
	sqlquery = """CREATE TABLE IF NOT EXISTS 'ACTIVITY_COMBINED' AS
	SELECT 
	datetime(ZOBJECT_IMPORT.ZSTARTDATE + 978307200,'unixepoch') AS "STARTTIME",
	ZOBJECT_IMPORT.ZSTARTDATE, 
	datetime(ZOBJECT_IMPORT.ZENDDATE + 978307200,'unixepoch') AS "ENDTIME",
	ZOBJECT_IMPORT.ZENDDATE,
	ZOBJECT_IMPORT.ZSTREAMNAME, 
	ZOBJECT_IMPORT.ZVALUESTRING, 
	ZOBJECT_IMPORT.ZENDDATE - ZOBJECT_IMPORT.ZSTARTDATE AS "SECONDS",
	ZOBJECT_IMPORT.ZVALUEINTEGER
	FROM ZOBJECT_IMPORT
	UNION ALL
	SELECT 
	datetime(BIOME_INFOCUS.ZSTARTDATE + 978307200,'unixepoch') AS "STARTTIME",
	BIOME_INFOCUS.ZSTARTDATE,
	datetime(BIOME_INFOCUS.ZENDDATE + 978307200,'unixepoch') AS "ENDTIME",
	BIOME_INFOCUS.ZENDDATE, 
	BIOME_INFOCUS.ZSTREAMNAME, 
	BIOME_INFOCUS.ZVALUESTRING, 
	BIOME_INFOCUS.ZENDDATE - BIOME_INFOCUS.ZSTARTDATE AS "SECONDS",
	BIOME_INFOCUS.ZVALUEINTEGER
	FROM BIOME_INFOCUS
	ORDER BY STARTTIME"""
	
	sql_cur.execute(sqlquery)
	
	logging.info('QUERY USED TO COMBINE TABLES: ')
	logging.info(sqlquery)
	logging.info('')


# =========================================================
# ================= START NON DEF CODE HERE ====================
# =========================================================

print('This program will parse all of the inFocus (what was actually in the foreground).')
print('of the iOS 16.0 and above which, since iOS 16.0, no longer resides in the knowledgeC')
print('The locations of the BIOME which contains the inFocus data: ')

print('   /private/var/db/biome/streams/restricted/_DKEvent.App.inFocus/local')
print()
print('The files have no extnetion but the name is an Apple absolute time milliseconds (number / 1000000)')
print('You can export the parent folder and then point the script to it (upcoming prompt),')
print('or you can simply place the files in the same folder as this script and it will default here.')
print('If subfolders contain more data, you only need point to the parent folder. ')
print('This script will search subfolders for additional files')
print()
print('NOTE: This looks for any "SEGB" within the first 256 kb of the file.  If it finds one in a')
print('file that is NOT a protobuf it error out if it also contains an "/app/inFocus" that is NOT')
print('part of an actual protobuf BIOME file.  This just means you should not just run it on the root')
print('of the drive or a place with many other scripts that may contain those words.')
print()
print('Provide the folder containing the inFocus biome files.')
print()
rootpath = input('INPUT:  ')

# ASSIGN THE ROOT PATH TO "." AS A DEFAULT
if rootpath == "":
    rootpath_w = r"."
else:
    rootpath_w = rootpath

# GET THE NAMES OF THE TSV, LOG, AND DB
print()
print('This will output the data to a TSV (tab separated variable) file AND')
print('an SQLite database along with the log file. ')
print('You can provided a file name for these OR it willdefault to "inFocus_BIOME_Parser.tsv", ')
print('"inFocus_BIOME_Parser.db", and "inFocus_BIOME_Parser.log"')
print('just hit ENTER')
print()
of = input('   INPUT: ')
print()

# ASSIGN THE NAMES OF THE TSV, LOG, AND DB
if of == "":
    of_tsv = 'inFocus_BIOME_Parser.tsv'
    of_db = 'inFocus_BIOME_Parser.db'
    of_log = 'inFocus_BIOME_Parser.log'
else:
    of_tsv = of + '.tsv'
    of_db = of + '.db'
    of_log = of + '.log'


# PREPARE THE DATABASE AND TABLE
sql_con = sqlite3.connect(of_db)
sql_con.row_factory = sqlite3.Row
sql_cur = sql_con.cursor()

sqlite_mt = ("""CREATE TABLE IF NOT EXISTS BIOME_INFOCUS (
Z_PK INTEGER PRIMARY KEY,
ZSTREAMNAME VARCHAR,
ZSTARTDATE TIMESTAMP,
ZSTARTDATE_T VARCHAR,
ZENDDATE TIMESTAMP,
ZENDDATE_T VARCHAR,
SECONDS INTEGER,
ZVALUESTRING VARCHAR,
ZUUID VARCHAR,
ZTRANSITION VARCHAR,
ZVALUEINTEGER INTEGER,
FILENAME VARCHAR,
LOCATION_D INTEGER
);""")

#print(sqlite_mt)

# EXECUTE THE QUERY
sql_cur.execute(sqlite_mt)


records = sql_cur.fetchall()

# LOGGING THE TOTAL NUMBER OF RECORDS RETURNED
num_records = str(len(records))



# DEFINE THE HEX FOR THE "/app/inFocus"
in_focus_bytes = b'\x2F\x61\x70\x70\x2F\x69\x6E\x46\x6F\x63\x75\x73'
in_focus_bytes_s = bytes(in_focus_bytes).decode()
print(f'Searching for instances of hexadecimal: {in_focus_bytes.hex()}, ASCII: {in_focus_bytes_s}')
print()

# WARNING THE USER OF THE STUFF GOING ALL OVER THE SCREEN SOON.
print('Please be patient...')
print('You may see a large number of integers sweeping across the screen')
print('for a few minutes.  This is normal.  It\'s showing the list of record hits')
input('Press any key to continue')

# SETTING UP LOGGING TO BE ABLE TO LOG ACTIONS
import logging
level    = logging.INFO
format   = '%(message)s'
handlers = [logging.FileHandler(of_log), logging.StreamHandler()]
logging.basicConfig(level = level, format = format, handlers = handlers)

#GET DATE AND TIME FOR LOGGING
now = datetime.datetime.now()
# USAGE: # print (now.strftime("%Y-%m-%d %H:%M:%S LT"))

# START THE LOGGING OF THE EVENTS FOR THE LOG FILE
print(f'Starting the log file {of_log}') 

logging.info('========================================')
logging.info('=========== LOG FILE ===================')
logging.info('========================================')
logging.info('')
logging.info(f'Staring the log file at {now}')
logging.info(f'TSV File: {of_tsv}, Database File: {of_db} , THIS log file: {of_log}')
logging.info('')


# OS WALK CODE - MODIFY TO CHECK AND PROCESS EACH FILE AND
# CREATE A LIST OF FILES CONTAINING SEGB WITHING THE FIRST 256 BYTES

segb_list = [] # LIST FOR FILES CONTAINING SEGB

for root, dirs, files in os.walk(rootpath_w):
    for file in files:
        file_name = os.path.join(root, file)
        segb_tf, segb_loc = check_file_segb(file_name)
        if segb_tf == True:
            segb_list.append(file_name)

print(segb_list)     


# ASSIGN THE RECORD COUNTER TO TOAL RECORDS PARSED
r_counter = 0

# OPEN THE TSV FILE FOR OUTPUTING RECORDS
tsv_output = open(of_tsv, 'w')
tsv_output.write('ZVALUEINTEGER\tZSTREAMNAME\tZSTARTDATE\tZSTARTDATE_T\tZENDDATE\tZENDDATE_T\tZVALUESTRING\tZUUID\tZTRANSITION\tFILENAME\tLOCATION_D\n')


# CALL THE FUNCTION TO PARSE THE DATA

for buf_file in segb_list:
    read_bioms(in_focus_bytes, buf_file)
    
#DON'T FORGET TO COMMIT!
sql_con.commit() 


# ASK ABOUT ACQUIRING KNOWLEDGE C DATA
print()
print('Do you want to import knowledgeC ZOBJECT data and combine the')
print(f'BIOME data with the ZOBJECT into a new table in {of_db}?')
print('To do this you MUST have the knowledgeC.db file.')
print('If you don\'t have it, select "N" for NO!')
print('Y = Yes, N (or any other key) = No')
print()


err_lock = 1

while err_lock == 1:
	ret = input('INPUT (Y or N):   ')
	print()
	if ret == "y" or ret == "Y":
		print('Importing knowledgeC data')
		import_knowledgec()
		err_lock = 0
		
	elif ret == "n" or ret == "N":
		print('Proceeding without importing knowledgeC data')
		print()
		err_lock = 0

	else:
		print('Please select "N" or "Y".')
	


# PUT THE TOYS AWAY AND CLOSE THE LID
sql_con.close() 
tsv_output.close()

logging.info('========================================')
logging.info('')
logging.info(f'Total records parsed fro BIOMES: {r_counter}')
logging.info('')

print('If you got no errors everything should have worked correctly.')
print(f'Check the {of_log}, {of_tsv}, and {of_db} for your data') 
sys.exit(0)

        
# END
