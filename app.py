from flask import Flask, render_template, url_for, redirect, request, session
import mysql.connector
import os

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='inventory'
)

mycursor = conn.cursor()


app = Flask(__name__)

app.secret_key = "shaka&julie"


@app.route('/', methods=['POST', 'GET'])
def login():
    msg = ''
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        query = f"SELECT * FROM {role} WHERE email=%s AND password=%s"
        mycursor.execute(query, (email, password))

        account = mycursor.fetchone()

        if account:
            session['loggedin'] = True
            session['user'] = account[1]
            session['id'] = account[0]
            if(role=='user'):
                return redirect(url_for('dashboard'))
            elif(role=='supplier'):
                return redirect(url_for('supplier'))
            elif(role=='employee'):
                permission=account[5]
                if permission=='1':
                    return redirect(url_for('employee'))
                else:
                    msg = "Your are not allowed to login See Your Admin!!!"
        else:
            msg = "Wrong email or password"
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/reset-password')
def passwordReset():
    return render_template('reset-password.html')


@app.route('/dashboard')
def dashboard():
    counts = {
        'num_pdt': get_table_count('product'),
        'num_w': get_table_count('ware_house'),
        'num_c': get_table_count('category'),
        'num_e':get_table_count('employee'),
        'num_s':get_table_count('supplier'),
        'num_sale':get_table_count('sale')
    }

    return render_template('dashboard.html', **counts)




@app.route('/category')
def category():
    mycursor.execute("SELECT * FROM category")
    categories = mycursor.fetchall()
    return render_template('category.html', categories=categories)


@app.route('/add-category', methods=['POST', 'GET'])
def addCategory():
    if request.method == "POST":
        catName = request.form['cat_name']
        status = request.form['status']

        mycursor.execute(
            "INSERT INTO category(cat_name, status) VALUES(%s, %s)", (catName, status))
        conn.commit()
    return redirect(url_for('category'))


@app.route('/edit-category', methods=['POST', 'GET'])
def editCategory():
    if request.method == "POST":
        id = request.form['cat_id']
        name = request.form['cat_name']
        status = request.form['status']

        mycursor.execute(
            "UPDATE category SET cat_name = %s, status=%s WHERE cat_id=%s", (name, status, id,))
        conn.commit()
    return redirect(url_for('category'))


@app.route('/delete-category', methods=['POST'])
def deleteCategory():
    if request.method == "POST":
        id = request.form['cat_id']
        mycursor.execute("DELETE FROM category WHERE cat_id=%s", (id,))
        conn.commit()
        return redirect(url_for('category'))


@app.route('/warehouse')
def wareHouse():
    mycursor.execute("SELECT * FROM ware_house")
    wareHouse = mycursor.fetchall()
    return render_template('warehouse.html', wareHouse=wareHouse)


@app.route('/add-warehouse', methods=['POST', 'GET'])
def addWarehouse():
    if request.method == "POST":
        name = request.form['wname']
        status = request.form['status']

        mycursor.execute(
            "INSERT INTO ware_house(w_name, status) VALUES(%s, %s)", (name, status))
        conn.commit()
    return redirect(url_for('wareHouse'))


@app.route('/edit-warehouse', methods=['POST', 'GET'])
def editWarehouse():
    if request.method == "POST":
        id = request.form['wh_id']
        name = request.form['whname']
        status = request.form['status']

        mycursor.execute(
            "UPDATE ware_house SET w_name = %s, status=%s WHERE id=%s", (name, status, id,))
        conn.commit()
    return redirect(url_for('wareHouse'))


@app.route('/delete-warehouse', methods=['POST'])
def deleteWarehouse():
    if request.method == "POST":
        id = request.form['wh_id']
        mycursor.execute("DELETE FROM ware_house WHERE id=%s", (id,))
        conn.commit()
        return redirect(url_for('wareHouse'))


@app.route('/products')
def products():
    mycursor.execute("SELECT * FROM product")
    products = mycursor.fetchall()
    return render_template('products.html', products=products)


