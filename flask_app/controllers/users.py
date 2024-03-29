from flask_app import app
from flask import render_template, redirect, request, session, jsonify
from flask_app.models.user import User
from flask_app.models.ride import Ride
from flask_app.models.rate import Rate
from flask_app.models.comment import Comment
from flask_app.models.message import Message
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS, cross_origin

bcrypt = Bcrypt(app)
server_session = Session(app)
CORS(app, supports_credentials=True)


@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        return redirect('/home')
    return render_template('index.html')

@app.route('/users/view/<int:profile_id>/<int:ride_id>')
def view_profile(profile_id, ride_id):
    user_id = session.get('user_id')
    if user_id:
        logged_user = User.get_by_id({'id' : session['user_id']})
        user_profile = User.get_by_id({'id' : profile_id})
        created_rides = Ride.get_created_rides({'id' : profile_id})
        comments = Comment.getAllByProfile({'id' : profile_id})
        rate = Rate.getAvgRate({'id' : profile_id})
        all_raters_id = Rate.get_profile_raters_id({'profile_id' : profile_id})
        actual_rate = Rate.get_rater_profile_rate({'rater_id' : session['user_id'], 'profile_id' : profile_id})
        countMessages = Message.countActifMessagesForUser({'id' : session['user_id']})
        actifMessages = Message.showActifMessagesForUser({'id' : session['user_id']})
        UserCount_rides = Ride.countCreatedRidesForUser({'id' : session['user_id']})
        count_rides = Ride.countCreatedRidesForUser({'id' : profile_id})
        if actual_rate:
            this_actual_rate = actual_rate[0]['rate']
        else:
            this_actual_rate = None
        raters_ids = []
        for rater_id in all_raters_id:
            raters_ids.append(rater_id['rater_id'])
        return render_template('view_profile.html', user = logged_user, ride_id = ride_id, rides = created_rides, profile = user_profile, comments = comments, rate = rate, raters_ids = raters_ids, actual_rate = this_actual_rate, countMessages=countMessages, messages=actifMessages, count_rides=count_rides, UserCount_rides=UserCount_rides)
    return render_template('login.html')


@app.route('/home')
def home():
    user_id = session.get('user_id')
    if user_id:
        logged_user = User.get_by_id({'id' : session['user_id']})
        countMessages = Message.countActifMessagesForUser({'id' : session['user_id']})
        actifMessages = Message.showActifMessagesForUser({'id' : session['user_id']})
        count_rides = Ride.countCreatedRidesForUser({'id' : session['user_id']})
        return render_template('home.html', user = logged_user, countMessages = countMessages, messages = actifMessages, count_rides=count_rides)
    return render_template('login.html')


@app.route('/register')
def register():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('register.html')
    return redirect('/')


@app.route('/api/users/register', methods = ['POST'])
def create_user():
    errors = User.validate(request.form)
    if len(errors)==0:
        hashed_password = bcrypt.generate_password_hash(request.form['password'])
        data = {
                **request.form, 'password':hashed_password
            }
        session['user_id'] = User.save(data)
        return jsonify({'errors' : 'success'})
    return jsonify({'errors' : errors})


@app.route('/api/users')
def get_all():
    user_id = session.get('user_id')
    if user_id:
        all_users = User.get_all_users()
        return jsonify({'all_users' : all_users})
    return redirect('/')


@app.route('/api/users/login', methods = ['POST'])
def login():
    # data = request.get_json()
    user_from_db = User.get_by_email({'email' : request.form['email']})
    if user_from_db :
        if user_from_db.state == 0:
            if bcrypt.check_password_hash(user_from_db.password, request.form['password']):
                if user_from_db.role == 'admin':
                    session['admin'] = True
                    return jsonify({'message' : "admin"})
                session['user_id'] = user_from_db.id
                return jsonify({'message' : "success"})
        else:
            return jsonify({'message' : "Desactivated"})
    return jsonify({'message' : "Error"})


@app.route('/admin')
def admin():
    if session.get('admin'):
        all_users = User.get_all_users()
        admin = User.getAdmin()
        for user in all_users:
            user.rate = Rate.getAvgRate({'id' : user.id})
        return render_template('admin.html',admin = admin, users = all_users)
    return redirect('/')

@app.route('/admin/activate/<int:user_id>')
def activate(user_id):
    if session.get('admin'):
        User.activate({'id' : user_id})
        all_users = User.get_all_users()
        admin = User.getAdmin()
        for user in all_users:
            user.rate = Rate.getAvgRate({'id' : user.id})
        return render_template('admin.html',admin = admin, users = all_users)
    return redirect('/')

@app.route('/admin/desactivate/<int:user_id>')
def desactivate(user_id):
    if session.get('admin'):
        User.desactivate({'id' : user_id})
        all_users = User.get_all_users()
        admin = User.getAdmin()
        for user in all_users:
            user.rate = Rate.getAvgRate({'id' : user.id})
        return render_template('admin.html',admin = admin, users = all_users)
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')