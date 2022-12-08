from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from passlib.hash import sha256_crypt
from .models import User


def invalid_credentials(form, field):
    """ StudentID and password checker """

    password = field.data
    student_id = form.student_id.data

    # Check student_id is invalid
    user_data = User.query.filter_by(student_id=student_id).first()
    if user_data is None:
        raise ValidationError("잘못된 아이디 또는 비밀번호입니다.")

    # Check password in invalid
    elif not sha256_crypt.verify(password, user_data.password):
        raise ValidationError("잘못된 아이디 또는 비밀번호입니다.")


class RegistrationForm(FlaskForm):
    """ Registration form"""

    student_id = StringField('student_id', validators=[InputRequired(message="아이디는 필수 입력사항입니다!"), Length(
        min=4, max=25, message="아이디는 4~25자 사이여야 합니다.")])
    name = StringField('name', validators=[
                       InputRequired(message="이름는 필수 입력사항입니다!")])
    phone_number = StringField('phone_number', validators=[
        InputRequired(message="전화번호는 필수 입력사항입니다!"), Length(
            min=11, max=12, message="아이디는 11~12자 사이여야 합니다.")])
    school_name = StringField('school_name', validators=[
                       InputRequired(message="학교는 필수 입력사항입니다!")])
    grade = StringField('grade', validators=[
                       InputRequired(message="학년는 필수 입력사항입니다!")])
    class_no = StringField('class_no', validators=[
                       InputRequired(message="반는 필수 입력사항입니다!")])
    password = PasswordField('password', validators=[InputRequired(message="비밀번호는 필수 입력사항입니다!"), Length(
        min=4, max=8, message="아이디는 4~8자 사이여야 합니다.")])

    def validate_student_id(self, student_id):
        user_object = User.query.filter_by(student_id=student_id.data).first()
        if user_object:
            raise ValidationError(
                "사용자가 이미 존재 합니다")


class LoginForm(FlaskForm):
    """ Login form """

    student_id = StringField('student_id', validators=[
        InputRequired(message="아이디는 필수 입력사항입니다!")])
    password = PasswordField('password', validators=[InputRequired(
        message="비밀번호는 필수 입력사항입니다!"), invalid_credentials])
