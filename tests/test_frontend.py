from authorization_server import models
from authorization_server.app import db, bcrypt
from authorization_server.frontend import forms
from authorization_server.frontend.views import LOGIN_ERROR_MESSAGE


def test_registration_form(frontend_app):
    '''Test the registration form as follows:

    1) Registration page is served at /register
    2) When all required fields are sent and they have the right format => users are redirected to login
    3) If any required field is missing or invalid => form should be invalid and error shown
        3.1) Required fields
        3.2) Email is invalid
        3.3) Email already exists
        3.4) Password is invalid
        3.5) Confirmed Password is not equal to Password
    '''

    # (1)
    response = frontend_app.get('/register')
    assert response.status_code == 200
    assert 'Sign Up' in response.get_data(as_text=True)

    # (2)
    data = {'firstname': 'John',
            'lastname': 'Doe',
            'email': 'validemail@example.com',
            'password': 'password',
            'confirm_password': 'password'}
    response = frontend_app.post('/register', data=data, follow_redirects=True)
    # --> Ensure record has been stored in database and password is encrypted
    db_data = db.session.query(models.User).one()
    assert bcrypt.check_password_hash(db_data.password, data['password'])
    # --> User is redirected to login page
    assert response.status_code == 200
    assert 'Sign In' in response.get_data(as_text=True)
    # -> Clean after me
    db.session.query(models.User).delete()
    db.session.commit()
    assert not db.session.query(models.User).first()

    # (3.1)
    original_value = data['firstname']
    data['firstname'] = ''
    response = frontend_app.post('/register', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert 'field is required' in response.get_data(as_text=True)

    # (3.2)
    data['firstname'] = original_value
    original_value = data['email']
    data['email'] = 'this is not a valid email'
    response = frontend_app.post('/register', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert forms.INVALID_EMAIL_ERROR in response.get_data(as_text=True)

    # (3.3)
    # --> Insert a record in database
    data['email'] = original_value
    db_data = dict(data)
    del db_data['confirm_password']
    db.session.add(models.User(**db_data))
    db.session.commit()
    assert db.session.query(models.User).one()

    response = frontend_app.post('/register', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert forms.EMAIL_EXIST_ERROR in response.get_data(as_text=True)
    db.session.query(models.User).delete()
    db.session.commit()
    assert not db.session.query(models.User).first()

    # (3.3)
    original_value = data['password']
    data['password'] = '123456'
    response = frontend_app.post('/register', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert forms.INVALID_PASSWORD_ERROR in response.get_data(as_text=True)

    # (3.5)
    data['password'] = original_value
    original_value = data['confirm_password']
    data['confirm_password'] = '123456'
    response = frontend_app.post('/register', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert forms.DIFFERENT_PASSWORD_ERROR in response.get_data(as_text=True)


def test_login_logout(frontend_app):
    '''Test the login and logout screens as follows:

    1) Login is served at /login
    2) if provided email does not exist => show login error
    3) if email exist but password is wrong => show login error
    4) if both email and password are correct => redirect to /profile page
    5) if user is logged in and click logout => user should be logged out
    6) if email/password is invalid or missing => show form error
    '''
    assert not db.session.query(models.User).first()

    # (1)
    response = frontend_app.get('/login')
    assert response.status_code == 200
    assert 'Sign In' in response.get_data(as_text=True)

    # (2)
    data = {'email': 'emailnotindb@example.com',
            'password': 'password'}
    response = frontend_app.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert LOGIN_ERROR_MESSAGE in response.get_data(as_text=True)

    # (3)
    user = models.User(email='johndoe@gmail.com', password=bcrypt.generate_password_hash('password'))
    db.session.add(user)
    db.session.commit()
    assert db.session.query(models.User).first()
    data['email'] = user.email
    data['password'] = 'somethingelse'
    response = frontend_app.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert LOGIN_ERROR_MESSAGE in response.get_data(as_text=True)

    # (4)
    data['password'] = 'password'
    response = frontend_app.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Account Details' in response.get_data(as_text=True)
    with frontend_app.session_transaction() as session:
        assert 'user_id' in session

    # (5)
    response = frontend_app.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    with frontend_app.session_transaction() as session:
        assert 'user_id' not in session

    # (6.1)
    # ---> Invalid field - email
    data['email'] = 'invalid email'
    response = frontend_app.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert forms.INVALID_EMAIL_ERROR in response.get_data(as_text=True)

    # (6.2)
    # Missing field - password
    data['email'] = 'validemail@example.com'
    del data['password']
    response = frontend_app.post('/login', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert forms.INVALID_PASSWORD_ERROR in response.get_data(as_text=True)
