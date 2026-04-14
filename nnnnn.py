from flask import Flask ,session , render_template , request ,redirect , url_for
import flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for sessions (change this to a random string in production)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/inventory'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/stock'


db = SQLAlchemy(app)

class ITEM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(25), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(25), nullable=False)
    def __repr__(self):
        return f"<item {self.name}>"



@app.route('/')
def home():
    return flask.render_template('index.html')

# @app.route('/bill')
# def bill():
#     posts = ITEM.query.all()
#     return flask.render_template('bill.html',posts=posts)


@app.route('/bill', methods=['GET', 'POST'])
def bill():
    if request.method == 'POST':
        # Handle adding item to cart
        item_type = request.form['type']
        search_value = request.form['name']
        buy_qty = int(request.form['item_quantity'])

        # Find the item
        if item_type == 'id':
            item = ITEM.query.get(search_value)
        else:
            item = ITEM.query.filter_by(name=search_value).first()

        if not item:
            return render_template('bill.html', error="Item not found.", items=ITEM.query.all(), cart=session.get('cart', []))

        if buy_qty > item.quantity:
            return render_template('bill.html', error=f"Not enough stock. Available: {item.quantity}", items=ITEM.query.all(), cart=session.get('cart', []))

        # Get or initialize cart (list of dicts: {'id': int, 'name': str, 'price': float, 'qty': int})
        cart = session.get('cart', [])

        # Check if item already in cart
        found = False
        for c_item in cart:
            if c_item['id'] == item.id:
                if c_item['qty'] + buy_qty > item.quantity:
                    return render_template('bill.html', error=f"Not enough stock after adding. Available: {item.quantity}", items=ITEM.query.all(), cart=cart)
                c_item['qty'] += buy_qty
                found = True
                break

        if not found:
            cart.append({'id': item.id, 'name': item.name, 'price': item.price, 'qty': buy_qty})

        total = 0
        for c_item in cart:
            total = total+(c_item['price']*c_item['qty'])


        session['cart'] = cart
        return render_template('bill.html', success="Item added to bill successfully!", items=ITEM.query.all(), cart=cart ,total=total)

    # GET request: Load all items and current cart
    return render_template('bill.html', items=ITEM.query.all(), cart=session.get('cart', []))

@app.route('/bill/delete/<int:index>', methods=['POST'])
def delete_item(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        del cart[index]
        session['cart'] = cart
    return redirect(url_for('bill'))

@app.route('/bill/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('bill'))


@app.route('/item', methods=['GET',"POST"])
def item():
    if flask.request.method == 'POST':
        item_name = flask.request.form['item_name']
        item_category = flask.request.form['item_category']
        item_price = flask.request.form['item_price']
        item_quantity = flask.request.form['item_quantity']
        item_status = flask.request.form['item_status']
        new_item = ITEM(name=item_name, category=item_category, price=item_price, quantity=item_quantity, status=item_status)
        db.session.add(new_item)
        db.session.commit()
        return flask.render_template('item.html', submitted=True)

    return flask.render_template('item.html')


@app.route('/search',methods=['GET',"POST"])
def search():
    if flask.request.method == 'POST':
        col = flask.request.form['type']
        value = flask.request.form['name']
        if col =='id':
            res = ITEM.query.filter_by(id=value).first()
        elif col =='name':
            res = ITEM.query.filter_by(name=value).first()
        else:
            res=None
        return flask.render_template('search.html', result=res, submitted=True)
    return flask.render_template('search.html')

@app.route('/edit', methods=['GET','POST'])
def edit():
    if flask.request.method == 'POST':
        col = flask.request.form['type']
        value = flask.request.form['name']
        if col =='id':
            res = ITEM.query.filter(ITEM.id==value).first()
        else:
            res = ITEM.query.filter(ITEM.name==value).first()
        return flask.render_template('edit.html', result=res , submitted =True , s=False)
    return flask.render_template('edit.html',s=True)

@app.route('/edit/<string:id>', methods=['GET','POST'])
def edit_item(id):
    if flask.request.method == 'POST':
        i_name = flask.request.form['item_name']
        i_category = flask.request.form['item_category']
        i_price = flask.request.form['item_price']
        i_quantity = flask.request.form['item_quantity']
        i_status = flask.request.form['item_status']
        
        edit_item = ITEM.query.filter_by(id=id).first()
        edit_item.name = i_name
        edit_item.category = i_category
        edit_item.price = i_price
        edit_item.quantity = i_quantity
        edit_item.status = i_status
        db.session.commit()
        
        return flask.render_template('edit.html', result=edit_item , submitted =False , s=True ,done=True)


@app.route('/stock')
def stock():
    posts = ITEM.query.all()
    return flask.render_template('stock.html',posts=posts)

@app.route('/stock/filter' , methods=['GET','POST'])
def stockfilter():
    if flask.request.method == 'POST':
        c = flask.request.form['item_category']
        p = flask.request.form['item_price']
        q = flask.request.form['item_quantity']
        submitted=True
        if c == "" and p == "" and q == "":
            res = None
            submitted = False
        elif c != "" and p != "" and q != "":
            if p=="highp" and q=="highq":
                res = ITEM.query.filter(ITEM.category==c).order_by(ITEM.price.desc(),ITEM.quantity.desc()).all()
            elif q=="highq":
                res = ITEM.query.filter(ITEM.category==c).order_by(ITEM.price.asc(),ITEM.quantity.desc()).all()
            elif p=="highp":
                res = ITEM.query.filter(ITEM.category==c).order_by(ITEM.price.desc(),ITEM.quantity.asc()).all()  
            else: 
                res = ITEM.query.filter(ITEM.category==c).order_by(ITEM.price.asc(),ITEM.quantity.asc()).all()
        elif c != "" and p != "":
            if p=="highp":
                res = ITEM.query.filter(ITEM.category==c).order_by(ITEM.price.desc()).all() # diffrent way-------------------
            else:
                res = ITEM.query.filter(ITEM.category==c).order_by(ITEM.price.asc()).all()
        elif c!="" and q!="":
             if q=="highq":
                res = ITEM.query.filter(ITEM.category==c).order_by(ITEM.quantity.desc()).all()
             else:
                res = ITEM.query.filter(ITEM.category==c).order_by(ITEM.quantity.asc()).all()
        elif c !='':
            res = ITEM.query.filter_by(category=c).all()  # diffrent way-------------------------------------------------
        elif p !='':
            if p=="highp":
                res = ITEM.query.order_by(ITEM.price.desc()).all()
            else:
                res = ITEM.query.order_by(ITEM.price.asc()).all()
        else:
            if q=="highq":
                res = ITEM.query.order_by(ITEM.quantity.desc()).all()
            else:
                res = ITEM.query.order_by(ITEM.quantity.asc()).all()
        return flask.render_template('stock.html', posts=res, submitted=submitted)

if __name__ == "__main__":
 app.run(debug=True)