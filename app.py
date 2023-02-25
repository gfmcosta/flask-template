# from crypt import methods
# from jinja2 import TemplateNotFound
import email
from email.mime import image
from enum import unique
from datetime import date
from mailbox import NotEmptyError
import re
from tkinter import image_names
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from sqlalchemy import desc 
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from flask_table import Table, Col



app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost:3306/shopdb'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost:3306/shopdb'
app.config['SECRET_KEY'] = 'IstoEUmaSecretKey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
IdCliente=0
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
print("teste")

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
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
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
    if form.validate_on_submit():
        categorias=Categorias.query.all()
        products=Produtos.query.all()
        user = Utilizadores.query.filter_by(email=form.email.data).first()
        client = Clientes.query.filter_by(utilizadorId=user.id).first()
        if user:
            if user.password == form.password.data:
                login_user(user, remember=form.password.data)
                if(user.roleId==1):
                    return redirect('/backend')
                else:
                    #return redirect('/frontend')
                    global IdCliente
                    IdCliente=client.id
                    return render_template('frontend.html', categorias=categorias,products=products)

        
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

        return render_template('login.html',form=form)
        # return redirect(url_for('login'))
        
    return render_template('registar.html', form=form)


@app.route('/backend')
@login_required
def backend():
    return render_template('backend.html', email=current_user.email)


@app.route('/logout')
def logout():
    logout_user
    return render_template('login.html')
    # return redirect(url_for('login'))
    

@app.route('/frontend')
@login_required
def frontend():
    try:
        categorias=Categorias.query.all()
        print(IdCliente)
        products = Produtos.query.all()
        return render_template('frontend.html', categorias=categorias,products=products)
    except Exception as e:
        print(e)
        return '<h1>Algo deu errado.</h1>'


@app.route('/comp_front')
@login_required
def comp_front():
    try:
        products = Produtos.query.all()
        return render_template('comp_front.html', products=products)
    except Exception as e:
        return '<h1>Algo deu errado.</h1>'


@app.route('/tel_front/<int:idCategoria>', methods=['GET', 'POST'])
@login_required
def tel_front(idCategoria):
    try:
        categorias=Categorias.query.all()
        id=idCategoria
        products = Produtos.query.all()
        return render_template('tel_front.html', categorias=categorias,products=products,id=id)
    except Exception as e:
        print(e)
        return '<h1>Algo deu errado.</h1>'

@app.route('/cliente_admin')
@login_required
def cliente_admin():
    try:
        clientes = Clientes.query.all()
        users = Utilizadores.query.all()
        return render_template('cliente_admin.html', clientes=clientes, users=users)
    except Exception as e:
        return '<h1>Algo deu errado.</h1>'
        

@app.route('/categoria_admin')
@login_required
def categoria_admin():
    try:
        categorias = Categorias.query.all()
        return render_template('categoria_admin.html', categorias=categorias)
    except Exception as e:
        return '<h1>Algo deu errado.</h1>'


@app.route('/novo_produto')
@login_required
def novo_produto():
    try:
        categorias = Categorias.query.all()
        return render_template('novo_produto.html', categorias=categorias)
    except Exception as e:
        return '<h1>Algo deu errado.</h1>'

@app.route('/novo_produto', methods=['POST'])
@login_required
def novo_produto_post():
    descricao = request.form['descricao']
    preco = request.form['preco']
    categoria_nome = request.form.get('categoria')
    imagem = request.files['file']
    categoriaId = 0
    if imagem.filename != '':
        imagem.save("static/images/"+imagem.filename)
    else:
        imagem.filename="semFoto.png"
    ## add new product to db
    categorias = Categorias.query.all()
    for categoria in categorias:
        if (categoria.descricao==str(categoria_nome)):
            categoriaId = categoria.id
        
    new_product = Produtos(descricao=descricao,preco=preco,image_url=imagem.filename,categoriaId=categoriaId)
    db.session.add(new_product)
    db.session.commit()
    products = Produtos.query.all()
    
    
    return render_template('produto_admin.html', products=products, categorias=categorias)

@app.route('/nova_categoria')
@login_required
def nova_categoria():
    return render_template('nova_categoria.html')

@app.route('/nova_categoria', methods=['POST'])
@login_required
def nova_categoria_post():
    descricao = request.form['descricao']
    new_categoria = Categorias(descricao=descricao)
    db.session.add(new_categoria)
    db.session.commit()
    categorias = Categorias.query.all()
    return render_template('categoria_admin.html',categorias=categorias)

