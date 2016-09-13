import os
import requests
import boto3
import json
import urllib2
import unicodecsv as csv


from botocore.client import Config

#load ECS config file
with open('ECSconfig.json') as config_file:
  config = json.load(config_file)

#function for getting Account Rep's Account Names and GDUNS
def getRepFunction(lastname, firstname, middle):
  print lastname
  print firstname
  print middle
 
 #get rep account data
  url = "http://pnwreport.bellevuelab.isus.emc.com/api/rep/"+lastname+"/"+firstname+"/"+middle
  myResponse = requests.get(url)
  repJsonData = json.loads(myResponse.content)


 #build Array of Account Names and GDUNS 
  allAccountArray = []
  for x in range(0,len(repJsonData['rows'])):
    temp = ""
    temp = '{"Global_Duns_Name":"'+repJsonData['rows'][x]['Global Duns Name']+'", "Global_Duns_Number":"' + repJsonData['rows'][x]['Global Duns Number']+'"}'
    if not allAccountArray:
      allAccountArray.append(temp)
    for y in range(0,len(repJsonData['rows'])):
      if temp not in allAccountArray:
        allAccountArray.append(temp)
      else:
        break

  print allAccountArray    
  
  #remove unicode
  allAccountJson = json.dumps(allAccountArray) 
  #convert JSON to string
  allAccountString = str(allAccountJson)

  return  allAccountString

# Function to load what keys to pull for from the Install Data
def getInstallKeyList(install_keyfile):
  
  with open(install_keyfile) as install_keyfile:
    install_keylist = json.load(install_keyfile)

  installKeyArray = []
  for k, v in install_keylist.items():
    if v == 'true':
      installKeyArray.append(k.rstrip())

  return installKeyArray

#Function to load SRS key list
def getSRSKeyList(srskeyfile):
  
  with open(srskeyfile) as srskeylist_file:
    srskeylist = json.load(srskeylist_file)
  
  srskeyarray=[]  
  for k, v in srskeylist.items():
    if v == 'true':
      srskeyarray.append(k.rstrip())

  return srskeyarray

# Function to pull account Install base, create CSV and upload it to ECS
def getInstallData(gdun, teaminfo):
  print gdun

#  print teaminfo

  #get list of Install keys to include on CSV
  keyArrayInstall = getInstallKeyList('installkeys.json')
#  print keyArrayInstall

  #get list of SRS  keys to include on CSV
  keyArraySRS = getSRSKeyList('srskeys.json')
#  print keyArraySRS


  #Get intall data 
  url = "http://pnwreport.bellevuelab.isus.emc.com/api/installs/"+gdun
  myResponse = requests.get(url)
  installJsonData = json.loads(myResponse.content)
    
#  installJsonData = installJsonData.encode('ascii', 'ignore').decode('ascii')

  # open a file for writing install data

  installfilename =  'InstallData.csv'
  install_data = open(installfilename,'w')

  # create the csv writer object

  csvwriter = csv.writer(install_data)
  csvwriter.writerow(keyArrayInstall)
  for item in installJsonData['rows']:
    tempArray = []
    for subkey in keyArrayInstall:
      tempArray.append(item[subkey])
    csvwriter.writerow(tempArray)
  install_data.close()
  
  #push install CSV to ECS
  bucket = 'QBR_Files'
  filename = gdun + '_Install_Data'
  s3 = boto3.resource('s3',
                      use_ssl=False,
		      endpoint_url=config['ecs_url'],
		      aws_access_key_id=config['ecs_user_id'],
		      aws_secret_access_key=config['ecs_user_access_key'],
		      config=Config(s3={'addressing_style':'path'}))

  s3.Bucket(bucket).upload_file(installfilename, filename)  

  print 'file ' + gdun + '_Install_Data   was added to the bucket: ' + bucket  
  
  #Get SRS data
  
  srsUrl = "http://pnwreport.bellevuelab.isus.emc.com/api/srs/"+gdun
  srsResponse = requests.get(srsUrl)
  srsJsonData = json.loads(srsResponse.content)
  
  # open a file for writing srs data
  
  srsfile = 'SRSData.csv'
  srsdata = open(srsfile, 'w')


  #create the csv writer object
 
  SRScsvwriter = csv.writer(srsdata)
  SRScsvwriter.writerow(keyArraySRS)
  for item in srsJsonData['rows']:
    SRStempArray = []
    for srsSubKey in keyArraySRS:
      SRStempArray.append(item[srsSubKey])
    SRScsvwriter.writerow(SRStempArray)
  srsdata.close()


  #push srs CSV to ECS
  
  srsfilename = gdun + '_SRS_Data'
  s3.Bucket(bucket).upload_file(srsfile, srsfilename)

 #push json of account team info to ECS
  
  teaminfo_filename = gdun + '_teaminfo'

  response = s3.Object(bucket,teaminfo_filename).put(Body=teaminfo)
  print(response) 


  print 'file ' + teaminfo_filename + " was uploaded into the bucket " + bucket +  "with the following contents: " + teaminfo
  return "You completed the first step of your QBR please contact shared services to create your presentation "
 



  

  
