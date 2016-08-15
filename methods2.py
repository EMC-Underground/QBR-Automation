import os
import requests
import boto3
import json
import urllib2
import csv



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
    temp = "{"+"Global Duns Name"+":"+repJsonData['rows'][x]['Global Duns Name']+","+"Global Duns Number" + ":" + repJsonData['rows'][x]['Global Duns Number']+"}"
    if not allAccountArray:
      allAccountArray.append(temp)
    for y in range(0,len(repJsonData['rows'])):
      if temp not in allAccountArray:
        allAccountArray.append(temp)
      else:
        break


  print allAccountArray    
  allAccount = json.dumps(allAccountArray) 
  print "break"
  print allAccount


#   Figure out how to Send accountsArray back to front end javascript  to populate dropdown
 
  return str(allAccountArray) + '\n' + str(allAccount) 

# Function to load what keys to pull for from the Install Data
def getInstallKeyList(keyfilename):
  
  with open(keyfilename) as keylist_file:
    keylist = json.load(keylist_file)

  print keylist
  keyarray = []
  for k, v in keylist.items():
    if v == 'true':
      keyarray.append(k)
 
  print keyarray

  #keyarray = []
  #for line in keyfile:
  #  keyarray.append(line.rstrip())
  #keyfile.close()

  return  keyarray

# Function to pull account Install base, create CSV and upload it to ECS
def getInstallData(gdun):
  
  #get list of keys to include on CSV
  keyArrayInstall = getInstallKeyList('keylistJson.json')
 
  print keyArrayInstall

  #Get intall data 
  url = "http://pnwreport.bellevuelab.isus.emc.com/api/installs/"+gdun
  myResponse = requests.get(url)
  installJsonData = json.loads(myResponse.content)
    
  
  # open a file for writing

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
  
  
 

  return "You got the install information for Gdun: {0}".format(gdun)
 



  

  
