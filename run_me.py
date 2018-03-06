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

# -*- coding: utf-8 -*-

from python_module_check import import_or_install
import glob
from odoo_connect import odoo_connect

import_or_install(['pandas','openpyxl'])
import pandas as pd

file_path_options = glob.glob('./*.xls*')
#TODO
#Create a more convenient user selection for file selection
# pd_file_path=raw_input("Input file path or press enter for %s :" % file_path_options) \
#     or default_pd_file_path
pd_file_path = file_path_options[0]


data_dict =  pd.read_excel(pd_file_path, 
                          sheet_name = [0,1]
                          )
sheet_1 = data_dict[0]
#sheet_1[0] = product default_code
#sheet_1[1] = product name
temp = sheet_1.columns
s1_header_default_code = temp[0]
s1_header_name = temp[1]

sheet_2 = data_dict[1]
#sheet_2[0] = product default_code
#sheet_2[1] = product barcode
temp = sheet_2.columns
s2_header_default_code = temp[0]
s2_header_barcode = temp[1]

main_data_dict = {}
#TODO:#duplicate sheet 1 default_code handling
main_data_dict_dup = {}


#fetch default_code and product name from sheet 1
for count, temp_default_code in enumerate(sheet_1[s1_header_default_code]):

    if temp_default_code not in main_data_dict:

        main_data_dict[temp_default_code] = {'name':str(sheet_1.at[count,s1_header_name])}
        #fetch barcode from sheet 2 via default_code
        temp_s2_target_row = sheet_2.loc[sheet_2[s2_header_default_code] == temp_default_code]
        main_data_dict[temp_default_code]['barcode'] = str(sheet_2.at[temp_s2_target_row.index.values[0],s2_header_barcode])

    else:
#         TODO:duplicate sheet 1 default_code handling
        main_data_dict_dup[temp_default_code] = {'name':sheet_1.at[count,s1_header_name]}
    
pp_obj = odoo_connect.pool('product.product')


target_default_codes = tuple([str(x) for x in main_data_dict.keys()])
odoo_connect.cr.execute('select pp.default_code,pt.name,pp.barcode,pp.id from product_product pp join product_template pt on pt.id = pp.product_tmpl_id where pp.default_code in %s',(target_default_codes,))
temp = odoo_connect.cr.fetchall()
existing_product_data = {}
for temp_res in temp:
    existing_product_data[temp_res[0]] = {'name':temp_res[1],
                                        'barcode':temp_res[2],
                                        'product_id':temp_res[3]}
write_to_excel_signal = False

for temp_default_code in main_data_dict:
#   Odoo entry creation
    if temp_default_code not in existing_product_data:
        pp_data = {'default_code':temp_default_code,
                 'barcode':str(main_data_dict[temp_default_code]['barcode']),
                 'name':str(main_data_dict[temp_default_code]['name'])}
        new_product_id = pp_obj.create(pp_data)
#   file's name should be updated, odoo's barcode should be updated when they're different
    else:
#       check for name value difference
        if existing_product_data[temp_default_code]['name']!=main_data_dict[temp_default_code]['name']:
#           update exccel file's name value
            temp_s1_target_row = sheet_1.loc[sheet_1[s1_header_default_code] == temp_default_code]
            sheet_1.at[temp_s1_target_row.index.values[0],s1_header_name] = existing_product_data[temp_default_code]['name']
            if not write_to_excel_signal:
                write_to_excel_signal = True

#       check for barcode value difference
        elif existing_product_data[temp_default_code]['barcode']!=main_data_dict[temp_default_code]['barcode']:
#           update odoo's barcode value
            target_product_id  = existing_product_data[temp_default_code]['product_id']
            target_product_barcode =  str(main_data_dict[temp_default_code]['barcode'])
            target_product_data = {'barcode':target_product_barcode}
            pp_obj.write([target_product_id],target_product_data)

if write_to_excel_signal:  
    writer = pd.ExcelWriter(pd_file_path)
    sheet_1.to_excel(writer,sheet_name = 'Sheet1',index = False)
    sheet_2.to_excel(writer,sheet_name = 'Sheet2',index = False)   
    writer.save()
            
print 'PYTHON SCRIPT EXECUTED!'