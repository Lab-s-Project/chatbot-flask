from .models import *
from .forms import *
from sqlalchemy import desc
from . import app
from .util import dbconn
from .chatbot import get_response
from flask import request, render_template, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from passlib.hash import sha256_crypt
# import pymysql
# pymysql.install_as_MySQLdb()


app.config['SQLALCHEMY_DATABASE_URI'] = dbconn.get_connection()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine_container = db.get_engine(app)

# Initialize login manager
login = LoginManager(app)
login.init_app(app)

# Close database connection
def clean_session():
    db.session.close()
    engine_container.dispose()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/register", methods=['GET', 'POST'])
def register():

    reg_form = RegistrationForm()

    # Update database if validation success
    if reg_form.validate_on_submit():
        student_id = reg_form.student_id.data
        type = "student"
        name = reg_form.name.data
        phone_number = reg_form.phone_number.data
        school_name = reg_form.school_name.data
        grade = reg_form.grade.data
        class_no = reg_form.class_no.data
        password = sha256_crypt.hash(reg_form.password.data)

        # Add new user to DB
        user = User(student_id=student_id, type=type, name=name, school_name=school_name,
                    phone_number=phone_number, grade=grade, class_no=class_no, password=password)
        db.session.add(user)
        db.session.commit()

        flash('계정을 만들었습니다. 로그인 해주세요.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=reg_form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    try:
        if not current_user.is_authenticated:
            login_form = LoginForm()

            # Allow login if validation success
            if login_form.validate_on_submit():
                user_object = User.query.filter_by(
                    student_id=login_form.student_id.data).first()
                login_user(user_object)

                return redirect(url_for('home'))

            return render_template("login.html", form=login_form)

        return redirect(url_for('home'))
    except Exception as e:
        print(e)
    finally:
        pass


@app.route("/logout", methods=['GET'])
def logout():

    # Logout user
    logout_user()
    flash('로그아웃이 잘 되었습니다', 'success')
    return redirect(url_for('login'))


@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    try:
        if not current_user.is_authenticated:
            flash('로그인 해주세요.', 'danger')
            clean_session()  # clear and close the session
            return redirect(url_for('login'))
        else:
            clean_session()  # clear and close the session
            
            return render_template("home.html")
    except Exception as e:
        print(e)
    finally:
        pass


@app.post("/predict")
def predict():

    user_id = current_user.get_id()
    text = request.get_json().get('message')

    # add message to the database
    storeMessage(user_id, "message", text)
    response = get_response(text)
    
    # add response to the database
    storeResponse(user_id, "response", response)

    # return response to UI
    answer = {"answer": response}
    return jsonify(answer)


def storeMessage(id, _type, text):
    user_id = id
    type = _type
    text = text

    chat = Chat(user_id=user_id, type=type, text=text)
    db.session.add(chat)
    db.session.commit()
    return None


def storeResponse(id, _type, text):
    user_id = id
    type = _type
    text = text

    chat = Chat(user_id=user_id, type=type, text=text)
    db.session.add(chat)
    db.session.commit()
    return None


@login_required
@app.get("/history")
def get_history():    
    try:
        if not current_user.is_authenticated:
            flash('로그인 해주세요.', 'danger')
            clean_session()  # clear and close the session
            return redirect(url_for('login'))
        else:
            user_id = current_user.get_id()
            history_filters = Chat.query.filter_by(user_id=user_id).order_by(Chat.created_at.asc()).all()
            
            convo = []
            for his in history_filters:
                type = his.type
                text = his.text
                created_at = his.created_at
                
                history = {"type": type, "text": text, "created_at": created_at}
                convo.append(history)
            
            clean_session()
            return jsonify(convo)
    
    except Exception as e:
        print(e)
    finally:
        pass


@login_required
@app.route("/profile", methods=['GET', 'POST'])
def profile():
    try:
        if not current_user.is_authenticated:
            flash('로그인 해주세요.', 'danger')
            clean_session()  # clear and close the session
            return redirect(url_for('login'))
        else:
            user_id = current_user.get_id()
            user = User.query.filter_by(id=user_id).first_or_404()
            
            clean_session()  # clear and close the session
            return render_template("profile.html", user=user)
    except Exception as e:
        print(e)
    finally:
        pass
    

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(405)
def method_not_found(e):
    return render_template("405.html")


@app.errorhandler(500)
def page_not_found(e):
    return ("Ouch, looks like we're knocked out"), 500
