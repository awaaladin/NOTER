from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from . import mail
from .token import generate_token, confirm_token

auth = Blueprint('auth',__name__)


#login function
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)  # ✅ Safe to use here
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect email or password', category='error')
            
    return render_template("home.html")




#logout function
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



#signup function
@auth.route('/sign-up' , methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')


        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exist.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
             flash('Passwords must be greater than 7 characters.', category='error')
      
        else:
             new_user = User(email=email, firstName=firstName, lastName=lastName, password=generate_password_hash(password1, method='pbkdf2:sha256'))
             db.session.add(new_user)
             db.session.commit()
             login_user(new_user, remember=True)
             token = generate_token(email)
             confirm_url = url_for('auth.confirm_email', token=token, _external=True)
             msg = Message('Confirm Your Email', sender='your_email@gmail.com', recipients=[email])
             msg.body = f'Click the link to verify your account: {confirm_url}'
             mail.send(msg)
             flash('A confirmation email has been sent.', category='info')
             flash('Account Created Successfully!.', category='success')

        
        return redirect(url_for('views.home'))
            


    return render_template("sign_up.html",user=current_user)

@auth.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or expired.', category='error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if user and not user.is_verified:
        user.is_verified = True
        db.session.commit()
        flash('Email confirmed successfully!', category='success')
    else:
        flash('Account already confirmed.', category='info')

    return redirect(url_for('auth.login'))



@auth.route('/setup-profile', methods=['GET', 'POST'])
@login_required
def setup_profile():
    if request.method == 'POST':
        bio = request.form.get('bio')
        avatar_url = request.form.get('avatar_url')
        current_user.bio = bio
        current_user.avatar_url = avatar_url
        db.session.commit()
        flash('Profile updated!', category='success')
        return redirect(url_for('views.home'))

    return render_template('setup_profile.html', user=current_user)


