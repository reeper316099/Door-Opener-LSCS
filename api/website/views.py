import asyncio
import json
import os
import time
import sys
from datetime import datetime
import random
from flask import Blueprint, render_template, request, jsonify, redirect, current_app
import hmac
import hashlib
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from control import Control

views = Blueprint("views", __name__)
is_opened = False
last_updated = time.time()
API_TIMEOUT = 10

load_dotenv()
SHARED_SECRET = os.getenv("API_SECRET_KEY")
TIME_WINDOW = 60

@views.before_app_request
def initialize_gpio():
    Control.setup()

def generate_time_key():
    print(SHARED_SECRET)
    time_chunk = int(time.time() // TIME_WINDOW)
    key = hmac.new(SHARED_SECRET.encode(), str(time_chunk).encode(), hashlib.sha256)

    return key.hexdigest()


@views.route("/")
def home():
    return render_template("home.html")

@views.route("/key")
def key():
    return generate_time_key()

@views.route("/api/open")
def open_door():
    global is_opened, last_updated
    client_key = request.args.get("key")

    if client_key not in (generate_time_key(),):
          return {"success": False, "error": "unauthorized"}, 401

    start_time = time.time()
    Control.open()

    while not Control.verified_open():
        if time.time() - start_time >= API_TIMEOUT:
            return {"success": False}

    is_opened = True
    last_updated = time.time()
    return {"success": True}

@views.route("/fopen")
def fopen():
    Control.open()
    return "ok"

@views.route("/fclose")
def fclose():
    Control.close()
    return "ok"

@views.route("/freset")
def freset():
    Control.clean()
    return "ok"

@views.route("/api/close")
def close_door():
    global is_opened, last_updated
    client_key = request.args.get("key")

    if client_key not in (generate_time_key(),):
          return {"success": False, "error": "unauthorized"}, 401

    start_time = time.time()
    Control.close()

    while Control.verified_open():
        if time.time() - start_time >= API_TIMEOUT:
            return {"success": False}

    is_opened = False
    last_updated = time.time()
    return {"success": True}

@views.route("api/status")
def status():
    client_key = request.args.get("key")

    if client_key not in (generate_time_key(),):
        return {"success": False, "error": "unauthorized"}, 401

    return {"api": True, "opened": is_opened, "position": 100, "power_supply": Control.get_estimated_power(), "wifi_network": "staff-net", "last_updated": int(last_updated)}
