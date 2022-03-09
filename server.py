from email.headerregistry import Address
from flask import Flask, abort, request
from mock_data import catalog, coupons
import json
from about_me import me
import random
import string
from flask_cors import CORS
from config import db



def address_page():
    address=me["address"]
    print(address["street"] + " " + address["city"] + " " + address["state"])

# create the server/app
app = Flask("server")
CORS(app) #ALLOWS SERVER TO BE CALLED FROM ANY ORIGIN

@app.route("/", methods=["get"])
def home_page():
    return "Under Construction!"

@app.route("/test")
def test():
    return "Test Page" 

@app.route("/about")
def about_me():
    return "This Page is All About Me"

@app.route("/myaddress")
def address_page():
    address=me["address"]
    return f'Send Mail Here {address["street"]} {address["city"]} {address["state"]}'

# ########################################
# ########### API ENDPOINT ###############
# ########################################


@app.route("/api/catalog", methods=["POST"])
def save_product():
    product= request.get_json() # READ THE PAYLOAD AS A DICTIONARY FROM JSON STRING

    #validate
    #title are longer than 3 chars long
    if not "title" in product or len(product["title"]) < 3:
        return abort(400, "Input a title longer than 3 characters")

    #must have a price
    if not "price" in product or product["price"] <= 0:
        return abort(400, "Add a price, we're trying to make money here")

    if not isinstance(product["price"], float) and not isinstance(product["price"], int):
        return abort(400, "Add a price, we're trying to make money here")

    # product["_id"]= random.randint(1000000,9000000)
    # catalog.append(product) #save it to local catalog

    db.products.insert_one(product)
    # HACK TO FIX THE ID
    product["_id"] = str(product["_id"])
    return json.dumps(product)

##############################################
######### API METHOD FOR COUPON CODES ########
##############################################

@app.route("/api/coupons", methods=["POST"])
def save_coupon():
    coupon=request.get_json()

    if not "name" in coupon:
        return abort(400, "Whats the name of this deal?")
    if not "discount" in coupon:
        return abort(400, "How much is the discount?")
    if not "_id" in coupon:
        coupon["_code"]= ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

    coupons.append(coupon)

    return json.dumps(coupon)
# 
# 
# GET ALL get /api/coupons
@app.route("/api/coupons")
def get_coupons():
    return json.dumps(coupons)
# 
# GET BY CODE get /api/coupons/<code>
@app.route("/api/coupons/<code>")
def get_coupon(code):
    for coupon in coupons:
        if code==coupon["_code"]:
            return json.dumps(coupon)

    return abort(404)

@app.route("/api/catalog")
def get_catalog():
    cursor = db.products.find({})
    results = []
    for prod in cursor:
        prod["_id"] = str(prod["_id"])
        results.append(prod)
        
    return json.dumps(results)

@app.route("/api/catalog/count")
def get_count():
    cursor = db.products.find({})
    count = 0
    for prod in cursor:
        count += 1
    # len(catalog)
    return json.dumps(count)

#get api/catalog/sum
# sum of all prices
@app.route("/api/catalog/sum")
def get_sum():
    total=0
    for product in catalog:
        total += product["price"]

    result = f'$ {total}'
    return json.dumps(result)

# GET API/PRODUCT/<ID>
# GET A PRODUCT BY ITS ID
@app.route("/api/product/<id>")
def get_product(id):
    for product in catalog:
        if id == product["_id"]:
            return json.dumps(product)

    return abort(404) #404 NOT FOUND

# GET API/PRODUCT/MOST_EXPENSIVE
# 
@app.route("/api/product/price")
def get_most_expensive():
    pivot = catalog[0]
    for product in catalog:
        if pivot["price"] < product["price"]:
            pivot = product
    return json.dumps(pivot)

@app.route("/api/product/categories")
def get_catagories():
    category_list = []
    
    for product in catalog:
        category = product["category"]
        if not category in category_list:
            category_list.append(category)

    return json.dumps(category_list)


@app.route("/api/catalog/<category>")
def get_all_category(category):
    results=[]
    cursor = db.products.find({"category": category})
    for product in cursor:
        product["_id"]=str(product["_id"])
        results.append(product)

    return json.dumps(results)


# start the server
app.run(debug=True)
