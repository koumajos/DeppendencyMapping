#!/usr/bin/python3.6
"""CreateScript:

    This script is part of PassiveAutodiscovery modul for modular monitoring system NEMEA (Network Measurement Analysis).
    This part is for:
        Script allows to create sqlite3 database file with inserted name. Then the database file will be scructured by SQL file (Database_sqlite_create.sql).

        Script will try download actualizate initial data from web database and download it (.csv files).If donwloading of anz file failed, the script will use backup file which is (in default state) stored in the same folder.

        The initial data from files will be added to tables: Ports, VendorsMAC and Services





    Copyright (C) 2020 CESNET


    LICENSE TERMS

        Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
            1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
  
            2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

            3. Neither the name of the Company nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

        ALTERNATIVELY, provided that this notice is retained in full, this product may be distributed under the terms of the GNU General Public License (GPL) version 2 or later, in which case the provisions of the GPL apply INSTEAD OF those given above. 

        This software is provided as is'', and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. In no event shall the company or contributors be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.




"""
#libraries for working with sqlite3 database
import sqlite3
import csv
#libraries for working with OS UNIX files and system
import os
import sys
#libraries for downloading initial data from oficial web databse
import urllib           
import urllib.request
#libraries for arguments os scripts
import argparse     
from argparse import RawTextHelpFormatter
#===============================================================================================
#url of (un)official web databse of inital data fro sqlite3 database
urlP = "https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv"
urlV = "https://macaddress.io/database/macaddress.io-db.csv"
#===============================================================================================
#===============================================================================================
def CheckStr(STR, DOT):
    """Function check if string have DOT suffix in end of string. Like suffix .txt in text.txt.

    Parameters
    --------
    STR : str 
        String of file name.
    DOT : str
        String of file suffix.
    Returns
    --------
    Boolean : boolean
        True if STR have suffix DOT.
        False if STR havn't suffix DOT.
    """
    x = STR.split(DOT)
    if x[-1] == '':
        return True
    return False
#===============================================================================================
#===============================================================================================
def CreateDB(FILE):
    """Create sqlite3 database file and then created scructure of tables in it
    
    Parameters
    --------
    FILE : str 
        The database file to create.

    Returns
    --------
    SQLiteConnection : sqlite3
        The connection to created sqlite3 database.
    cursor : sqlite3
        The cursor for execute SQL queries in created sqlite3 database.
    """
    try:
        print("Connecting to database....", end = '')
        if os.path.exists(FILE):        #if database file exist:
            print("")
            print("Database already exists. Do you want do delete it and create new? [yes] - ", end = '')
            if(input() == "yes"):       #choose if:
                print("Removing old database and create new one....", end = '')
                os.remove(FILE)         #remove file and continue
            else:
                print("Exiting script....")
                sys.exit()              #exit
        SQLiteConnection = sqlite3.connect(FILE)        #create ne connection to new sqlite database file
        cursor = SQLiteConnection.cursor()
        print("done")
        with open('Database_sqlite_create.sql') as sqlite_file:     #open the sql file
            sql_script = sqlite_file.read()
        print("Creating Database schema....", end = '')
        cursor.executescript(sql_script)        #and execute it for create sql scructure in database
        print("done")
        return SQLiteConnection, cursor;        #return connectiona nd cursor for work with database
    except sqlite3.Error as error:
        print("Error while executing sqlite script", error)
#===============================================================================================
#===============================================================================================
def DownloadData(name):
    """Download initial data for sqlite3 database and open it
    
    Parameters
    -----------
    name : str 
        The name of table for that are downloaded data.

    Returns
    --------
    reader : csv
        The opened data taht have been downloaded.
    """
    try:        #try download the file from url, if can't download or connect, use the archive local file (can be deprecated)
        if name == "Ports":        
            print("Downloading Transport Layer Ports data....", end='')
            urllib.request.urlretrieve(urlP, name + "_url.csv")
        else:
            print("Downloading Vendors of MAC address data....", end='')
            urllib.request.urlretrieve(urlV, name + "_url.csv")                    
        print("done")
        reader = csv.reader(open(name + "_url.csv",'r'), delimiter=',')
    except:
        print("Download failed, open local archive file...")
        reader = csv.reader(open(name + ".csv",'r'), delimiter=',')
    return reader
