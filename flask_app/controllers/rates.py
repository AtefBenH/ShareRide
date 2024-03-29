from flask_app import app
from flask import redirect, request, session
from flask_app.models.rate import Rate
from flask_session import Session

@app.route('/rates/create/<int:profile_id>/<int:user_id>', methods = ['POST'])
def rate(profile_id, user_id):
    if session.get('user_id'):
        data = {
            'profile_id' : profile_id,
            'rater_id' : user_id,
            'rate' : request.form['rate']
        }
        ride_id = request.form['ride_id']
        Rate.save(data)
        return redirect(f'/users/view/{profile_id}/{ride_id}')
    return redirect('/')



@app.route('/rates/update/<int:profile_id>/<int:user_id>/<int:ride_id>', methods = ['POST'])
def updaterate(profile_id, user_id, ride_id):
    if session.get('user_id'):
        data = {
            'profile_id' : profile_id,
            'rater_id' : user_id,
            'rate' : request.form['rate']
        }
        Rate.updaterate(data)
        return redirect(f'/users/view/{profile_id}/{ride_id}')
    return redirect('/')