@app.route('/produto_admin')
@login_required
def produto_admin():
    try:
        products = Produtos.query.all()
        categorias = Categorias.query.all()
        return render_template('produto_admin.html', products=products, categorias=categorias)
    except Exception as e:
        return '<h1>Algo deu errado.</h1>'

@app.route('/edit_produto/<int:idProduto>', methods=['GET', 'POST'])
@login_required
def edit_produto(idProduto):
    try:
        produto=Produtos.query.filter_by(id=idProduto).first()
        categorias = Categorias.query.all()
        if produto:
            if request.method == 'POST':
                categoriaId = 0
                descricao = request.form['descricao']
                preco = request.form['preco']
                categoria_nome = request.form.get('categoria')
                imagem = request.files['file']

                for categoria in categorias:
                    if (categoria.descricao==str(categoria_nome)):
                        categoriaId = categoria.id
                produto.descricao = descricao
                produto.preco=preco
                produto.categoriaId=categoriaId
                if imagem.filename != '':
                    produto.image_url=imagem.filename
                    imagem.save("static/images/"+imagem.filename)
                db.session.commit()
                products = Produtos.query.all()
                ##return render_template('produto_admin.html',products=products, categorias=categorias)
                return redirect(url_for('produto_admin', products=products, categorias=categorias))
            return render_template('edit_produto.html', produto=produto, categorias=categorias)
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
        return '<h1>Algo deu errado.</h1>'

@app.route('/edit_categoria/<int:idCategoria>', methods=['GET', 'POST'])
@login_required
def edit_categoria(idCategoria):
    try:
        categoria=Categorias.query.filter_by(id=idCategoria).first()
        if categoria:
            if request.method == 'POST':
                descricao = request.form['descricao']
                categoria.descricao= descricao

                db.session.commit()
                categorias = Categorias.query.all()
                ##return render_template('produto_admin.html',products=products, categorias=categorias)
                return redirect(url_for('categoria_admin', categorias=categorias))
            return render_template('edit_categoria.html', categoria=categoria)
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
        return '<h1>Algo deu errado.</h1>'

@app.route('/encomenda/<int:idProduto>', methods=['GET', 'POST'])
@login_required
def encomenda(idProduto):
    try:
        products = Produtos.query.all()
        produto=Produtos.query.filter_by(id=idProduto).first()
        categorias = Categorias.query.all()
        if produto:
            if request.method == 'POST':
                quantidade= request.form['quantidade']
                total= float(quantidade)*float(produto.preco)
                today=date.today()
                new_encomenda = Encomendas(dataEncomenda=today,total=total,clienteId=IdCliente)
                db.session.add(new_encomenda)
                db.session.commit()
                encomenda = Encomendas.query.filter_by(clienteId=IdCliente).order_by(Encomendas.id.desc()).first()
                new_linhaEncomenda = Linhas_encomenda(quantidade=quantidade,encomendaId=encomenda.id,produtoId=produto.id)
                db.session.add(new_linhaEncomenda)
                db.session.commit()
                return redirect(url_for('fatura', idFatura=encomenda.id))
            return render_template('carrinho.html',categorias=categorias,products=products,produto=produto)
        else:
            return 'Error loading'
    except Exception as e:
        print(e)
        return '<h1>Algo deu errado.</h1>'

@app.route('/fatura/<int:idFatura>', methods=['GET'])
@login_required
def fatura(idFatura):
    try:
        print(idFatura)
        categorias = Categorias.query.all()
        encomenda= Encomendas.query.filter_by(id=idFatura).first()
        linhaEncomenda= Linhas_encomenda.query.filter_by(encomendaId=idFatura).first()
        produto= Produtos.query.filter_by(id=linhaEncomenda.produtoId).first()
        cliente = Clientes.query.filter_by(id=IdCliente).first()
        nomeF='doc/encomenda.txt'+str(encomenda.id)
        with open(nomeF, 'x') as f:
            f.write('Data da encomenda: ')
            f.write(str(encomenda.dataEncomenda))
            f.write('\nNr. Encomenda: ')
            f.write(str(encomenda.id))
            f.write('\nNome: ')
            f.write(str(cliente.nome))
            f.write('\Morada: ')
            f.write(str(cliente.morada))
            f.write('\n====================')
            f.write("\n1 "+str(produto.descricao)+" "+str(linhaEncomenda.quantidade)+" "+str(produto.preco))
            f.write('\n\n\nTotal fatura: ')
            f.write(str(encomenda.total) +"€")
        return render_template('fatura.html', categorias=categorias, produto=produto,linhaEncomenda=linhaEncomenda,encomenda=encomenda,cliente=cliente)
    except Exception as e:
        return '<h1>Algo deu errado.</h1>'
    
if __name__ == "__main__":
    app.run (debug=True)
