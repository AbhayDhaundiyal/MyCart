import sqlalchemy as db
import pandas as pd

engine = db.create_engine('sqlite:///db.db')

connection = engine.connect()


def login(): # for user and admin flow switch
    print("1. User")
    print("2. Admin")
    choice = input("Select the choice: ")
    if choice == '1':
        user()
    elif choice == '2':
        admin()
    else:
        print("Invalid Choice")
        login()

def add(choice):
    if choice == "1":
        name = input("Input category name ")
        df = pd.read_sql("Select * from cate", con=engine)
        chk = pd.read_sql("Select * from cate where name like '" + name + "'", con=engine)
        if chk.size > 0:
            print("Category already exists")
        else:
            engine.execute("Insert into cate values (" + str((df.size+1)) + ",'" + name + "')")
            print("Category Added!")
    else:
        name = input("Input product name ")
        price = input("Add the product price ")
        cate = input("Add category of the product ")
        chk = pd.read_sql("Select id from cate where name like '" + str(cate) + "'", con=engine)
        if chk.size == 0:
            print("Category Not found")
        else:
            df = pd.read_sql("Select * from prod", con=engine)
            engine.execute("Insert into prod values (" + str((df.size+1)) + ",'" + name + "'," + str(price) + "," + str(chk.values[0][0]) + ")")
            print("Product Added!")
    login()

def see_bill():
    df = pd.read_sql("Select distinct id from bills", con=engine)
    print("Bill_ID  Prod_Name  QTY")
    for ids in df.values:
        ind_bill = pd.read_sql("Select * from bills where id = " + str(ids[0]), con=engine)
        for data in ind_bill.values:
            for d in data:
                print(d, end="  ")
            print("\n", end="")
    print("Total Price : " + str(ind_bill.values[0][3]), end="\n\n")


def admin():
    print("1. Add Category")
    print("2. Add Product")
    print("3. Show Cart")
    print("4. See all bilings")
    choice = input("Select any option ")
    if choice == "1" or choice == "2":
        add(choice)
    elif choice == "3":
        cart("2")
    elif choice == '4':
        see_bill()
    else:
        print("invalid Choice")
        admin()
    

def bill(): # final user billing
    df = pd.read_sql("Select * from cart", con = engine)
    price = 0
    if df.size == 0:
        print("Nothing to bill yet")
        user()
    else:
        x = []
        y = []
        z = []
        for data in df.price:
            y.append(int(data))
        for data in df.qty:
            x.append(int(data))
        for data in df.name:
            z.append(data)
        print("Name  Price  QTY")
        for i in range(len(x)):
            print(z[i] + "  " + str(y[i]) + "  " + str(x[i]), end = "\n")
            price = price + (x[i] * y[i])
        tmp = price
        if price > 10000:
            price = price - 500
        bill_id = (pd.read_sql("Select * from bills", con = engine)).size
        for i in range(len(x)):
            engine.execute("Insert into bills values (" + str(bill_id) + ", '" + z[i] + "', " + str(x[i]) + ", " + 
            str(price) + ")")
            print("Bill Saved!")
    print("Actual price :", end = " ")
    if tmp > 10000:
        print(price + 500)
    else:
        print(price)
    print("Final price :", end = " ")
    print(price)
    print("Thank You")
    engine.execute("delete from cart")
    engine.execute("vacuum")
    print("\n")
    user()


def cart(val):  # list cart and can proceed to checkout
    df = pd.read_sql("Select * from cart", con = engine)
    if df.size == 0:
        print("Nothing here yet")
        user()
    else:
        for data in df.values:
            for d in data:
                print(d, end = " ")
            print("\n")
        if val != "2":
            choice = input("Checkout? Y/N ")
            if choice == "Y":
                bill()
            elif choice != "N":
                print("Invalid Choice\n")
            else:
                print("1. Increase Quantity of any product")
                print("2. Decrease Quantity of any product")
                choice = input("Insert choice ")
                prod = input("Input id of product ")
                if choice == "1":
                    engine.execute("Update from cart set qty = qty - 1 where prod_id = " + prod)
                    df = pd.read_sql("Select prod_id from cart where qty = 0")
                    if df.size != 0:
                        for data in df.values:
                            for d in data:
                                engine.execute("delete from cart where prod_id = " + d)
                elif choice == "2":
                    engine.execute("Update from cart set qty = qty + 1 where prod_id = " + prod)
                else:
                    print("Invalid choice")
        login()
        
def buy(val): # cart products listing
    if val != "prod":
        products = pd.read_sql("Select * from prod where cate = " + val, con = engine)
    else:
        products = pd.read_sql("Select * from prod", con = engine)

    for product in products.values:
        for details in product:
            print(details, end = " ")
        print("\n")
    if products.size == 0:
        print("No Items Available")
        user()
    prod_id = input("Select the product you want to buy")
    sql = "Select * from cart where prod_id = "
    sql = sql + prod_id
    price = pd.read_sql("select price from prod where id = " + prod_id, con = engine)
    name = pd.read_sql("select name from prod where id = " + prod_id, con = engine)
    df = pd.read_sql(sql, con = engine)
    if df.size == 0:
        sql = "Insert into cart values (" + name.values[0][0] + ",1," + prod_id + "," + str(price.values[0][0]) + ")"
        # print(sql)
        engine.execute("Insert into cart values ( '" + name.values[0][0] + "', 1, " + prod_id + "," + str(price.values[0][0]) + " )")
    else:
        sql = "Update cart set qty = qty + 1 where prod_id = " + prod_id
        engine.execute(sql)
    print("Product added sucessfully")
    check = input("Go to cart ?(Y/N) ")

    if check == "Y":
        cart("1")
    user()

def show(table): # list items from products, categories
    if table != "prod":
        sql = "Select * from "
        sql = sql + table
        df = pd.read_sql(sql, con = engine)
        for data in df.values:
            for d in data:
                print(d, end = " ")
            print("\n")
        choice = input("Select the category ")
        buy(choice)
    else:
        buy("prod")



def user(): # functions of user
    print("1. Show the Categories")
    print("2. Show the Products")
    print("3. Show Cart")
    print("4. Billing")
    choice = input("Select what you want ")
    if choice == '1':
        show("cate")
    elif choice == "2":
        show("prod")
    elif choice == '3':
        cart("1")
    elif choice == '4':
        bill()
    else:
        print("Invalid Choice")
        user()

print("Welcome To MyCart")
login()


    
