from product_management import User, Product, Orders
from test import client
from product_management import app 
import pytest

"""
def initial_setup():
    request_data={"username":"username", "password":"password", "address":"address" ,"userType":"PRODUCER"}
    response = client.post("/user", json=request_data)
    response_data = response.json["data"]
    user_id = response_data.get("id")
    
def create_product():
    request_data={"name":"book", "description":"a good book", "quantity":1}
    response = client.post("/product", json=request_data)
    """

def initial_user_create(username = None, password=  None, address = None, user_type = "PRODUCER"):
    if not username:
        username = "username"
    if not password:
        password = "password"
    if not address:
        address = "address"
    if not user_type:
        user_type = "PRODUCER"
    user_id = None
   
    with app.app_context():
        user_id  = User.get_by_username(username="username")
        app.secret_key = 'super secret key'
        app.config['SESSION_TYPE'] = 'filesystem'   
    if user_id:
        username = user_id.username
        password = user_id.password
    else :
        request_data={"username":username, "password":password, "address":address ,"userType":user_type}
        response = client.post("/user", json=request_data)
        response_data = response.json["data"]
        user_id = response_data.get("id")
        username = response_data.get("username")
        password = response_data.get("password")   
   
    return username,password

def test_product_add(client):
    username,password = initial_user_create()
    response = client.post("/login", json={"username":username, "password":password})
    
    request_data={"name":"book5", "description":"a good book", "quantity":1}
    response = client.post("/product", json=request_data)
    
    response_data = response.json["data"]
    assert response_data.get("name") == "book4"
    assert response_data.get("description") == "a good book"
    assert response_data.get("quantity") == 1

class ProductTest:

    def test_prod_read(client):

        import pdb
        pdb.set_trace()
        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})

        product_name = "book1"
        product_desc = None
        product_quantity = None
        with app.app_context():
            product_id  = Product.get_by_name(name=product_name )
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'
        if product_id:
            product_desc = product_id.description
            product_quantity = product_id.quantity
            product_id=product_id.id        
        else:
            request_data={"name":"book1", "description":"a good book", "quantity":1}
            response = client.post("/product", json=request_data)
            response_data = response.json["data"]
            product_id = response_data.get("id")
            product_desc = response_data.get("description")
            product_quantity = response_data.get("quantity")
        url =f"/product?id={product_id}"
        response = client.get(url)
    
        response_data = response.json["data"]
        assert response_data.get("name") == product_name
        assert response_data.get("description") == product_desc
        assert response_data.get("quantity") == product_quantity
        


    def test_prod_edit(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})

        product_name = "book1"
        product_desc = None
        product_quantity = None
        with app.app_context():
            product_id  = Product.get_by_name(name=product_name )
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'
        if product_id:
        
            product_id=product_id.id        
        else:
            request_data={"name":"book1", "description":"a good book", "quantity":1}
            response = client.post("/product", json=request_data)
            response_data = response.json["data"]
            product_id = response_data.get("id")
        
        new_product_desc = "new desc"
        new_product_quantity = 2
        request_json = {"id":product_id, "description":new_product_desc, "quantity":new_product_quantity}
        
        response = client.put("/product", json = request_json)

        response_data = response.json["data"]
        assert response_data.get("description") == new_product_desc
        assert response_data.get("quantity") == new_product_quantity
    
    def test_prod_delete(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})
    
        product_name = "book1"
        with app.app_context():
            product_id  = Product.get_by_name(name=product_name )
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'
            
        if product_id:
            product_id = product_id.id
        else:
            request_data={"name":"book1", "description":"a good book", "quantity":1}
            response = client.post("/product", json=request_data)
            response_data = response.json["data"]
            product_id = response_data.get("id")

        url =f"/product?id={product_id}"
        response = client.delete(url)
    
        response_data = response.json["data"]
        assert response_data.get("status") == True
        
    def test_prod_list(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})

        product_name = "book1"
        with app.app_context():
            product_id  = Product.get_by_name(name=product_name )
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'
        if product_id:
            
            product_id=product_id.id        
        else:
            request_data={"name":"book1", "description":"a good book", "quantity":1}
            response = client.post("/product", json=request_data)
            response_data = response.json["data"]
            product_id = response_data.get("id")
        
        
        response = client.list("/product/list", json ={})

        response_data = response.json["data"]

        for a_product in response_data.get("products"):
            assert a_product.get("id") == product_id