#===============================================================================================
#===============================================================================================
def InserData(SQLiteConnection, cursor, readerP, readerM, readerS, readerF):
    """Insert initial data to tables
    
    Parameters
    -----------
    SQLiteConnection : sqlite3 
        The connection to the sqlite3 database.
    cursor : sqlite3
        The cursor at the sqlite3 database for execute SQL queries.
    readerP : csv
        The opened file that is fill with initial Ports table data
    readerM : csv
        The opened file that is fill with initial VendorsMAC table data
    readerS : csv
        The opened file that is fill with initial Services table data
    readerF : csv
        The opened file that is fill with initial Filter table data
    """
    try:
        print("Inserting data to table Ports....", end='')
        for row in readerP:
            to_db = [row[0], row[1], row[2], row[3]]
            cursor.execute("INSERT INTO Ports (ServiceName, PortNumber, TransportProtocol, Description) VALUES (?, ?, ?, ?);", to_db)
        print("done")
        print("Inserting data to table VendorsMAC....", end='')
        for row in readerM:
            to_db = [row[0], row[1], row[2], row[4], row[5]]
            cursor.execute("INSERT INTO VendorsMAC (VendorMAC, IsPrivate, CompanyName, CountryCode, AssignmentBlockSize) VALUES (?, ?, ?, ?, ?);", to_db)
        print("done")
        print("Inserting Services data to table....", end='')
        for row in readerS:
            to_db = [row[0], row[1], row[2], row[3]]
            cursor.execute("INSERT INTO Services (PortNumber, DeviceType, Shortcut, Description) VALUES (?, ?, ?, ?);", to_db)
        print("done")
        print("Inserting Filter data to table....", end='')
        for row in readerF:
            to_db = [row[0], row[1], row[2], row[3]]
            cursor.execute("INSERT INTO Filter (ID_Filter, PortNumber, Protocol, MinPackets) VALUES (?, ?, ?, ?);", to_db)
        print("done")
        SQLiteConnection.commit()        
    except sqlite3.Error as error:
        print("Error while inserting data to sqlite3 database", error)
#===============================================================================================
#===============================================================================================
#main function
def Main():
    """Main function of script. Work with other functions to create database, get a initial data and fill the initial data to tables.
    
    """
    #===============================================================================================
    #Arguemnts of python script
    parser = argparse.ArgumentParser( description="""Create sqlite3 database from sql file: Database_sqlite_create.sql 
    Database is filled with PassiveAutodiscovery.py NEMEA modul with coaporate Collector.py.
    Then analyze with DeviceAnalyzer.py.

    Usage:""", formatter_class=RawTextHelpFormatter)
    #===============================================================================================
    parser.add_argument(
        '-d', '--database',
        help="Set name of the database without . part,  default is Database",
        type=str,
        metavar='NAME',
        default="Database"
    )
    arguments = parser.parse_args()
    #===============================================================================================
    #name of sqlite3 database file that will be create    
    if CheckStr(arguments.database, ".db") == True:
        FILE = arguments.database
    else:
        FILE = arguments.database + ".db"       
    #create sqlite3 database
    SQLiteConnection, cursor = CreateDB(FILE)
    #===============================================================================================
    #fill sqlite3 database with initial data
    readerP = DownloadData("Ports")
    readerM = DownloadData("VendorsMAC")
    readerS = csv.reader(open('Services.csv','r'), delimiter=',')    
    readerF = csv.reader(open('Filter.csv','r'), delimiter=',')
    InserData(SQLiteConnection, cursor, readerP, readerM, readerS, readerF)
    #===============================================================================================
    #release of used resources
    cursor.close()
    if(SQLiteConnection):
        SQLiteConnection.close()
#===============================================================================================
#===============================================================================================
if __name__ == "__main__":
    Main()
#===============================================================================================
#===============================================================================================
