from flask import Flask, request , session
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
import os
import bcrypt
import uuid
from flask_migrate import Migrate
import psycopg2

from sqlalchemy.sql import func

import common_utilities as common_utilities

app = Flask(__name__)

docker = False
if docker:
    POSTGRES_DATABASE_USER = "postgres"
    POSTGRES_DATABASE_PASSWORD = os.getenv("db_root_password")
    POSTGRES_DATABASE_DB = os.getenv("db_name")
    POSTGRES_DATABASE_HOST = os.getenv("POSTGRES_SERVICE_HOST")
    POSTGRES_DATABASE_PORT = int(os.getenv("POSTGRES_SERVICE_PORT"))
else:
    POSTGRES_DATABASE_USER = "shiblnasser"
    POSTGRES_DATABASE_PASSWORD = "postgres"
    POSTGRES_DATABASE_DB = "postgres"
    POSTGRES_DATABASE_HOST = "localhost"
    POSTGRES_DATABASE_PORT = 5432
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{POSTGRES_DATABASE_USER}:{POSTGRES_DATABASE_PASSWORD}@{POSTGRES_DATABASE_HOST}:{POSTGRES_DATABASE_PORT}/{POSTGRES_DATABASE_DB}"


#f"postgresql://{MYSQL_DATABASE_USER}:{MYSQL_DATABASE_PASSWORD}@{MYSQL_DATABASE_HOST}:{MYSQL_DATABASE_PORT}/{MYSQL_DATABASE_DB}"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#migrate = Migrate(app, db)


common_utilities.MESSAGES = {"DEFAULT":"Error ocurred", "INVALID_DATA_TYPE":"Please enter valid datatype"}

class Product(db.Model):
    """
    Product Class
    
    id  - str, primary key
    user_id - foreign key from the User Model
    name - str
    orders - back reference to the Order Model
    status - ACTIVE / DELETED 
    description - str
    quantity - integer
    created_on - timestamp
    updated_on - timestamp
    """


    id = db.Column('id', db.String(50), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False, unique = False)
    orders = db.relationship('Orders', backref='product')
    status = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_json(self):
        """
        this function is used for converting the attributes of objects to json
        """
        response_json = {}
        
        response_json["id"] = self.id
        response_json["name"] = self.name
        response_json["description"] = self.description
        response_json["userId"] = self.user_id
        user_id =User.get_id(id = self.user_id)
        
        if user_id and user_id.user_type == "CUSTOMER":
            response_json["orders"] = self.orders
        response_json["quantity"] = self.quantity
        response_json["createdOn"] = self.created_on
        response_json["updatedOn"] = self.updated_on
        return response_json
        
    @classmethod
    def add(cls, user_id, name, description , quantity, id = None):
        """
        function used for adding product entry to the model
        """
        status = False
        if not id:
            id = str(uuid.uuid4())
    
        product = cls(id = id, user_id = user_id , name = name, status = "ACTIVE", description = description, quantity= quantity)
        
        db.session.add(product)
        db.session.commit()
        status = True
        return status , product
    
    @classmethod
    def list(cls, user_id = ""):
        """
        function used for listing all the products based on user_id
        """
        status = False

        if user_id:
            products = cls.query.filter_by(user_id = user_id, status  = "ACTIVE")
        else:
            products = cls.query.filter_by( status  = "ACTIVE")
        
        status = True
        return status ,products
    
    @classmethod
    def get_id(cls, id):
        """
        function used for fetching entry from the model by id
        """
        product = cls.query.filter_by(id=id, status = "ACTIVE").first()
        return product

    @classmethod
    def get_by_name(cls, name):
        """
        function used for fetching entry from the model by name
        """
        product = cls.query.filter_by(name=name, status = "ACTIVE").first()
        return product

    @classmethod
    def delete(cls,ids):
        """
        function used for deleting entry from the model by ids
        """
        status = True 
        for a_id in ids:
            product = cls.get_id(id = a_id)
            if product:
                if product.orders:
                    status = False
                else:
                    product.status = "DELETED"
        db.session.commit()
        return status
        
    @classmethod
    def update(cls,id, updated_values):
        """
        function used for updating entry 
        """
        
        status = False
        product = cls.get_id(id = id)
        if product:
            for key, value in updated_values.items():                
                setattr(product, key, value)
            db.session.commit()
            status = True
        return status ,product