class UserTest:
    def test_user_add(client):

        user_id = None
        username = None
        password = None
        with app.app_context():
            user_id  = User.get_by_username(username="username")
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'   
        if user_id:
            username = user_id.username
            password = user_id.password
        else :
            request_data={"username":"username", "password":"password", "address":"address" ,"userType":"PRODUCER"}
            response = client.post("/user", json=request_data)
            response_data = response.json["data"]
            user_id = response_data.get("id")
            username = response_data.get("username")
            password = response_data.get("password")   
        
        assert response_data.get("username") == username
        assert response_data.get("password") == password
        

    def test_user_read(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})

        with app.app_context():
            user_id  = User.get_by_username(username=username )
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'
        if user_id:
            username = user_id.username
            password = user_id.password
            user_id = user_id.id

        else:
            request_data={"username":"username", "password":"password", "address":"address" ,"userType":"PRODUCER"}
            response = client.post("/user", json=request_data)
            response_data = response.json["data"]
            
            user_id = response_data.get("id")
            username = response_data.get("username")
            password = response_data.get("password")
            
        url =f"/user?id={user_id}"
        response = client.get(url)
    
        response_data = response.json["data"]
        assert response_data.get("username") == username
        assert response_data.get("password") == password

        
    def test_user_update(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})
        
        
        with app.app_context():
            user_id  = User.get_by_username(username=username )
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'
        if user_id:
            username = user_id.username
            password = user_id.password
            user_id = user_id.id

        else:
            request_data={"username":"username", "password":"password", "address":"address" ,"userType":"PRODUCER"}
            response = client.post("/user", json=request_data)
            response_data = response.json["data"]
            
            user_id = response_data.get("id")
            username = response_data.get("username")
            password = response_data.get("password")

        new_password = "newpassword"
        address = "new address"

        request_json = {"username":username, "oldPassword":password, "newPassword":new_password,"address":address}
        
        response = client.put("/user", json = request_json)

        response_data = response.json["data"]
        assert response_data.get("password") == new_password
        assert response_data.get("address") == address
    
    def test_user_delete(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})
    
        product_name = "book1"
        with app.app_context():
            product_id  = Product.get_by_name(name=product_name )
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'
            
        if product_id:
            product_id = product_id.id
        else:
            request_data={"name":"book1", "description":"a good book", "quantity":1}
            response = client.post("/product", json=request_data)
            response_data = response.json["data"]
            product_id = response_data.get("id")

        url =f"/product?id={product_id}"
        response = client.delete(url)
    
        response_data = response.json["data"]
        assert response_data.get("status") == True
        
    def test_user_list(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})

        product_name = "book1"
        with app.app_context():
            product_id  = Product.get_by_name(name=product_name )
            app.secret_key = 'super secret key'
            app.config['SESSION_TYPE'] = 'filesystem'
        if product_id:
            
            product_id=product_id.id        
        else:
            request_data={"name":"book1", "description":"a good book", "quantity":1}
            response = client.post("/product", json=request_data)
            response_data = response.json["data"]
            product_id = response_data.get("id")
        
        
        response = client.list("/product/list", json ={})

        response_data = response.json["data"]

        for a_product in response_data.get("products"):
            assert a_product.get("id") == product_id



