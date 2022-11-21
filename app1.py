from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

import pandas

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.db'

db = SQLAlchemy(app)


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
    photo = db.Column(db.Text)
    photo_comment = db.Column(db.Text)
    desc_g = db.Column(db.Text)
    desc_s = db.Column(db.Text)

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


with app.app_context():
    db.create_all()
    table = pandas.read_excel('UzFl1.xlsx')
    df = pandas.DataFrame(table)
    #print(df.iloc[0])

    for i in range(4414):
        print(i)
        new_spec = Flora(family = df['FAMILY'][i], familyru = df['FAMILYRU'][i],
                            genus = df['GENUS'][i], body = 'FLORA',
                            rod = df['ROD'][i], spec = df['SPECIES'][i],
                            ipni = df['IPNI'][i], russian = df['RUSSIAN'][i],
                            uzbek = df['UZBEK'][i], synonim = df['SYNONIMS'][i],
                            lifestyle = df['LIFESTYLE'][i], area = df['AREA'][i],
                            areal = df['AREAL'][i], uzbekistan = df['UZBEKISTAN'][i],
                            endemism = df['ENDEMISM'][i], status = df['STATUS'][i],
                            using = df['USING'][i], comment = df['COMMENT'][i],
                            photo = df['image'][i], photo_comment = df['image_author'][i],
                            desc_g = df['Description_1'][i], desc_s = df['Description_2'][i])
        try:
            db.session.add(new_spec)
            db.session.commit()
        except Exception as exception:
            print(exception)

    print('all')