class User(db.Model):

    """
    User Class
    
    id  - str, primary key
    username - str, unique
    password - str
    user_type - CUSTOMER/PRODUCER
    products - back reference to product class
    orders - back reference to orders class
    status - ACTIVE / DELETED 
    address - str
    created_on - timestamp
    updated_on - timestamp
    """

    id = db.Column('id', db.String(50), default=lambda: str(uuid.uuid4()), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique = True)
    password = db.Column(db.String(100), nullable=False )
    user_type = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='user')
    orders = db.relationship('Orders', backref='user')
    status = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_json(self, is_detail=False):
        """
        this function is used for converting the attributes of objects to json
        """
        response_json = {}
        response_json["id"] = self.id
        response_json["username"] = self.username
        response_json["password"] = self.password
        response_json["userType"] = self.user_type
        if is_detail:
            response_json["products"] = self.products
        response_json["address"] = self.address
        response_json["createdOn"] = self.created_on
        response_json["updatedOn"] = self.updated_on
        return response_json
        
    @classmethod
    def add(cls, username, password , user_type, address, id = None):
        """
        function used for adding user entry to the model
        """
        message = ""
        status = False
        user = None
        if cls.get_by_username(username=username):
            message = common_utilities.MESSAGES.get("USERNAME_ALREADY_EXISTS")
        else:
            if not id:
                id = str(uuid.uuid4())
            user = cls(id = id, username = username, status = "ACTIVE", user_type = user_type , password = password, address= address)
            
            db.session.add(user)
            db.session.commit()
            status = True
        return status , message, user
    
    @classmethod
    def list(cls):
        """
        function used for listing all the user 
        """
        status = False
        users = cls.query.filter_by(status = "ACTIVE")
        status = True
        return status ,users
    
    
    @classmethod
    def get_id(cls, id):
        """
        function used for fetching single entry by id
        """
        user = cls.query.filter_by(id=id, status = "ACTIVE").first()
        return user
    
    @classmethod
    def get_by_username(cls, username):
        """
        function used for fetching single entry by username
        """
        user = cls.query.filter_by(username=username, status = "ACTIVE").first()
        return user
    

    @classmethod
    def validate_username_password(cls, username, password):
        """
        function used for validating password
        """
        status = False
        message = ""
        user = cls.get_by_username(username=username)
        if user:

            if password == user.password:
                status = True
            else:
                message = common_utilities.MESSAGES.get("INVALID_PASSWORD")

        else:
            message = common_utilities.MESSAGES.get("INVALID_USERNAME")
        return status,message
    @classmethod
    def delete(cls,id):
        """
        function used for deleting user entry
        """
        message = ""
        
        user_id = cls.get_id(id = id)
        status = False
        if user_id:
            status = True
            if user_id.user_type == "PRODUCER":
                _ , products = Product.list(user_id = user_id.id)
                if products.count():
                    message = common_utilities.MESSAGES.get("USER_PRODUCER")
                    status = False
            elif user_id.user_type == "CONSUMER":
                _ , orders = Orders.list(user_id = user_id.id)
                if orders.count():
                    message = common_utilities.MESSAGES.get("USER_CONSUMER")
                    status = False
        if status:
            user_id.status = "DELETED"
            db.session.commit()
            status = True
        return status,message
        
    @classmethod
    def update(cls,id, updated_values):
        """
        function used for updating user entry
        """
        status = False
        user = cls.get_id(id = id)
        if user:
            for key, value in updated_values.items():                
                setattr(user, key, value)
            db.session.commit()
            status = True
        return status ,user
