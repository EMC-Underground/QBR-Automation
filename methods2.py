import os
import requests
import boto3
import json
import urllib2
import csv


repJsonData = {}

from botocore.client import Config

with open('ECSconfig.json') as config_file:
  config = json.load(config_file)

def getRepFunction(lastname, firstname, middle):
  global repJsonData
  print lastname
  print firstname
  print middle
 
  url = "http://pnwreport.bellevuelab.isus.emc.com/api/rep/"+lastname+"/"+firstname+"/"+middle
  myResponse = requests.get(url)
  repJsonData = json.loads(myResponse.content)

  #print repJsonData

  print len(repJsonData['rows'])

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
 

# Send accountsArray back to front end javascript  to populate dropdown
 
  return "Rep info: lastname: {0} firstname: {1} middle initial: {2}!".format(lastname, firstname, middle)

  
def getInstallData(gdun):

  url = "http://pnwreport.bellevuelab.isus.emc.com/api/installs/"+gdun
  myResponse = requests.get(url)
  installJsonData = json.loads(myResponse.content)
  install_json = installJsonData['rows']
  # open a file for writing
 
  install_data = open('/tmp/InstallData.csv','w')

  # create the csv writer object

  csvwriter = csv.writer(install_data)
  count = 0
  for item_num in install_json:
    if count ==0:
      header = item_num.keys()
      csvwriter.writerow(header)
      count +=1
    csvwriter.writerow(item_num.values())
  install_data.close()
  
  print(gdun)

  csvwriter= csv.writer(install_json)

  return "you got the install information for Gdun: {0}".format(gdun)

#def getInstallData(accountName):
 # global repJsonData 
  #print accountName
  #print repJsonData
  #for x in range (0,len(repJsonData['rows'])):
   # if repJsonData['rows'][x]['Global Duns Name'] == accountName:
    #   gdun = repJsonData['rows'][x]['Global Duns Number']
     #  print gdun

  #s3 = boto3.resource('s3',
                   #   use_ssl=False,
		    #  endpoint_url=config['ecs_url'],
		    #  aws_access_key_id=config['ecs_user_id'],
		    #  aws_secret_access_key=config['ecs_user_access_key'],
		    #  config=Config(s3={'addressing_style':'path'}))
 
  
  #userBucket = s3.Bucket('pacnwinstalls')
  
  #userObject = userBucket.Object('{0}.json'.format(gdun)).get()
  
  #print(json.loads(userObject['Body'].read()))
 

#  return "You got the install information for Account Name: {0}".format(accountName)
  



  

  
