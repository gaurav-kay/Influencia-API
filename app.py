import firebase_admin
from flask import Flask, request, jsonify
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('./influencia.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client(default_app)

app = Flask(__name__)

#
@app.route('/register_influencer', methods=['POST'])
def register_influencer():
    influencer_tags = request.json['tags']
    influencer_tags = set(influencer_tags)

    for brand_doc_ref in db.collection('brands').stream():
        brand_tags_set = set(brand_doc_ref.to_dict())

        db\
            .collection('influencers')\
            .document(request.json[''])
