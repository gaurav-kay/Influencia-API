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

    # Extract keywords and add compat

    text = request.args['text'].lower()
    r = rake_nltk.Rake()
    r.extract_keywords_from_text(text)
    influencer_tags_set = set(list(r.get_ranked_phrases()))
    most_used_word_tag = list(r.get_ranked_phrases_with_scores())[0]

    print(influencer_tags_set)

    db.collection('influencers').document(request.args['influencer_id']).set({
        'tags': list(influencer_tags_set),
        'most_used_word': str(most_used_word_tag)
    }, merge=True)

    for brand_doc_ref in db.collection('brands').stream():
        brand_tags_set = set(list(brand_doc_ref.to_dict()['tags']))

        db \
            .collection('compat') \
            .document(brand_doc_ref.id + "&" + request.args['influencer_id']) \
            .set({
                'common_tags': list(brand_tags_set.intersection(influencer_tags_set)),
                'score': 100
                        if len(influencer_tags_set.intersection(brand_tags_set)) == len(brand_tags_set)
                        else len(influencer_tags_set.intersection(brand_tags_set)) * 100 / len(brand_tags_set)
            })

    return jsonify({'tags_extracted': str(influencer_tags_set), 'user': 'influencer', 'most_used_word': most_used_word_tag})


"""
api args request requirements
    tags,
    brand_id
"""
@app.route('/register_brand', methods=['POST'])
def register_brand():
    text = request.args['text'].lower()
    r = rake_nltk.Rake()
    r.extract_keywords_from_text(text)
    brands_tags_set = set(list(r.get_ranked_phrases()))
    most_used_word_tag = list(r.get_ranked_phrases_with_scores())[0]

    print("Tags extracted from the description", brands_tags_set)

    db.collection('brands') \
        .document(request.args['brand_id']) \
        .set({
            'tags': list(brands_tags_set),
            'most_used_word': str(most_used_word_tag)
        }, merge=True)

    return jsonify({'tags_extracted': str(brands_tags_set), 'user': 'brand', 'most_used_word': most_used_word_tag})


@app.route('/compat', methods=['GET'])
def compat():
    influencers = []
    for computed in db.collection('compat').stream():
        if computed.id.split('&')[0] == request.args['brand_id']:
            try:
                influencers.append(
                    [computed.id.split('&')[1], computed.to_dict()['score'], computed.to_dict()['most_used_word']]
                )
            except Exception or IndexError:
                influencers.append(
                    [computed.id.split('&')[1], computed.to_dict()['score']]
                )
    result = []
    for i in influencers:
        result.append(i)

    try:
        return jsonify({'result': str(result), 'most_used_word': str(result[2])})
    except Exception or KeyError:
        return jsonify({'result': str(result)})


if __name__ == '__main__':
    app.run(debug=True)
