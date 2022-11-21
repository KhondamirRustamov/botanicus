from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_required, current_user, login_user, logout_user
from random import randint
from datetime import datetime
from PIL import Image
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sih4b2h604081531'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


class Flora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family = db.Column(db.Text)
    familyru = db.Column(db.Text)
    genus = db.Column(db.Text)
    body = db.Column(db.Text)
    rod = db.Column(db.Text)
    spec = db.Column(db.Text)
    ipni = db.Column(db.Text)
    russian = db.Column(db.Text)
    uzbek = db.Column(db.Text)
    synonim = db.Column(db.Text)
    lifestyle = db.Column(db.Text)
    area = db.Column(db.Text)
    areal = db.Column(db.Text)
    uzbekistan = db.Column(db.Text)
    endemism = db.Column(db.Text)
    status = db.Column(db.Text)
    using = db.Column(db.Text)
    comment = db.Column(db.Text)

    def __repr__(self):
        return '<Flora %r>' % self.id


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    year_birth  = db.Column(db.String(100))
    sex = db.Column(db.String(100))
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000))
    rendered_data = db.Column(db.Text, nullable=False)  # Data to render the pic in browser
    text = db.Column(db.Text)
    pic_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.Column(db.Integer, nullable=False)
    species = db.Column(db.Text, nullable=False)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('profile'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    year = request.form.get('year')
    sex = request.form.get('sex')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'),
                    year_birth = year, sex = sex)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    species = Photo.query.filter_by(user=str(current_user.id))
    return render_template('profile.html', name=current_user.name, photo=species)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route('/')
def main():
    if current_user:
        try:
            name = current_user.name
        except AttributeError:
            name = 'unlogged'
    return render_template('main.html', name=name)


@app.route('/jamoamiz', methods=['POST', 'GET'])
def team():
    text=''
    if request.method == 'POST':
        text='Mana'
        return render_template('team.html', text=text)
    else:
        return render_template('team.html', text=text)


@app.route('/donate')
def donate():
    return render_template('donate.html')


@app.route('/report')
def report():
    return render_template('report.html')


def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic


@app.route('/upload')
def upload_get():
    if current_user:
        try:
            name = current_user.name
        except AttributeError:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    floras = Flora.query.all()
    return render_template('upload_image.html', floras=floras)


@app.route('/upload', methods=['POST'])
def upload():
     if current_user:
        try:
            name = current_user.name
        except AttributeError:
            return redirect(url_for('login'))
     else:
        return redirect(url_for('login'))
     file = request.files['inputFile']

     data = file.read()
     render_file = render_picture(data)
     text = request.form['text']
     #location = request.form['location']
     species = request.form['species']

     newFile = Photo(name=file.filename, rendered_data=render_file, text=text,
                     species = species, user = current_user.id)
     img = Image.open(file)
     if img.size[0] != 720 and img.size[1] != 480:
         flash('Image should have 720*480 size')
         return redirect(url_for('upload'))
     db.session.add(newFile)
     db.session.commit()
     species = Flora.query.filter_by(spec=str(species))
     return redirect(url_for('flora_id', id = species[0].id))


