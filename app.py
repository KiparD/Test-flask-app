from flask import Flask, render_template, request, flash, redirect, url_for
from wtforms import Form, StringField, validators
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import time

app = Flask(__name__)

# Config MySQL. For production we hide all passwords and names('config.cfg')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'my7new2sqlpass'
app.config['MYSQL_DB'] = 'searchapp'

# init MySQL
mysql = MySQL(app)

# Config Mail
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'admin admin'
app.config['MAIL_PASSWORD'] = 'simplepass'

# init Mail
mail = Mail(app)

# Search Form Class
class SearchForm(Form):
    search_text = StringField('Search Text', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])

# Search pannel and connection to DB
@app.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        start_time = time.time()
        search_text = form.search_text.data
        email = form.email.data

        # Message to user
        flash('Search started... The result will be send to %s.' % email, 'success')

        # Create cursor
        cur = mysql.connection.cursor()

        # Get results
        result = cur.execute("""SELECT * FROM books WHERE MATCH(chapter, body) AGAINST (%s IN NATURAL LANGUAGE MODE)""", [search_text])

        if result > 0:
            data = cur.fetchall()
            send = ''
            for i in range(result):
                send += str(i+1) + " Title: '%s', author: '%s', chapter: '%s', page: %s; \n" % (data[i][1], data[i][2], data[i][3], data[i][4])
            msg = Message(send, sender='spamgeneratorr@gmail.com', recipients=[email])
            mail.send(msg)
            flash("Results sent", 'success')
        else:
            flash("Your text isn't found in the database. Try again.", 'danger')

        # flash(send, 'success')

        # Close connection
        cur.close()
        log = time.time() - start_time

        return redirect(url_for('search'))

    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.secret_key='secret133'
    app.run(debug=True)
