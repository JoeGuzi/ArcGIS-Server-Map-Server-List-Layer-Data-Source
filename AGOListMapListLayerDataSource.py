""" ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------###
Description: This script will go through all of the MXDs that created services and list the layer and data source within the map.
 
Beginning with: AGOListMapListLayerDataSource.py
 
Created on: 8/4/2016
 
Purpose: This script will go through all of the MXDs that created services and list the layer and data source within the map.
 
Authored by: Brandon Longenberger
 
Previous Production Date: 8/2/2018     Production Date: 8/31/18
 
### ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
#Import Modules
import arcpy, string, os, sys

import arcpy, time, sys, string, os, traceback, datetime, shutil
import smtplib
from email.MIMEText import MIMEText



# Write Log code
logFile = ""
message = ""

def writelog(logfile,msg):
    print msg
    f = open(logfile,'a')
    f.write(msg)
    f.close()

dateTimeStamp = time.strftime('%Y%m%d%H%M%S')
root = os.path.dirname(sys.argv[0]) #"C:\\Users\\jsguzi\\Desktop" 
if not os.path.exists(root + "\\log"): # Check existence of a log folder within the root, if it does not exist it creates one.
    os.mkdir(root + "\\log")
scriptName = sys.argv[0].split("\\")[len(sys.argv[0].split("\\")) - 1][0:-3] #Gets the name of the script without the .py extension  
logFile = root + "\\log\\" + scriptName + "_" + dateTimeStamp[:14] + ".log" #Creates the logFile variable
if os.path.exists(logFile):
    os.remove(logFile)

''' 
---  These are log examples  ---
message += "Write log message here" + "\n"
exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
formatted_lines = traceback.format_exc().splitlines()
writelog(logFile,message + "\n" + formatted_lines[-1])
writelog(logFile, "Write log message here" + "\n")
---  End log examples  ---
'''
# End Write Log code



#Create Audit Folder
message += "Check Folder Existence" + "\n"

folder_Path = "G:\\SCGIS\\ArcGISServerAudit\\SCGIS\\"
date = datetime.date.today()
date =str(date)
newDate = date[5:7] + date[8:] + date[0:4]
folder = folder_Path + "Audit" + newDate
if not os.path.exists(folder):
    os.mkdir(folder)

message += "Check Folder Existence Complete!" + "\n"



#Variables
ArcGISServerFolderPath = "\\\\ArcGISServer.esri.local\\E$\\arcgisserver\\directories\\arcgissystem\\arcgisinput" # change this to your server
FolderPath = ""
File = folder + "\\MapServiceAudit.csv"
Con_File = folder + "\\MapServiceAudit - Condensed.csv"

csv_file = open(File, "wb")
csv_file.write("Full Path,Server,MXD Name,Layer Name,Layer Data Source" + "\n")

con_csv_file = open(Con_File, "wb")
con_csv_file.write("Server,Folder Name,Service Name,Layer Data Source,Geodatabase,Dataset,Feature Class" + "\n")

#Functions
def FindMXD(folderPath, server):
    writelog(logFile, "Process Started" + server +"\n")
    global text
    global con_text
    for subdir, dirs, files in os.walk(folderPath):
        for file in files:
            #if os.path.isfile(fullpath):
            if file.lower().endswith(".mxd"):
                #print file
                fullpath = os.path.join(subdir, file)
                mxd = arcpy.mapping.MapDocument(fullpath)
                for lyr in arcpy.mapping.ListLayers(mxd):
                    if lyr.supports("DATASOURCE"):
                        FolderName, ServiceName = ReturnServiceInfo(fullpath)
                        name = lyr.name
                        dataSource = lyr.dataSource
                        con_data_source = DataSource(dataSource)
                        text += fullpath.replace(u'\u002c', "") + "," + server + "," + FolderName + "," + ServiceName + "," + name.replace(u'\u002c', "") + "," + dataSource.replace(u'\u002c', "") + "," + "\n"
                        if con_data_source[1] != "":
                            con_text += server + "," + FolderName + "," + ServiceName + "," + "" + "," + con_data_source[1] + "," + con_data_source[2] + "," + con_data_source[3] + "\n"
                        else:
                            con_text += server + "," + FolderName + "," + ServiceName + "," + con_data_source[0] + "\n"
                del mxd
            #break
    writelog(logFile, "Process Complete" + server + "\n")

def DataSource(data_source):
    cat_index = data_source.find("ArcCatalog")
    dat_index = data_source.find("Database Connections")
    if dat_index == -1 and cat_index == -1:
        data_source = data_source
        database = ""
        dataset = ""
        fc = ""
    else:
        if dat_index != -1:
            data_source = data_source[dat_index + 21:]
            l_index = data_source.find("\\")
            r_index = data_source.rfind("\\")
            database = data_source[0:l_index]
            dataset = data_source[l_index + 1:r_index]
            fc = data_source[r_index + 1:]
        elif cat_index != -1:
            data_source = data_source[cat_index + 11:]
            l_index = data_source.find("\\")
            r_index = data_source.rfind("\\")
            database = data_source[0:l_index]
            dataset = data_source[l_index + 1:r_index]
            fc = data_source[r_index + 1:]
    return data_source, database, dataset, fc

def ReturnServiceInfo(FullPath):
    print FullPath
    #print type(FullPath)
    #print FullPath.find("arcgisinput")
    #print FullPath.find("extracted")
    Service = FullPath[FullPath.find("arcgisserver\\directories\\arcgissystem\\arcgisinput") + 50:FullPath.find("extracted\\v101") - 1]
    if ".MapServer" in Service or ".FeatureServer" in Service:
        Backslash = Service.find("\\")
        FolderName = ""
        ServiceName = ""

        if Backslash == -1:
            ServiceName = Service
        else:
            FolderName = Service[:Backslash]
            ServiceName = Service[Backslash + 1:]
        return FolderName, ServiceName

#Process

try:
    #Loop through each MXD file
    text = ""
    con_text = ""
    FindMXD(ArcGISServerFolderPath, "ArcGISServer") #change parameters of the function
    csv_file.write(text + "\n")
    csv_file.close()

    con_csv_file.write(con_text + "\n")
    con_csv_file.close()

    writelog(logFile, "Process Complete!" + "\n")
    
except:
    message += "error"
    messages = arcpy.GetMessages()
    message += messages
    print message
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    formatted_lines = traceback.format_exc().splitlines()
    writelog(logFile,message + "\n" + formatted_lines[-1])
    message += formatted_lines[-1]
    # Send Email
    # This is the email notification piece [%]
    #email error notification
    smtpserver = ''
    AUTHREQUIRED = 0 # if you need to use SMTP AUTH set to 1
    smtpuser = ''  # for SMTP AUTH, set SMTP username here
    smtppass = ''  # for SMTP AUTH, set SMTP password here

    RECIPIENTS = ['jsguzi@starkcountyohio.gov', 'bwlongenberger@starkcountyohio.gov']
    SENDER = ''
    #msg = arcpy.GetMessages()***I think I need to look at the message variable
    #msg = arcpy.GetMessage(0)# Brian Corrected this it is arcpy.GetMessage()
    #msg += arcpy.GetMessage(2)# Brian Corrected this it is arcpy.GetMessage()
    #msg += arcpy.GetMessage(3)# Brian Corrected this it is arcpy.GetMessage()
    msg = MIMEText(message) #***i pointed this mime thing at the message 
    msg['Subject'] = 'Error with Script: ' + str(scriptName) ### this is the subject line of the email
    # Following headers are useful to show the email correctly
    # in your recipient's email box, and to avoid being marked
    # as spam. They are NOT essential to the sendmail call later
    msg['From'] = "ArcGIS on WebAGS "
    msg['Reply-to'] = "Joe Guzi "
    msg['To'] = "jsguzi@starkcountyohio.gov"

    session = smtplib.SMTP(smtpserver)
    if AUTHREQUIRED:
        session.login(smtpuser, smtppass)
    session.sendmail(SENDER, RECIPIENTS, msg.as_string())
    session.close()
