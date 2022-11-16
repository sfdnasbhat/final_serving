 
 import flask
from flask_restful import Api,request
import os
from flask import Flask, jsonify
app = Flask(__name__)
import google.auth
import json
import pandas as pd
from google.cloud import retail
from google.oauth2 import service_account

PROJECT_NUMBER='677677793557'

credentials, project = google.auth.default(
    scopes=[
      'https://www.googleapis.com/auth/cloud-platform'
    ]
)

# For local testing you may want to do something like this if
# your default credentials done have Retail/Recommendations Viewer Role
SERVICE_ACCOUNT_FILE = 'new.json'
credentials = service_account.Credentials.from_service_account_file(
  SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/cloud-platform'])

client = retail.PredictionServiceClient(credentials=credentials)

def recommend(userid):
    #if request.args and 'visitorid' in request.args:
    visitorid = userid
    #else:
           #visitorid = "1001"

    placement = 'similarproductsearch'

    user_event = {
        'event_type': 'detail-page-view',
        'visitor_id': visitorid,
        'product_details': [{
          'product': {
            'id': '0YZ3C0',
          }
        }]
      }

    predict_request = {
        "placement":'projects/' + PROJECT_NUMBER +'/locations/global/catalogs/default_catalog/placements/' + placement,
        "user_event": user_event
    }

    response = client.predict(predict_request)
    items = []
    for rec in response.results:
        product = rec.metadata.get('product')
        item =  rec.id
        items.append(item)
    recommend = {
        'visitorId':visitorid ,
        'items':items
    }
    return recommend
@app.route('/v1/check',methods=['GET','POST'])
def check():
    if request.method =='POST' :
        #print (request.is_json)
        content = request.get_json()
        
        device = content['device']
        device = device.split(',')
        device = list(device)
        #return jsonify(device)
        #[x.encode('utf-8') for x in rec]
        df = pd.DataFrame()
        for dev in device:
            ans = recommend(dev)
            df1 = pd.DataFrame.from_dict(ans, orient="columns")
            df = pd.concat([df,df1])
        data = df.reset_index()
        data=data.groupby(["visitorId"], as_index=False)['items'].agg(",".join)
        data = data.to_json(orient = 'index')
            
        return data
  
    

port =os.getenv('PORT',5000)
if __name__ == '__main__':
    app.run(host ="0.0.0.0",port=port)
