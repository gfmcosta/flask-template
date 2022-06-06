# from crypt import methods
# from jinja2 import TemplateNotFound
import email
from enum import unique
from mailbox import NotEmptyError
import re
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user



app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost:3306/shopdb'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost:3306/shopdb'
app.config['SECRET_KEY'] = 'IstoEUmaSecretKey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Roles(UserMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    descricao = db.Column(db.String(100), nullable=False)


class Categorias(UserMixin, db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    descricao = db.Column(db.String(250), nullable=False)


class Produtos(UserMixin, db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    descricao = db.Column(db.String(250), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(100), nullable=False)
    categoriaId = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    categorias = db.relationship("Categorias", backref=db.backref("categorias", uselist=False))


class Utilizadores(UserMixin, db.Model):
    __tablename__ = 'utilizadores'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)#unique=True
    roleId = db.Column(db.Integer, db.ForeignKey('roles.id'))
    roles = db.relationship("Roles", backref=db.backref("roles", uselist=False))


class Clientes(UserMixin, db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    nome = db.Column(db.String(100), nullable=True)
    morada = db.Column(db.String(100), nullable=True)
    utilizadorId = db.Column(db.Integer, db.ForeignKey('utilizadores.id'))
    utilizadores = db.relationship("Utilizadores", backref=db.backref("utilizadores"))


class Encomendas(UserMixin, db.Model):
    __tablename__ = 'encomendas'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    dataEncomenda = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total = db.Column(db.Float, nullable=False)
    clienteId = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    clientes = db.relationship("Clientes", backref=db.backref("clientes"))


class Linhas_encomenda(UserMixin, db.Model):
    __tablename__ = 'linhas_encomenda'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    quantidade = db.Column(db.Integer, nullable=False)
    encomendaId = db.Column(db.Integer, db.ForeignKey('encomendas.id'))
    encomendas = db.relationship("Encomendas", backref=db.backref("encomendas"))
    produtoId = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    produtos = db.relationship("Produtos", backref=db.backref("produtos"))



###################################################################################################



class LoginForm(FlaskForm):
    email = StringField('Email', render_kw={"placeholder": "Email"}, validators=[DataRequired(), Email(message='Email invalido'), Length(max=50)])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[DataRequired(), Length(min=3, max=80)])


class RegisterForm(FlaskForm):
    nome = StringField('Nome', render_kw={"placeholder": "Nome"}, validators=[DataRequired(), Length(min=3, max=12)])
    morada = StringField('Morada', render_kw={"placeholder": "Morada"}, validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', render_kw={"placeholder": "Email"}, validators=[DataRequired(), Email(message='Email invalido'), Length(max=50)])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[DataRequired(), Length(min=3, max=80)])


@login_manager.user_loader
def load_user(utilizadorId):
    return Utilizadores.query.get(int(utilizadorId))
 

@app.route('/', methods=['GET'])
def home():
    return render_template('inicio.html')


@app.route('/sobre', methods=['GET'])
def sobre():
    return render_template('sobre.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print("Entrou aqui")
    if form.validate_on_submit():
        user = Utilizadores.query.filter_by(email=form.email.data).first()
        print(user)
        if user:
            if user.password == form.password.data:
                login_user(user, remember=form.password.data)
                if(user.roleId==1):
                    return '<h1> Modo de Administrador </h1>'
                else:
                    return '<h1> Modo Cliente </h1>'
                #return redirect(url_for('dashboard'))
        
        return '<h1> Email invalido ou password errada! </h1>'

    return render_template('login.html', form=form)



@app.route('/registar', methods=['GET', 'POST'])
def registar():
    form = RegisterForm()

    print(form.validate_on_submit())
    if form.validate_on_submit():
        # hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = Utilizadores(email=form.email.data, password=form.password.data, roleId=2)
        db.session.add(new_user)
        db.session.commit()
        user = Utilizadores.query.filter_by(email=form.email.data).first()
        new_client = Clientes(nome=form.nome.data, morada=form.morada.data, utilizadorId=user.id)
        db.session.add(new_client)
        db.session.commit()

        return redirect(url_for('login'))
        
    return render_template('registar.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', email=current_user.email)


@app.route('/logout')
@login_required
def logout():
    logout_user
    return redirect(url_for('login'))



if __name__ == "__main__":    app.run (debug=True)
