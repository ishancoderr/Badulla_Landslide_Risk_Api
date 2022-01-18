from flask import Flask, render_template, jsonify, request
from shapely.geometry import shape, Point
import json
from flask_restful import Api,Resource
from flask_httpauth import HTTPBasicAuth

# create the app
app = Flask(__name__)
api = Api(app)
app.config['JSON_SORT_KEYS'] = False
auth = HTTPBasicAuth()

USER_DATA={
    "cifra":"CifraSecret"
}

@auth.verify_password
def verify(username, password):
   if not (username and password):
       return False
   return USER_DATA.get(username) == password

class endpoint(Resource):
   @auth.login_required
   def get(self):
       lon = request.args.get('lon')
       lat = request.args.get('lat')
       # buf_dist=request.args.get('buf-dist')

       error_res = {}
       polygon_risk = {}

       # arguments passed from the API are strings
       try:
           lon = float(lon)
       except ValueError:
           error_res['longitude error'] = 'lon argument should be numeric'
           error_res['value given'] = lon
           return jsonify(error_res)

       # check if lon is out of range
       if lon < -180.0 or lon > 180.0:
           error_res['longitude error'] = 'lon argument value out of range. It shoud be between -180.0 and 180.0'
           error_res['value given'] = lon
           return jsonify(error_res)

       # check if lat argument value is valid as numeric
       # arguments passed from the API are strings
       try:
           lat = float(lat)
       except ValueError:
           error_res['latitude error'] = 'lat argument should be numeric'
           error_res['value given'] = lat
           return jsonify(error_res)

       # check if lat is out of range
       if lat < -90.0 or lat > 90.0:
           error_res['latitude error'] = 'lat argument value out of range. It shoud be between -90.0 and 90.0'
           error_res['value given'] = lat
           return jsonify(error_res)

       # load GeoJSON file containing sectors

       with open(r"E:\geo_api\app\riskmap\risk.json", "r") as f:
           js = json.load(f)

       point = Point(lon, lat)

       # check each polygon to see if it contains the point
       for feature in js['features']:
           polygon = shape(feature['geometry'])
           if polygon.contains(point):
               properties = feature['properties']
               polygon_risk['Location Risk'] = properties["value"]
               return jsonify(polygon_risk)
       else:
           polygon_risk['Location Risk'] = 'not your location in research area'
           return jsonify(polygon_risk)








api.add_resource(endpoint,'/buffer-point')

#http://127.0.0.1:5000/buffer-point?lon=80.997985&lat=6.829219


# rendering the index or entry using either of the 3 routes

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
	return render_template('index.html')

#the point Risk implementation

# main to run app
if __name__ == '__main__':
	app.run(debug = True, host="0.0.0.0",port=80)



