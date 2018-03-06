#######################################################################
# 
# Copyright (C) 2018 Romeo Abulencia 
#
# Author: romeo abulencia <romeo.abulencia@gmail.com>
# Maintainer: romeo abulencia <romeo.abulencia@gmail.com> 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details. 
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>. 
#######################################################################
import getpass
import datetime
import random
import ast
import json
from python_module_check import import_or_install
import_or_install(['oerplib', 'psycopg2'])
import oerplib
import psycopg2


initial_vars = [
#(var_name,message,target_data_type, default_value)
('login_name','Login name (default: admin): ',str,'admin'),
('password','Enter password (default: admin): ',str,'admin'),
]
for var,msg,datatype,default_val in initial_vars:
    if var == 'password':
        if 'login_name' in locals() and login_name != 'admin':
            temp = datatype(getpass.getpass(msg))
        else:
            temp = default_val
    else:
        temp = raw_input(msg)


    if temp:
        locals()[var]=datatype(temp)
    else:
        locals()[var]=default_val

temp_str="""
Choose a connection :
1 : localhost
2 : others
Please Enter your choice (default: localhost): 
"""
connection_mode = raw_input(temp_str) or '1'
cm_bank = {
'1':'localhost',
'2':'others',
}
# Prepare the connection to the Odoo server
if cm_bank[connection_mode] == 'localhost':
    oerp = oerplib.OERP('localhost', protocol='xmlrpc', port=8069, database="odoo_9_stage")
    conn = psycopg2.connect("dbname=odoo_9_stage user=odoo_9_dev password=odoo_9_dev")
elif cm_bank[connection_mode] == 'others':
    server = raw_input('Enter server address: ')
    database = raw_input('Enter database name: ')
    dbuser = raw_input('Enter database user (default: odoo_9_dev): ')
    dbpass = raw_input("Enter database user's password (default: odoo_9_dev): ")
# temp_bank=['dbuser','dbpass']
# for temp_elem in temp_bank:
#     if not locals().get(temp_elem):
#         locals()[temp_elem]='odoo_9_dev'

    oerp = oerplib.OERP(server=server, database=database, protocol='xmlrpc', port=8069)
    conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (server,database,dbuser,dbpass) )

print 'login_name used : ',login_name
print 'password used : ',password
class odoo_connect:
    cr = conn.cursor()
    user = oerp.login(user=login_name, passwd=password)
    pool = oerp.get