from flask import Flask, render_template, jsonify, request
import os
import json
from models import db, Food, Mood, User

app = Flask(__name__)
# Database Config
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'smartdine.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ... (Database Config remains) ...
app.config['SECRET_KEY'] = 'your-secret-key-change-this' # Required for sessions

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    # ... (Same init_db logic) ...
    # Ensure instance folder exists
    with app.app_context():
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db.create_all()
        if Mood.query.first() is None:
            print("Database empty. Migrating data from JSON...")
            migrate_data()

# ... (migrate_data remains same) ...

# Initialize DB on startup
init_db()

@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('discover'))
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    from flask import redirect, url_for, flash
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            # In a real app, use flash messages
            return "Username already exists"
            
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('discover'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    from flask import redirect, url_for
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('discover'))
        else:
            return "Invalid credentials" # Ideally, flash message
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/discover')
@login_required
def discover():
    return render_template('index.html', user=current_user)

@app.route('/api/moods')
# ... (rest of API remains) ...

@app.route('/api/moods')
def get_moods():
    moods = Mood.query.all()
    # Frontend expects specific list structure? Or just names?
    # Previous implementation sent keys of json object.
    return jsonify([m.name for m in moods])

@app.route('/api/search')
def search():
    mood_param = request.args.get('mood', '').lower()
    
    # 1. Get Keywords for the Mood
    target_keywords = []
    if mood_param:
        mood = Mood.query.filter_by(name=mood_param).first()
        if mood:
            target_keywords = mood.keywords.split(',')
    
    # Prepare base query
    if not target_keywords:
        results = Food.query.limit(20).all()
        scored_results = [(f, 0) for f in results]
    else:
        # 2. Score Foods based on connections
        all_foods = Food.query.all()
        scored_results = []
        
        for food in all_foods:
            food_keywords = set(food.keywords.split(',')) if food.keywords else set()
            overlap = len(food_keywords.intersection(target_keywords))
            if overlap > 0:
                scored_results.append((food, overlap))
        
        # Sort by overlap desc
        scored_results.sort(key=lambda x: x[1], reverse=True)
        scored_results = scored_results[:20]

    # 3. Format Response with Favorites status
    final_results = []
    user_fav_ids = set()
    if current_user.is_authenticated:
        user_fav_ids = {f.id for f in current_user.favorites}

    for food, score in scored_results:
        food_dict = food.to_dict()
        food_dict['is_favorite'] = food.id in user_fav_ids
        final_results.append(food_dict)
    
    return jsonify(final_results)

@app.route('/api/favorite/<int:food_id>', methods=['POST'])
@login_required
def toggle_favorite(food_id):
    food = Food.query.get_or_404(food_id)
    if food in current_user.favorites:
        current_user.favorites.remove(food)
        action = 'removed'
    else:
        current_user.favorites.append(food)
        action = 'added'
    db.session.commit()
    return jsonify({'status': 'success', 'action': action})

@app.route('/api/favorites')
@login_required
def get_favorites():
    favs = [f.to_dict() for f in current_user.favorites]
    for f in favs:
        f['is_favorite'] = True
    return jsonify(favs)

@app.route('/order/<int:food_id>')
@login_required
def order_page(food_id):
    food = Food.query.get_or_404(food_id)
    return render_template('order_confirmation.html', food=food)

@app.route('/api/surprise')
@login_required
def surprise_me():
    import random
    all_foods = Food.query.all()
    if not all_foods:
        return jsonify({'error': 'No foods found'}), 404
        
    random_food = random.choice(all_foods)
    food_dict = random_food.to_dict()
    
    # Check favorite status
    if current_user.is_authenticated:
        food_dict['is_favorite'] = random_food in current_user.favorites
        
    return jsonify(food_dict)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
