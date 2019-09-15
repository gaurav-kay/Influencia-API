import firebase_admin
import rake_nltk
from flask import Flask, request, jsonify
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('./influencia.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client(default_app)

app = Flask(__name__)

"""
api args request requirements:
    text, as a comma separated string
    influencer_id
"""
@app.route('/register_influencer', methods=['POST'])
def register_influencer():
    text = request.json['text']
    r = rake_nltk.Rake()
    r.extract_keywords_from_text(text)
    influencer_tags_set = set(list(r.get_ranked_phrases()))
    # influencer_tags_set = set(list(str(request.json['text']).split(',')))

    # for brand_doc_ref in db.collection('brands').stream():
    #     brand_tags_set = set(list(brand_doc_ref.to_dict()['tags']))
    #
    #     db \
    #         .collection('influencers') \
    #         .document(request.args['influencer_id']) \
    #         .collection('score') \
    #         .document(brand_doc_ref.id + '&' + request.args['influencer_id']) \
    #         .set({
    #             'common_tags': list(brand_tags_set.intersection(influencer_tags_set)),
    #             'score': 100
    #                     if len(influencer_tags_set.intersection(brand_tags_set)) == 0
    #                     else len(influencer_tags_set.intersection(brand_tags_set)) * 100 / len(brand_tags_set)
    #         })
    for brand_doc_ref in db.collection('brands').stream():
        brand_tags_set = set(list(brand_doc_ref.to_dict()['tags']))

        # influencer_tags_set = set(list(str(request.args['tags']).split(',')))

        db \
            .collection('compat') \
            .document(brand_doc_ref.id + "&" + request.json['influencer_id']) \
            .set({
                'common_tags': list(brand_tags_set.intersection(influencer_tags_set)),
                'score': 100
                        if len(influencer_tags_set.intersection(brand_tags_set)) == 0
                        else len(influencer_tags_set.intersection(brand_tags_set)) * 100 / len(brand_tags_set)
            })

    return jsonify({'status': 'registered'})


"""
api args request requirements
    tags,
    brand_id
"""
# @app.route('/register_brand', methods=['POST'])
# def register_brand():
#     brands_tags_set = set(list(str(request.data['tags'])))
@app.route('/register_brand', methods=['POST'])
def register_brand():
    text = request.json['text']
    r = rake_nltk.Rake()
    r.extract_keywords_from_text(text)
    brands_tags_set = set(list(r.get_ranked_phrases()))

    db.collection('brands') \
        .document(request.json['brand_id']) \
        .set({
            'tags': list(brands_tags_set)
        }, merge=True)


# @app.route('/compatibility', methods=['GET'])
# def check_compat():
#     brand = request.args['brand']
#
#     for brand_influencer in db.collection('compat').stream():
#         brand, influencer = brand_influencer.id.split('&')[:2]
#


if __name__ == '__main__':
    app.run(debug=True)