class Orders(db.Model):

    """
    Orders Class

    id  - str, primary key
    user_id - foreign key from User model
    product_id - foreign key from product model
    status - ACTIVE / DELETED 
    quantity - int
    created_on - timestamp
    updated_on - timestamp
    """
    
    id = db.Column('id', db.String(50), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'))
    product_id = db.Column(db.String(50), db.ForeignKey('product.id'))
    status = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_json(self):
        """
        this function is used for converting the attributes of objects to json
        """
        response_json = {}
        response_json["id"] = self.id
        response_json["userId"] = self.user_id
        response_json["productId"] = self.product_id
        response_json["quantity"] = self.quantity
        response_json["createdOn"] = self.created_on
        response_json["updatedOn"] = self.updated_on
        return response_json
        
    @classmethod
    def add(cls,user_id, product_id  , quantity, id = None):
        """
        function used for adding order entry to the model
        """
        status = False
        if not id:
            id = str(uuid.uuid4())
        order = cls(id = id,product_id=product_id, status = "ACTIVE", user_id = user_id, quantity= quantity)
        
        db.session.add(order)
        db.session.commit()
        status = True
        return status , order
    
    @classmethod
    def list(cls, user_id):
        """
        function used for listing order based upon user_id
        """
        status = False
        orders = cls.query.filter_by(user_id = user_id , status = "ACTIVE")
        status = True
        return status ,orders
    
    @classmethod
    def get_id(cls, id):
        """
        function used for fetching single  order entry by id
        """
        order = cls.query.filter_by(id=id, status = "ACTIVE").first()
        return order
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """
        function used for fetching single  order entry by user_id
        """
        order = cls.query.filter_by(user_id=user_id, status = "ACTIVE")
        return order
    
    @classmethod
    def delete(cls,id):
        """
        function used for deleting entry
        """
        status  =False
        order = cls.get_id(id = id)
        if order:
            db.session.delete(order)
            db.session.commit()
            status = True
        return status
        
    @classmethod
    def update(cls,id, updated_values):
        """
        function used for updating single order entry 
        """
        status = False
        order_initial = cls.get_id(id = id)
        initial_time = None

        if order_initial:
            initial_time = order_initial.updated_on
            for key, value in updated_values.items():                
                setattr(order_initial, key, value)
            order_final = cls.get_id(id = id)
            if order_final.updated_on == initial_time:
                db.session.commit()
            status = True
        return status ,order_initial

class BaseMethod(MethodView):
    CONTINUE_PROCESS= True
    ENCRYPTION_RESPONSE = False
    AUTHENTICATION_REQUIRED = False
    AUTHENTICATION_REQUIRED_FOR = ["POST", "DELETE", "PUT", "GET"]

    def __init__(self):
        if request.method in self.AUTHENTICATION_REQUIRED_FOR:
            if self.AUTHENTICATION_REQUIRED:
                if not session:
                    self.CONTINUE_PROCESS = False
            
    def get(self):
        request_json = {}
        if self.CONTINUE_PROCESS:
            request_json = request.args.to_dict(flat=False)
            request_json=common_utilities.format_json(request_json=request_json)
            request_json = common_utilities.decode(request_json=request_json)
            request_json  = self.process_get_request(request_json=request_json)
            if self.ENCRYPTION_RESPONSE:
                request_json  = common_utilities.encode(request_json=request_json)
        else:
            request_json = {"status":False, "message":common_utilities.MESSAGES.get("AUTHENTICATION_FAILED")}
        return request_json
    
    def post(self):
        request_json = {}
        if self.CONTINUE_PROCESS:
            request_json = request.json        
            request_json = common_utilities.decode(request_json=request_json)
            request_json  = self.processs_post_request(request_json=request_json)
            if self.ENCRYPTION_RESPONSE:
                request_json  = common_utilities.encode(request_json=request_json)
        else:
            request_json = {"status":False, "message":common_utilities.MESSAGES.get("AUTHENTICATION_FAILED")}

        return request_json
    
    def put(self):
        request_json = {}
        if self.CONTINUE_PROCESS:
            request_json = request.json        
            request_json = common_utilities.decode(request_json=request_json)
            request_json  = self.processs_put_request(request_json=request_json)
            if self.ENCRYPTION_RESPONSE:
                request_json  = common_utilities.encode(request_json=request_json)
        else:
            request_json = {"status":False, "message":common_utilities.MESSAGES.get("AUTHENTICATION_FAILED")}

        return request_json
    
    def delete(self):
        request_json = {}
        if self.CONTINUE_PROCESS:
            request_json = request.args.to_dict(flat=False)
            request_json=common_utilities.format_json(request_json=request_json)
            request_json = common_utilities.decode(request_json=request_json)
            request_json  = self.processs_delete_request(request_json=request_json)
            if self.ENCRYPTION_RESPONSE:
                request_json  = common_utilities.encode(request_json=request_json)
        else:
            request_json = {"status":False, "message":common_utilities.MESSAGES.get("AUTHENTICATION_FAILED")}

        return request_json
    
    
    def process_get_request(self,request_json = None):
        pass
    def processs_post_request(self,request_json = None):
        return
    def processs_put_request(self,request_json = None):
        return
    
    def processs_delete_request(self, request_json = None):
        return
    

class ProductCRUDOperation(BaseMethod):
    
    AUTHENTICATION_REQUIRED = False
    
    def processs_post_request(self,request_json = None):
        
        status = False
        response_json = {"status":status}
        validation_json = {"required":{"name":str, "description":str, "quantity":int}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
            
        if Product.get_by_name(name = request_json.get("name", "")):
            response_json["message"] = common_utilities.MESSAGES.get("ALREADY_EXISTS")
        else:
            username = common_utilities.get_username(session=session)
            user_id = User.get_by_username(username=username)
            if user_id and user_id.user_type == "PRODUCER":
                status , product = Product.add(user_id =user_id.id, name = request_json.get("name"),description = request_json.get("description"),quantity = request_json.get("quantity"))
            else:
                status = False
                response_json.update({"status":status, "message":common_utilities.MESSAGES.get("USER_TYPE_INCORRECT")})
            if status:
                response_json.update({"status":status, "message":common_utilities.MESSAGES.get("SUCCESSFULLY_CREATED")})
                response_json["data"] = product.to_json()
            
        return response_json
    
    def processs_put_request(self,request_json = None):
       
        status = False
        response_json = {"status":status}
        validation_json = {"required":{"id":str}, "optional":{"description":str, "quantity":int}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
        else:
            status  = False
            username = common_utilities.get_username(session=session)
            user_id = User.get_by_username(username=username)
        
            if user_id:
                product_id = request_json.pop("id")
                product = Product.get_id(id = product_id)
        
                if product:
                    if user_id.id == product.user_id:
                        status , product = Product.update(id = product_id, updated_values=request_json)
        if status:
            response_json.update({"status":status, "message":common_utilities.MESSAGES.get("UPDATED")})

            response_json["data"] = product.to_json()
            
        return response_json
    
    def processs_delete_request(self,request_json = None):
        status = False
        response_json = {"status":status}
        validation_json = {"required":{"id":str}}
        
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
        else:
            status = False
            username = common_utilities.get_username(session=session)
            user_id = User.get_by_username(username=username)
        
            if user_id:

                product = Product.get_id(id = request_json.get("id"))
                if product:
                    if user_id.id == product.user_id:
                        status = Product.delete(ids = [request_json.get("id")])
        if status:
            response_json.update({"status":status, "message":common_utilities.MESSAGES.get("DELETED")})
    
        return response_json

    def process_get_request(self,request_json):
        
        status = False
        response_json = {"status":status}
        validation_json = {"required":{"id":str}}

        
        
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
        status = False
        username = common_utilities.get_username(session=session)
        user_id = User.get_by_username(username=username)
        
        if user_id:
            product = Product.get_id(id = request_json.get("id"))   
            if product:
                
                if user_id.user_type == "ADMIN" or product.user_id == user_id.id:
                    status  = True

        if status:
            response_json.update({"status":True})
            response_json["data"] = product.to_json()
        else:
            response_json.update({"status":False})
        return response_json

class ListProduct(BaseMethod):
    AUTHENTICATION_REQUIRED =False

    def processs_post_request(self,request_json = None):
       
        status = False
        response_json = {"status":status}
        validation_json = {"optional":{"userId":str}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
        
    
        else:
            status , products = Product.list(user_id=request_json.get("userId"))
        
            if status:
                response_json.update({"status":status, "data" :{"products":[]}})
                for a_product in products:
                    response_json["data"]["products"].append(a_product.to_json())

            
        return response_json
    
  


class UserCRUDOperation(BaseMethod):
    AUTHENTICATION_REQUIRED = False
    def processs_post_request(self,request_json = None):
        status = False
        response_json = {"status":status}

        validation_json = {"required":{"username":str, "password":str, "userType":str, "address":str}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
            
        else:
            status , message, user = User.add(username= request_json.get("username"),password = request_json.get("password"),user_type = request_json.get("userType"), address= request_json.get("address"))
            
            if status:
                response_json.update({"status":status, "message":common_utilities.MESSAGES.get("successfully created")})

                response_json["data"] = user.to_json()
            else:
                response_json["message"] = message
        return response_json
    
    def processs_put_request(self,request_json = None):
        status = False
        response_json = {"status":status}
       
        validation_json = {"required":{"username":str, "oldPassword":str, "newPassword":str}, "optional":{"password":str, "address":str}}

        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
        else:
            status= False
            username = request_json.pop("username")
            user_id =User.get_by_username(username=username)
            old_password = request_json.get("oldPassword")
            
            if old_password == user_id.password:
                updated_values = {}
                field_mapper = {"newPassword":"password", "address":"address"}
                for key, value in field_mapper.items():
                    if key in request_json:
                        updated_values[value] = request_json.get(key)

              
                status , user = User.update(id = user_id.id, updated_values=updated_values)
            
            else:
                status = False
            if status:
                response_json.update({"status":status, "message":common_utilities.MESSAGES.get("UPDATED"), "data": user.to_json()})
            else:
                response_json.update({"status":status, "message":common_utilities.MESSAGES.get("FAILED")})
        return response_json
    
    def processs_delete_request(self,request_json = None):
        status = False
        message = ""
        response_json = {"status":status}
        validation_json = {"required":{"id":str}}
       
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))

        status, message = User.delete(id =request_json.get("id"))
        if status:
            response_json.update({"status":status, "message":common_utilities.MESSAGES.get("DELETED")})
        else:
            response_json.update({"status":status,"message":message})
        return response_json

    def process_get_request(self,request_json):
        status = False
        response_json = {"status":status}
        validation_json = {"required":{"id":str}}   
        
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
            
        user = User.get_id(id = request_json.get("id"))
        if user:
            status = True
            response_json.update({"status":status})
            response_json["data"] = user.to_json()
            
        return response_json

class ListUser(BaseMethod):

    def processs_post_request(self,request_json = None):
       
        status = False
        response_json = {"status":status}
        validation_json = {"optional":{}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
        
        else:
            status , users = User.list()
            if status:
                response_json.update({"status":status, "data" :{"users":[]}})
                for a_user in users:
                    response_json["data"]["users"].append(a_user.to_json())

            
        return response_json
    
  

class OrderCRUDOperation(BaseMethod):

    def processs_post_request(self,request_json = None):
        status = False
        response_json = {"status":status}

        validation_json = {"required":{ "productId":str, "quantity":int}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
            
        else:
            username = common_utilities.get_username(session=session)
            user_id = User.get_by_username(username=username)

            if user_id and user_id.user_type == "CUSTOMER":
                status , order = Orders.add(user_id = user_id.id,product_id=request_json.get("productId"), quantity=request_json.get("quantity"))
            else:
                status = False
            if status:
                response_json.update({"status":status, "message":common_utilities.MESSAGES.get("successfully created")})

                response_json["data"] = order.to_json()
            
        return response_json
    
    def processs_put_request(self,request_json = None):
        status = False
        response_json = {"status":status}
        validation_json = {"required":{"id":str}, "optional":{"quantity":int}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
        else:
            order_id = request_json.pop("id")
            status , order = Orders.update(id = order_id, updated_values=request_json)
            if status:
                response_json.update({"status":status, "message":common_utilities.MESSAGES.get("UPDATED")})

                response_json["data"] = order.to_json()
                
        return response_json
    
    def processs_delete_request(self,request_json = None):
        status = False
        
        response_json = {"status":status}
        validation_json = {"required":{"id":str}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
            
        status = Orders.delete(id =request_json.get("id"))
        if status:
            response_json.update({"status":status, "message":common_utilities.MESSAGES.get("DELETED")})
    
        return response_json

    def process_get_request(self,request_json):
        status = False
        response_json = {"status":status}
        validation_json = {"required":{"id":str}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
            
        order = Orders.get_id(id = request_json.get("id"))
        if order:
            status = True
            response_json.update({"status":status})

            response_json["data"] = order.to_json()
            
        return response_json

class ListOrder(BaseMethod):
    
    def processs_post_request(self,request_json = None):
       
        status = False
        response_json = {"status":status}
        validation_json = {"optional":{}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
        
        else:
            username = common_utilities.get_username(session=session)
            
            user_id = User.get_by_username(username=username)
            status , orders = Orders.list(user_id=user_id.id)
            if status:
                response_json.update({"status":status, "data" :{"orders":[]}})
                for a_order in orders:
                    response_json["data"]["orders"].append(a_order.to_json())

            
        return response_json
    



class LoginClass(BaseMethod):
    AUTHENTICATION_REQUIRED = False

    def processs_post_request(self,request_json = None):
        session.clear()
        status = False
        response_json = {"status":status}
        validation_json = {"required":{"username":str, "password":str}}
        status = common_utilities.validate_json(request_json=request_json,validation_json=validation_json)
        if status == False:
            response_json["message"] = common_utilities.MESSAGES.get("INVALID_DATA_TYPE", common_utilities.MESSAGES.get("DEFAULT", ""))
            
        else:
            status,message =User.validate_username_password(username=request_json.get("username"), password=request_json.get("password"))
            if status:
                session["username"] =request_json.get("username")
                response_json["status"] = status

            
        return response_json


class LogoutClass(BaseMethod):
    
    AUTHENTICATION_REQUIRED = False
    def process_get_request(self,request_json):
        
        status = True
        response_json = {"status":status}
        session.clear()
       
        return response_json





app.add_url_rule("/product",view_func=ProductCRUDOperation.as_view("product"))
app.add_url_rule("/product/list",view_func=ListProduct.as_view("list-product"))

app.add_url_rule("/user",view_func=UserCRUDOperation.as_view("user"))
app.add_url_rule("/user/list",view_func=ListUser.as_view("list-user"))

app.add_url_rule("/order",view_func=OrderCRUDOperation.as_view("order"))
app.add_url_rule("/order/list",view_func=ListOrder.as_view("list-order"))

app.add_url_rule("/login",view_func=LoginClass.as_view("login"))
app.add_url_rule("/logout",view_func=LogoutClass.as_view("logout"))





with app.app_context():
    db.create_all()

if __name__ == '__main__': 
    
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(host="0.0.0.0", port=5000)