@app.route('/flora-uz', methods=['POST', 'GET'])
def flora():
    species = ''
    spec = []
    a = ''
    b = ''
    d = ''
    text = ''
    floras = Flora.query.all()

    if request.method == 'POST':
        species = ["Ushbu tur O'zbekiston florasida uchramaydi"]

        text = str(request.form['text'])

        method = str(request.form['metod'])
        if method == 'Tur nomi (lotin)':

            for i in floras:
                if str(text).lower() in str(i.spec).lower() or str(text).lower() in str(i.synonim).lower():
                        a = '000'
                        spec.append(i)

                        '''
                        v = '+'.join(str(i.spec).split(' ')[:2])
                        r1 = str('http://www.theplantlist.org/tpl/search?q=' + v)
                        r2 = str('http://apps.kew.org/herbcat/getHomePageResults.do?homePageSearchText=' + v)
                        r3 = str('https://www.ncbi.nlm.nih.gov/search/all/?term=' + v)
                        r4 = str('https://www.gbif.org/species/search?via=data.gbif.org&dataset_key=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&q=' + v)
                        r5 = str('https://www.google.com/search?q=%22{}%22&tbm=isch'.format(v))
                        r = r1, r2, r3, r4, r5'''

            if len(spec)==0:
                a=''
                b=''
                d = '00'
                text = None, text
                return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)
            else:
                text = None, text
                return render_template('flora.html', spec=spec, a=a, b=b, text=text, d=d)
            '''
            except:
                d= '00'
                a=''
                b=''
                return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)'''

        elif method == 'Tur nomi (rus)':
            try:
                for i in floras:
                    if text.lower() in str(i.russian).lower():
                        a = '00'
                        species = Flora.query.get(i.id)
                        text = None, text
                        v = '+'.join(str(species.spec).split(' ')[:2])
                        r1 = str('http://www.theplantlist.org/tpl/search?q=' + v)
                        r2 = str('http://apps.kew.org/herbcat/getHomePageResults.do?homePageSearchText=' + v)
                        r3 = str('https://www.ncbi.nlm.nih.gov/search/all/?term=' + v)
                        r4 = str('https://www.gbif.org/species/search?via=data.gbif.org&dataset_key=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&q=' + v)
                        r5 = str('https://www.google.com/search?q=%22{}%22&tbm=isch'.format(v))
                        r = r1, r2, r3, r4, r5
                        return render_template('flora.html', spec=species, a=a, b=b, text=text, d=d, r=r)
                    else:
                        if i.id >= 4414:
                            d = '00'
                            text = None, text
                            return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)
            except:
                d = '000'
                return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)

        elif method == "Tur nomi (o'zbek)":
            try:
                for i in floras:
                    if text.lower() in str(i.uzbek).lower():
                        a = '00'
                        species = Flora.query.get(i.id)
                        text = None, text
                        v = '+'.join(str(species.spec).split(' ')[:2])
                        r1 = str('http://www.theplantlist.org/tpl/search?q=' + v)
                        r2 = str('http://apps.kew.org/herbcat/getHomePageResults.do?homePageSearchText=' + v)
                        r3 = str('https://www.ncbi.nlm.nih.gov/search/all/?term=' + v)
                        r4 = str('https://www.gbif.org/species/search?via=data.gbif.org&dataset_key=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&q=' + v)
                        r5 = str('https://www.google.com/search?q=%22{}%22&tbm=isch'.format(v))
                        r = r1, r2, r3, r4, r5
                        return render_template('flora.html', spec=species, a=a, b=b, text=text, d=d, r=r)
                    else:
                        if i.id >= 4414:
                            d = '00'
                            text = None, text
                            return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)
            except:
                d = '00'
                return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)

        elif method == "Turkum nomi (lotin)":
            try:
                for i in floras:
                    if text.lower() in str(i.genus).lower():
                        b = '00'
                        species = Flora.query.filter_by(genus=str(Flora.query.get(i.id).genus))
                        text = 'Turkum:', text
                        c = species.count()
                        return render_template('flora.html', spec=species, a=a, b=b, text=text, c=c, d=d)
                    else:
                        if i.id >= 4414:
                            d = '00'
                            text = 'Turkum:', text
                            return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)
            except:
                d = '00'
                return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)

        elif method == "Turkum nomi (rus)":
            try:
                for i in floras:
                    if text.lower() == str(i.rod).lower():
                        b = '00'
                        species = Flora.query.filter_by(genus=str(Flora.query.get(i.id).genus))
                        c = species.count()
                        text = 'Turkum:', text
                        return render_template('flora.html', spec=species, a=a, b=b, text=text, c=c, d=d)
                    else:
                        if i.id >= 4414:
                            d = '00'
                            text = 'Turkum:', text
                            return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)
            except:
                d = '00'
                return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)

        elif method == "Oila nomi (lotin)":
            try:
                for i in floras:
                    if text.lower() in str(i.family).lower():
                        b = '00'
                        species = Flora.query.filter_by(family=str(Flora.query.get(i.id).family))
                        text = 'Oila:', text
                        c = species.count()
                        return render_template('flora.html', spec=species, a=a, b=b, text=text, c=c, d=d)
                    else:
                        if i.id >= 4414:
                            d = '00'
                            text = 'Oila:', text
                            return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)
            except:
                d = '00'
                return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)

        elif method == "Oila nomi (rus)":
            try:
                for i in floras:
                    if text.lower() in str(i.familyru).lower():
                        b = '00'
                        species = Flora.query.filter_by(family=str(Flora.query.get(i.id).family))
                        text = 'Oila:', text
                        c = species.count()
                        return render_template('flora.html', spec=species, a=a, b=b, text=text, c=c, d=d)
                    else:
                        if i.id >= 4414:
                            d = '00'
                            text = 'Oila:', text
                            return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)
            except:
                d = '00'
                return render_template('flora.html', spec=species, a=a, b=b, d=d, text=text)

    else:
        z = []
        for i in range(9):
            z1 = Flora.query.get(randint(0, 4413))
            z.append(z1)
        return render_template('flora.html', spec=species, a=a, b=b, z=z, d=d, text=text)


@app.route('/flora-uz/<int:id>')
def flora_id(id):
    species = Flora.query.get(id)
    photo = Photo.query.filter_by(species=str(species.spec))
    a = '00'
    v = '+'.join(str(species.spec).split(' ')[:2])
    r1 = str('http://www.theplantlist.org/tpl/search?q=' + v)
    r2 = str('http://apps.kew.org/herbcat/getHomePageResults.do?homePageSearchText=' + v)
    r3 = str('https://www.ncbi.nlm.nih.gov/search/all/?term=' + v)
    r4 = str(
        'https://www.gbif.org/species/search?via=data.gbif.org&dataset_key=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c&q=' + v)
    r5 = str('https://www.google.com/search?q=%22{}%22&tbm=isch'.format(v))
    r = r1, r2, r3, r4, r5
    return render_template('flora_id.html', spec=species, a=a, r=r, photo=photo)


@app.route('/photo_id/<int:id>')
def photo_id(id):
    photo = Photo.query.get(id)
    a = '00'

    return render_template('photo_id.html', a=a, photo=photo)


if __name__ == "__main__":
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    app.run(debug=True)