import sys

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

sys.path.append('.')
from biblio.models import Livro, session

app = Flask(__name__)

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# Flask and Flask-SQLAlchemy initialization here
admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(ModelView(Livro, session))

app.run(threaded=False)
