from flask import Flask, render_template, request, redirect, flash,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from models import db, RecruitModel, ProspectModel, HighSchoolModel, User, Watchlist
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db.init_app(app)
app.config['SECRET_KEY'] = 'totally_secret_key'

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('view_prospects'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken')
            return redirect(url_for('register'))
        
        # Create new user and add to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful, please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/populatehs')
@login_required
def populate_hs():
    highschools = [
        HighSchoolModel(name='IMG Academy'),
        HighSchoolModel(name='Montverde'),
        HighSchoolModel(name='Logansport'),
        HighSchoolModel(name='La Salle'),
        HighSchoolModel(name='West Lafayette'),
        HighSchoolModel(name='McCutcheon'),
        HighSchoolModel(name='Army'),
        HighSchoolModel(name='Luminare'),
        HighSchoolModel(name='Purdue Prep'),
        HighSchoolModel(name='Indiana Prep')
    ]
    db.session.bulk_save_objects(highschools)
    db.session.commit()
    return 'populated'


@app.route('/prospects')
@login_required
def view_prospects():
    prospects = ProspectModel.query.all()
    return render_template('view_prospects.html', prospects=prospects)

@app.route('/add/prospect', methods=['GET', 'POST'])
@login_required
def add_prospect():
    if request.method == 'POST':
        highschool_id = request.form['highschool_id']
        overall = request.form['overall']
        potential = request.form['potential']
        name = request.form['name']
        
        new_prospect = ProspectModel(name=name, highschool_id=highschool_id, overall=overall, potential=potential)
        db.session.add(new_prospect)
        db.session.commit()
        
        return redirect(url_for('view_prospects'))
    return render_template('add_prospect.html')

@app.route('/edit/prospect/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_prospect(id):
    prospect = ProspectModel.query.get_or_404(id)
    if request.method == 'POST':
        prospect.overall = request.form['overall']
        prospect.potential = request.form['potential']
        db.session.commit()
        return redirect(url_for('view_prospects'))
    return render_template('edit_prospect.html', prospect=prospect)

@app.route('/remove/prospect/<int:id>')
@login_required
def remove_prospect(id):
    prospect_to_remove = ProspectModel.query.get_or_404(id)
    db.session.delete(prospect_to_remove)
    db.session.commit()
    
    return redirect(url_for('view_prospects'))

@app.route('/query_prospects', methods=['GET'])
@login_required
def query_prospects():
    highschools = HighSchoolModel.query.all()
    return render_template('query_prospects.html', highschools=highschools)

@app.route('/handle_query', methods=['POST','GET'])
@login_required
def handle_query():
    min_overall = int(request.form.get('min_overall', 0))
    min_potential = int(request.form.get('min_potential', 0))
    highschool_id = request.form.get('highschool')

    query = ProspectModel.query
    if min_overall > 0:
        query = query.filter(ProspectModel.overall >= min_overall)
    if min_potential > 0:
        query = query.filter(ProspectModel.potential >= min_potential)
    if highschool_id:
        query = query.filter(ProspectModel.highschool_id == highschool_id)

    prospects = query.all()
    return render_template('report_results.html', prospects=prospects)


@app.route('/add_to_watchlist/<int:prospect_id>')
@login_required
def add_to_watchlist(prospect_id):
    new_entry = Watchlist(user_id=current_user.id, prospect_id=prospect_id)
    db.session.add(new_entry)
    db.session.commit()
    flash('Prospect added to watchlist.')
    return redirect(request.referrer)

@app.route('/view_watchlist')
@login_required
def view_watchlist():
    user_watchlist = Watchlist.query.filter_by(user_id=current_user.id).all()
    return render_template('view_watchlist.html', watchlist=user_watchlist)

@app.route('/remove_from_watchlist/<int:id>', methods=['POST'])
@login_required
def remove_from_watchlist(id):
    Watchlist.query.filter_by(id=id, user_id=current_user.id).delete()
    db.session.commit()
    flash('Removed from watchlist.')
    return redirect(url_for('view_watchlist'))










if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=False)