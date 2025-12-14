from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for Many-to-Many relationship between Food and Mood
food_mood_association = db.Table('food_mood',
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True),
    db.Column('mood_id', db.Integer, db.ForeignKey('mood.id'), primary_key=True)
)

from flask_login import UserMixin

# ... (association table code remains same) ...

# Association table for User favorites
user_favorites = db.Table('user_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False) # In real app, hash this!
    
    # Relationship to favorite foods
    favorites = db.relationship('Food', secondary=user_favorites, backref=db.backref('favorited_by', lazy='dynamic'))

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # We store keywords as a simple JSON string or comma-separated string for simplicity if not using a separate Tag model
    # But strictly speaking, the simplified requirement was just keywords. 
    # Let's keep keywords as a string field for simple search logic matching the previous JSON structure.
    keywords = db.Column(db.String(500), nullable=True) 

    # Relationship to moods
    moods = db.relationship('Mood', secondary=food_mood_association, backref=db.backref('foods', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'keywords': self.keywords.split(',') if self.keywords else []
        }

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # Keywords associated with the mood itself (e.g. Happy -> ["sweet", "party"])
    keywords = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'keywords': self.keywords.split(',') if self.keywords else []
        }
