# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "HR Management",
    "version": "1.1",
    "author": "Saraswathi",
    "category": "Hr",
    "sequence": 12,
    'complexity': "easy",
    "website": "http://www.ktree.com",
    "description": """
    """,
    'author': 'SARASWATHI',
    'website': 'http://www.Ktree.com',
    'images': [],
    'depends': ['base','hr','hr_recruitment','hr_holidays','mail','hr_attendance','hr_timesheet',],
    'init_xml': [],
    'update_xml': ['ktree_hr_view.xml','hr_employee_view.xml'],
    'demo_xml': [
       
    ],
    'test': [
             
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
#    'certificate': '0086710558965',
#    "css": [ 'static/src/css/hr.css' ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