class OrderTest:
        
    def test_order_add(client):
        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})
        
        request_data={"name":"book5", "description":"a good book", "quantity":1}
        response = client.post("/product", json=request_data)
        response_data = response.json["data"]
        product_id = response_data.get("id")

        username_customer = "username_customer"
        password_customer = "password_customer"
        address_customer = "address_customer"

        username,password = initial_user_create(username=username_customer, password=password_customer, address=address_customer, user_type="CUSTOMER")
        response = client.post("/login", json={"username":username, "password":password})
        

        request_data={"productId":product_id, "quantity":1}
        response = client.post("/order", json=request_data)

        response_data = response.json["data"]
        assert response_data.get("productId") == product_id
        assert response_data.get("quantity") == 1




    def test_order_read(client):



        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})
        
        request_data={"name":"book5", "description":"a good book", "quantity":1}
        response = client.post("/product", json=request_data)
        response_data = response.json["data"]
        product_id = response_data.get("id")

        username_customer = "username_customer"
        password_customer = "password_customer"
        address_customer = "address_customer"

        username,password = initial_user_create(username=username_customer, password=password_customer, address=address_customer, user_type="CUSTOMER")
        response = client.post("/login", json={"username":username, "password":password})
        

        request_data={"productId":product_id, "quantity":1}
        response = client.post("/order", json=request_data)


        response_data = response.json["data"]
        order_id  = response_data.get("id")

        url =f"/order?id={order_id}"
        response = client.get(url)
    
        response_data = response.json["data"]
        assert response_data.get("productId") == product_id
        assert response_data.get("id") == order_id
        assert response_data.get("quantity") == 1
        


    def test_order_edit(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})
        
        request_data={"name":"book5", "description":"a good book", "quantity":1}
        response = client.post("/product", json=request_data)
        response_data = response.json["data"]
        product_id = response_data.get("id")

        username_customer = "username_customer"
        password_customer = "password_customer"
        address_customer = "address_customer"

        username,password = initial_user_create(username=username_customer, password=password_customer, address=address_customer, user_type="CUSTOMER")
        response = client.post("/login", json={"username":username, "password":password})
        

        request_data={"productId":product_id, "quantity":1}
        response = client.post("/order", json=request_data)

        response_data = response.json["data"]
        order_id =response_data.get("id")
        new_order_quantity = 10
        request_json = {"id":order_id, "quantity":new_order_quantity}
        
        response = client.put("/product", json = request_json)

        response_data = response.json["data"]
        assert response_data.get("quantity") == new_order_quantity
    
    def test_order_delete(client):


        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})
        
        request_data={"name":"book5", "description":"a good book", "quantity":1}
        response = client.post("/product", json=request_data)
        response_data = response.json["data"]
        product_id = response_data.get("id")

        username_customer = "username_customer"
        password_customer = "password_customer"
        address_customer = "address_customer"

        username,password = initial_user_create(username=username_customer, password=password_customer, address=address_customer, user_type="CUSTOMER")
        response = client.post("/login", json={"username":username, "password":password})
        

        request_data={"productId":product_id, "quantity":1}
        response = client.post("/order", json=request_data)

        response_data = response.json["data"]
        order_id =response_data.get("id")

        url =f"/order?id={order_id}"
        response = client.delete(url)
    
        response_data = response.json["data"]
        assert response_data.get("status") == True
        
    def test_order_list(client):

        username,password = initial_user_create()
        response = client.post("/login", json={"username":username, "password":password})
        
        request_data={"name":"book5", "description":"a good book", "quantity":1}
        response = client.post("/product", json=request_data)
        response_data = response.json["data"]
        product_id = response_data.get("id")

        username_customer = "username_customer"
        password_customer = "password_customer"
        address_customer = "address_customer"

        username,password = initial_user_create(username=username_customer, password=password_customer, address=address_customer, user_type="CUSTOMER")
        response = client.post("/login", json={"username":username, "password":password})
        

        request_data={"productId":product_id, "quantity":1}
        response = client.post("/order", json=request_data)

        response_data = response.json["data"]
        order_id = response_data.get("id")
        
        response = client.list("/order/list", json ={})

        response_data = response.json["data"]

        for a_order in response_data.get("orders"):
            assert a_order.get("id") == order_id
