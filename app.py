from flask import Flask, request, jsonify, make_response, abort
from pydantic import BaseModel 
import uuid
from typing import List
import re

app = Flask(__name__)

class Item(BaseModel):
    shortDescription: str
    price: str

class Receipt(BaseModel):
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: List[Item]
    total: str

receipts = {}
points = {}

def validate_retailer(retailer: str):
    if re.match("^\\S+$", retailer):
        raise ValueError("Invalid retailer")

def validate_purchase_date(purchase_date: str):
    if not re.match("^\\d{4}-\\d{2}-\\d{2}$", purchase_date):
        raise ValueError("Invalid purchase date")

def validate_purchase_time(purchase_time: str):
    if not re.match("^\\d{2}:\\d{2}$", purchase_time):
        raise ValueError("Invalid purchase time")

def validate_total(total: str):
    if not re.match("^\\d+\\.\\d{2}$", total):
        raise ValueError("Invalid total")

def validate_short_description(short_description: str):
   if re.match(r"^\\S+$", short_description.strip()):
        raise ValueError("Invalid short description")


def validate_price(price: str):
    if not re.match("^\\d+\\.\\d{2}$", price):
        raise ValueError("Invalid price")

@app.route("/receipts/process", methods=["POST"])
def process_receipt():
    receipt = Receipt(**request.get_json())
    validate_retailer(receipt.retailer)
    validate_purchase_date(receipt.purchaseDate)
    validate_purchase_time(receipt.purchaseTime)
    validate_total(receipt.total)
    for item in receipt.items:
        validate_short_description(item.shortDescription)
        validate_price(item.price)
    receipt_id = str(uuid.uuid4())
    receipts[receipt_id] = receipt
    points[receipt_id] = calculate_points(receipt)
    return jsonify({"id": receipt_id}), 200

@app.route("/receipts/<receipt_id>/points", methods=["GET"])
def get_points(receipt_id):
    if receipt_id not in receipts:
        abort(404)
    return jsonify({"points": points[receipt_id]})

import datetime


def calculate_points(receipt):
    points = 0
    purchase_date = datetime.datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    purchase_time = datetime.datetime.strptime(receipt.purchaseTime, "%H:%M").time()

    points += len([c for c in receipt.retailer if c.isalnum()])
    if purchase_time >= datetime.time(14, 0) and purchase_time < datetime.time(16, 0):
        points += 10
    if purchase_date.day % 2 == 1:
        points += 6
    if float(receipt.total) % 0.25 == 0:
        points += 25
    if float(receipt.total).is_integer():
        points += 50
    points += 5 * (len(receipt.items) // 2)
    for item in receipt.items:
        trimmed_description = item.shortDescription.strip()
        if len(trimmed_description) % 3 == 0:
            points += round(float(item.price) * 0.2)
    return points


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)