from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'owner': self.owner
        }


with app.app_context():
    db.create_all()


@app.route('/ads', methods=['POST'])
def create_ad():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('description') or not data.get('owner'):
        return jsonify({'error': 'Нужны title, description, owner'}), 400

    ad = Advertisement(
        title=data['title'],
        description=data['description'],
        owner=data['owner']
    )
    db.session.add(ad)
    db.session.commit()
    return jsonify(ad.to_dict()), 201


@app.route('/ads/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404
    return jsonify(ad.to_dict()), 200


@app.route('/ads/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404
    db.session.delete(ad)
    db.session.commit()
    return jsonify({'message': 'Удалено'}), 200


@app.route('/ads/<int:ad_id>', methods=['PUT'])
def update_ad(ad_id):
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return jsonify({'error': 'Объявление не найдено'}), 404

    data = request.get_json()
    if data.get('title'):
        ad.title = data['title']
    if data.get('description'):
        ad.description = data['description']
    if data.get('owner'):
        ad.owner = data['owner']

    db.session.commit()
    return jsonify(ad.to_dict()), 200


if __name__ == '__main__':
    app.run(debug=True)