from django.shortcuts import render_to_response
import MySQLdb

def Connect_BD():
  # Connect with LATIN database credentials
  db = MySQLdb.connect("localhost","latincomm","poi9.34LATI21","latincomm")
  return db
