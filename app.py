import firebase_admin
from flask import Flask, request, jsonify
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('./influencia.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client(default_app)

app = Flask(__name__)

"""
api args request requirements:
    tags, as a comma separated string
    influencer_id
"""


@app.route('/register_influencer', methods=['POST'])
def register_influencer():
    influencer_tags_set = set(list(str(request.args['tags']).split(',')))

    for brand_doc_ref in db.collection('brands').stream():
        brand_tags_set = set(list(brand_doc_ref.to_dict()['tags']))

        db \
            .collection('influencers') \
            .document(request.args['influencer_id']) \
            .collection('score') \
            .document(brand_doc_ref.id + '-' + request.args['influencer_id']) \
            .set({
                'common_tags': list(brand_tags_set.intersection(influencer_tags_set)),
                'score': 100
                        if len(influencer_tags_set.intersection(brand_tags_set)) == 0
                        else len(influencer_tags_set.intersection(brand_tags_set)) * 100 / len(brand_tags_set)
            })

    return jsonify({'status': 'registered'})


if __name__ == '__main__':
    app.run(debug=True)