@app.route('/addProduct', methods=['POST', 'GET'])
def addProduct():

    if request.method == 'POST':
        pdt_name = request.form['pdt_name']
        pdt_image = request.files['pdt_image']
        pdt_category = request.form['category']
        pdt_warehouse = request.form['warehouse']
        pdt_desc = request.form['pdt_dsc']
        pdt_price = request.form['pdt_price']
        pdt_qty = request.form['pdt_quantity']
        availability = request.form['availability']

        imagePath = "static/images/"

        data = [
            pdt_name,
            pdt_desc,
            pdt_image.filename,
            pdt_category,
            pdt_warehouse,
            pdt_price,
            pdt_qty,
            availability
        ]

        if pdt_image:
            pdt_image.save(os.path.join(imagePath, pdt_image.filename))

            mycursor.execute(
                "INSERT INTO product(pdt_name, pdt_description, pdt_image, pdt_category, pdt_whouse, pdt_price, pdt_quantity, availability) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (data))
            conn.commit()

        return redirect(url_for('products'))

    mycursor.execute("SELECT * FROM ware_house")
    wareHouse = mycursor.fetchall()

    mycursor.execute("SELECT * FROM category")
    categories = mycursor.fetchall()

    return render_template('pages/add-product.html', wareHouse=wareHouse, categories=categories)


@app.route('/editProduct/<int:id>', methods=['POST', 'GET'])
def editProduct(id):

    if request.method == 'POST':
        pdt_name = request.form['pdt_name']
        pdt_image = request.files['pdt_image']
        pdt_category = request.form['category']
        pdt_warehouse = request.form['warehouse']
        pdt_desc = request.form['pdt_dsc']
        pdt_price = request.form['pdt_price']
        pdt_qty = request.form['pdt_quantity']
        availability = request.form['availability']

        imagePath = "static/images/"

        if pdt_image:
            pdt_image.save(os.path.join(imagePath, pdt_image.filename))
            pdt_image = pdt_image.filename
        else:
            pdt_image = request.form['pdt_image']

        data = [
            pdt_name,
            pdt_desc,
            pdt_image,
            pdt_category,
            pdt_warehouse,
            pdt_price,
            pdt_qty,
            availability,
            id
        ]

        data_tuple = tuple(data)

        mycursor.execute(
            "UPDATE product SET pdt_name=%s, pdt_description=%s, pdt_image=%s, pdt_category=%s, pdt_whouse=%s, pdt_price=%s, pdt_quantity=%s, availability=%s WHERE id=%s", data_tuple)
        conn.commit()

        return redirect(url_for('editProduct', id=id))

    mycursor.execute("SELECT * FROM product WHERE id=%s", (id,))
    product = mycursor.fetchone()

    mycursor.execute("SELECT * FROM ware_house")
    wareHouse = mycursor.fetchall()

    mycursor.execute("SELECT * FROM category")
    categories = mycursor.fetchall()
    return render_template('pages/edit-product.html', p=product, wareHouse=wareHouse, categories=categories)


@app.route('/deleteProduct<int:id>', methods=['POST', 'GET'])
def deleteProduct(id):
    mycursor.execute("DELETE FROM product WHERE id=%s", (id,))
    conn.commit()
    return redirect('products')


@app.route('/suppliers', methods = ['POST', 'GET'])
def suppliers():
    if request.method=="POST":
        sup_name = request.form['sup_name']
        sup_email = request.form['sup_email']
        sup_phone = request.form['sup_phone']
        password = request.form['password']
        
        data = [
            sup_name,
            sup_email,
            sup_phone,
            password
        ]
        
        mycursor.execute("INSERT INTO supplier(name, email, phone, password) VALUES(%s, %s, %s,%s)", (data))
        conn.commit()
        
    mycursor.execute("SELECT * FROM supplier")
    suppliers = mycursor.fetchall()
        
        
    return render_template('suppliers.html', suppliers=suppliers)


@app.route('/employees', methods=['POST', 'GET'])
def employees():
    if request.method=="POST":
        employee_name = request.form['employee_name']
        employee_email = request.form['employee_email']
        employee_phone = request.form['employee_phone']
        password = request.form['password']
        permission = 0
        
        data = [
            employee_name,
            employee_email,
            employee_phone,
            password,
            permission
        ]
        mycursor.execute("INSERT INTO employee(name, email, phone, password, permission) VALUES(%s, %s, %s,%s, %s)", (data))
        conn.commit()
        
    mycursor.execute("SELECT * FROM employee")
    employees = mycursor.fetchall()
        
    return render_template('employees.html', employees = employees)

@app.route('/permit-employee/<int:id>')
def permitEmployee(id):
    mycursor.execute("SELECT * FROM employee WHERE id=%s", (id,))
    emp = mycursor.fetchone()
    prm = emp[5]
    
    if prm =='1':
        mycursor.execute("UPDATE employee SET permission=%s WHERE id=%s", ('0', id,))
        conn.commit()
    else:
        mycursor.execute("UPDATE employee SET permission=%s WHERE id=%s", ('1', id,))
        conn.commit()
    return redirect(url_for('employees'))

@app.route('/sales')
def sales():
    sales = get_data('sale')
    return render_template('sales.html', sales=sales)

@app.route('/settings', methods=['POST', 'GET'])
def settings():
    msg = ''
    if 'id' in session:
        userId = session['id']
        user = get_data_by_id('user', userId)
        str_pass = user[5]
               
        if request.method=="POST":
            email=request.form['email']
            old_pass = request.form['o_pass']
            n_pass = request.form['n_pass']
            cf_pass = request.form['cf_pass']
            
            if str_pass==old_pass:
                if n_pass==cf_pass:
                    mycursor.execute("UPDATE user SET email=%s, password=%s WHERE id=%s",(email, n_pass, userId))
                    conn.commit()
                else: 
                    msg = "Passwords doen't match"
            else:
                msg = "Please input correct Password"
                
           
            
            
    return render_template('settings.html', user=user, msg=msg)








# ---------------------------------supplier-------------------------------------------------------------
@app.route('/supplier')
def supplier():
    return render_template('supplier/layout.html')



# ---------------------------------employee-------------------------------------------------------------
@app.route('/employee')
def employee():
    if 'id' in session:
        employeeId = session['user']
    counts = {
        'num_pdt': get_table_count('product'),
        'num_s':get_table_count_by_user('sale', employeeId)
        
    }    
    return render_template('employee/dashboard.html', **counts)

@app.route('/e-products')
def eproduct():
    mycursor.execute("SELECT * FROM product")
    products = mycursor.fetchall()
    return render_template('employee/products.html', products=products)

@app.route('/sellProduct/<int:id>', methods=['POST', 'GET'])
def sellProduct(id):
    if 'id' in session:
        employeeId = session['user']
        if request.method=="POST":
            quantity = request.form['quantity']
            total_price = request.form['total-price']
            _qty = request.form['qty']
            pdt = request.form['pdt']
                       
            newQty = float(_qty)-int(quantity)
            
            mycursor.execute("INSERT INTO sale(employeeId, productId, quantity, price) VALUES(%s, %s, %s, %s)", (employeeId, pdt, quantity, total_price))
            conn.commit()
            
            mycursor.execute("UPDATE product SET pdt_quantity=%s WHERE id=%s", (newQty, id,))
            conn.commit()
    
    mycursor.execute("SELECT * FROM product WHERE id=%s", (id,))
    product = mycursor.fetchone()
    return render_template('employee/sell-product.html', p=product)


@app.route('/mysales')
def mySales():
    if 'id' in session:
        employee = session['user']
        
        sales = get_data('sale')
        print(employee)
    return render_template('employee/mysales.html', sales=sales, e=employee)


@app.route('/employee-settings', methods=['POST', 'GET'])
def esettings():
    
    msg = ''
    if 'id' in session:
        userId = session['id']
        user = get_data_by_id('employee', userId)
        str_pass = user[5]
               
        if request.method=="POST":
            email=request.form['email']
            old_pass = request.form['o_pass']
            n_pass = request.form['n_pass']
            cf_pass = request.form['cf_pass']
            
            if str_pass==old_pass:
                if n_pass==cf_pass:
                    mycursor.execute("UPDATE employee SET email=%s, password=%s WHERE id=%s",(email, n_pass, userId))
                    conn.commit()
                else: 
                    msg = "Passwords dosen't match"
            else:
                msg = "Please input correct Password"
    return render_template('employee/settings.html', user=user, msg=msg)





def get_data(tabel_name):
    mycursor.execute(f"SELECT * FROM {tabel_name}")
    return (mycursor.fetchall())

def get_data_by_id(table_name, id):
    mycursor.execute(f"SELECT * FROM {table_name} WHERE id={id}")
    return(mycursor.fetchone())

def get_table_count(table_name):
    mycursor.execute(f"SELECT * FROM {table_name}")
    return len(mycursor.fetchall())

def get_table_count_by_user(table_name, username):
    query = "SELECT COUNT(*) FROM {} WHERE employeeId = %s".format(table_name)
    mycursor.execute(query, (username,))
    return mycursor.fetchone()[0]



if __name__ == '__main__':
    app.run(debug=True)
