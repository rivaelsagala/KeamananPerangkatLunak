from flask import render_template
from flask import render_template
import os
import sys

class IndexController:
    @staticmethod
    def index():
        return render_template("index.html")
    
    @staticmethod
    def decryption():
        return render_template("decryption.html")
    