import methods2
import os
from flask import Flask, request, jsonify
app = Flask(__name__)

port = 8000

#app.debug = True



@app.route("/<lastname>/<firstname>/<middle>", methods = ['GET'])
def repFunction(lastname, firstname, middle):
  if request.method == 'GET':
    return  methods2.getRepFunction(lastname,firstname,middle) 
  else: 
    return "Invalid"

@app.route("/account/<gdun>", methods = ['POST'])
def getInstallData(gdun):
  if request.method == 'POST':
    payload = request.get_json()
    return methods2.getInstallData(gdun, payload)
  else:
    return "Invalid"


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=port)





