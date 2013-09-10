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

import ast
import re
import datetime
from itertools import groupby
from operator import itemgetter
import math
import tools
from osv import osv
from osv import fields
from tools.safe_eval import safe_eval as eval
from tools.translate import _
import time
import netsvc

# main mako-like expression pattern
EXPRESSION_PATTERN = re.compile('(\$\{.+?\})')

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('name','=',name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None,context=None, count=False):
        ids = []
        group ='HR Manager'
        cur_group_id=self.pool.get('res.groups').search(cr,uid,[('name','=',group)])
        group_ids = self.pool.get('res.users').browse(cr,uid,uid).groups_id
        test = False
        list=[]
        for  group_id in group_ids:
             list.append(group_id.id)
        if cur_group_id and self.pool.get('res.users').browse(cr,uid,cur_group_id[0]).id in list: #adedd aug30
            test = True
        if uid != 1 and test == True:
            return  super(hr_employee, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order,context=context, count=count)
        elif uid != 1:
            args=[]
            args=[('user_id', '=', uid)] 
            res =  super(hr_employee, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order,context=context, count=count)
        else:
            res =  super(hr_employee, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order,context=context, count=count)
        return res
    
    _columns = {
                'date_of_join':fields.date('Date of Joining'),
                'get_email':fields.boolean('Receive Emails',help='Receive Emails When any employee apply for Leaves'),
                'week_off_on_sat':fields.boolean('Allow Saturday Weekoff'),
                'emp_id':fields.char('Emp ID',size=100),
                'current_address_id':fields.many2one('res.partner',"Current Address") , # comented to install it
                'primary_cname':fields.char("contact Name",size=56),
                'primary_cnumbre':fields.char("contact Numbrer",size=56),
                'primary_crelation':fields.char("Relation",size=56),
                'secondar_sname':fields.char("Contact Name",size=56),
                'secondar_snumber':fields.char("Contact Number",size=56),
                'secondar_srelation':fields.char("Relation",size=56),
                'allocated':fields.boolean('Allocated'),
                'ishr':fields.boolean('Is Hr'),
                }
    
    def allocate_leaves(self, cr, uid, ids, context=None):
        ''' This method will return the allocated leaves to the every employee '''
        emp_obj = self.browse(cr,uid,ids)
        obj_emp = self.pool.get('hr.employee')
        status_ids=self.pool.get('hr.holidays.status').search(cr,uid,[('active','=',True)])
        status_objs=self.pool.get('hr.holidays.status').browse(cr,uid,status_ids)
        leave_ids=[]
        for record in status_objs:
            #print record
            vals = {
                    'name': record.name,
                    'type': 'add',
                    'holiday_type': 'employee',
                    'holiday_status_id': record.id,
                    'number_of_days_temp': record.alloc_leaves,
                    'employee_id': emp_obj[0].id,
                    'year':record.year.id
             }
            leave_ids.append(self.pool.get('hr.holidays').create(cr, uid, vals, context=None))
            wf_service = netsvc.LocalService("workflow")
            for leave_id in leave_ids:
                #print leave_id
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        self.write(cr,uid,ids,{'allocated':True})
        return True  
    
    
    
    def allocat_leaves(self, cr, uid, context=None):
        self.pool.get('hr.holidays.status').search(cr,uid,[('active','=',True)])
        for record in status_objs:
            #print record
            for emp in obj_emp.browse(cr, uid, emp_ids):
                vals = {
                    'name': record.name,
                    'type': 'add',
                    'holiday_type': 'employee',
                    'holiday_status_id': record.id,
                    'number_of_days_temp': record.alloc_leaves,
                    'employee_id': emp.id,
                }
                leave_ids.append(self.pool.get('hr.holidays').create(cr, uid, vals, context=None))
            wf_service = netsvc.LocalService("workflow")
            for leave_id in leave_ids:
                #print leave_id
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        self.write(cr,uid,ids,{'test':True})
        
        
        return True
    
    
    
hr_employee()

class hr_holidays_status(osv.osv):
    """To inherite hr holyday status"""
    _inherit = "hr.holidays.status"
    
    def get_carry_leaves(self, cr, uid, context=None):
        dic={}
        for i ,j in enumerate(range(10,110,10)):
            dic[str(j)]=j
        return dic.items()
    
    def create(self, cr, uid, data, context=None):
        #print context,data
        if data.has_key('line_id'):
            leave_obj = self.pool.get('leave.year').browse(cr,uid,data['line_id'])
            data['name'] = data['name']+' / '+leave_obj.year.name
            data['year'] = leave_obj.year.id
            if data['lop'] == True:
               data['no_rules']=True 
        return super(hr_holidays_status, self).create(cr, uid, data, context)
    
    _columns = {
                 'no_rules' : fields.boolean('No Rules'),
                 'carry_forward_to_nextyear' : fields.boolean('Carry Forward To Next Year'),
                 'carry_forwarded' : fields.boolean('Is Carry Forward'),
                 'carry_fo_leaves':fields.selection(get_carry_leaves,'Carry Forward(%)',size=16),
                 'alloc_leaves'        :fields.float("No Of Leaves"),
                 'year'        :fields.many2one('account.fiscalyear','Year'),  
                 'line_id': fields.many2one('leave.year', 'Leave Lines'), 
                 'lop' : fields.boolean('Is LOP'), 
                 }
    
    def get_days(self, cr, uid, ids, employee_id, return_false, context=None):
        """To get the leaves summurry of an employee"""
        cr.execute("""SELECT id, type, number_of_days, holiday_status_id FROM hr_holidays WHERE employee_id = %s AND state='validate' AND holiday_status_id in %s""",
            [employee_id, tuple(ids)])
        result = sorted(cr.dictfetchall(), key=lambda x: x['holiday_status_id'])
        grouped_lines = dict((k, [v for v in itr]) for k, itr in groupby(result, itemgetter('holiday_status_id')))
        ###########if employee applied has any lops ##############
        lop=0
        if grouped_lines:
            emp_id=self.pool.get('hr.holidays').search(cr,uid,[('employee_id','=',employee_id),('state','=','validate'),('holiday_status_id','=',grouped_lines.keys()[0])])
            for id in emp_id:
                obj=self.pool.get('hr.holidays').browse(cr,uid,id)
                if (obj.lop==True) and (obj.for_lop==True):
                    lop+=obj.number_of_days_temp
        #####################################################
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = {}
            max_leaves = leaves_taken = 0
            if not return_false:
                if record.id in grouped_lines:
                    leaves_taken = -sum([item['number_of_days'] for item in grouped_lines[record.id] if item['type'] == 'remove'])
                    max_leaves = sum([item['number_of_days'] for item in grouped_lines[record.id] if item['type'] == 'add'])
            res[record.id]['max_leaves'] = max_leaves
            res[record.id]['remaining_leaves'] = max_leaves - leaves_taken
            leaves_taken =leaves_taken-lop        #removing lop from total no.of leaves tacken
            res[record.id]['leaves_taken'] = leaves_taken
            if leaves_taken>=0:
              res[record.id]['remaining_leaves'] = max_leaves - leaves_taken
        return res
hr_holidays_status()    
 
class leave_year(osv.osv):
    _name = 'leave.year'
    
    def create(self, cr, uid, data, context=None):
        if data['year']:
           cur_id = self.search(cr,uid,[('year','=',data['year'])])
           if cur_id:
               raise osv.except_osv(_('Warning!'),_('You cannot create again same record ') )
        return super(leave_year, self).create(cr, uid, data, context)
    _columns = {
         'name'        :fields.char('Name',size=56),
         'year'        :fields.many2one('account.fiscalyear','Year'), 
         'order_line'  : fields.one2many('hr.holidays.status', 'line_id', 'Leave Lines'),  
         'test'        :fields.boolean('Test')
}
    def allocate_leaves(self, cr, uid, ids, context=None):
        ''' This method will return the allocated leaves to the every employee '''
        curr_obj = self.browse(cr,uid,ids)
        obj_emp = self.pool.get('hr.employee')
        emp_ids = obj_emp.search(cr, uid, [])
        leave_ids = []
        status_objs=self.browse(cr,uid,ids)[0].order_line
        for record in status_objs:
            for emp in obj_emp.browse(cr, uid, emp_ids):
                vals = {
                    'name': record.name,
                    'type': 'add',
                    'holiday_type': 'employee',
                    'holiday_status_id': record.id,
                    'number_of_days_temp': record.alloc_leaves,
                    'employee_id': emp.id,
                }
                leave_ids.append(self.pool.get('hr.holidays').create(cr, uid, vals, context=None))
            wf_service = netsvc.LocalService("workflow")
            for leave_id in leave_ids:
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        self.write(cr,uid,ids,{'test':True})
        return True  
leave_year()


class carry_forwarded(osv.osv):
    _name = 'carry.forwarded'
    
    def create(self, cr, uid, data, context=None):
        if data['from_year'] and data['to_year']:
           cur_id = self.search(cr,uid,[('from_year','=',data['from_year']),('to_year','=',data['to_year'])])
           if cur_id:
               raise osv.except_osv(_('Warning!'),_('You cannot create again same record ') )
        return super(carry_forwarded, self).create(cr, uid, data, context)

    _columns ={
               'from_year':fields.many2one('account.fiscalyear','From Year'),
                'to_year'        :fields.many2one('account.fiscalyear','To Year'),
                'test'           :fields.boolean('Test'),
               }
    
    def carry_forward_leaves(self, cr, uid, ids, context=None):
        ''' This method will return the carry forwarded allocated leaves to the every employee '''
        curr_obj = self.browse(cr,uid,ids)
        from_year = curr_obj[0].from_year
        to_year = curr_obj[0].to_year
        obj_emp = self.pool.get('hr.employee')
        emp_ids = obj_emp.search(cr, uid, [])
        leave_ids = []
        status_ids=self.pool.get('hr.holidays.status').search(cr,uid,[('year','=',from_year.id),('carry_forwarded','=',True)])
        status_objs=self.pool.get('hr.holidays.status').browse(cr,uid,status_ids)
        for record in status_objs:
            perce_carryleaves=int(record.carry_fo_leaves)
            create_status_id = self.pool.get('hr.holidays.status').create(cr,uid,{'name':str(record.name),'color_name': 'red', 'no_rules':True,'year':to_year.id})
            for emp in obj_emp.browse(cr, uid, emp_ids):
                leaves_rest = self.pool.get('hr.holidays.status').get_days( cr, uid, [record.id], emp.id, False)[record.id]['remaining_leaves']
                if int((leaves_rest)*(float(record.carry_fo_leaves)/100))>0:
                    vals = {
                        'name': record.name,
                        'type': 'add',
                        'holiday_type': 'employee',
                        'holiday_status_id': create_status_id,
                        'number_of_days_temp': int((leaves_rest)*(float(record.carry_fo_leaves)/100)),
                        'employee_id': emp.id,
                    }
                    leave_ids.append(self.pool.get('hr.holidays').create(cr, uid, vals, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    #print leave_id
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        self.write(cr,uid,ids,{'test':True})
        before_year_status_ids = self.pool.get('hr.holidays.status').search(cr,uid,[('year','!=',to_year.id)])
        k = self.pool.get('hr.holidays.status').search(cr,uid,[('year','=',False)])
        if before_year_status_ids and k:
            before_year_status_ids = before_year_status_ids+k
        self.pool.get('hr.holidays.status').write(cr,uid,before_year_status_ids,{'active':False})
        return True
carry_forwarded()   

 
class hr_holidays(osv.osv):
    """
    Inherit the hr.holidays object to override a function
    """
    _inherit = "hr.holidays"
    
    def get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False 
    _columns = {
                'lop':fields.boolean('Make LOP'),###########To apply lop
                'for_lop':fields.boolean('To Approve'),#########when leave is lop
                'create_date': fields.datetime('Creation Date', readonly=True, help="Date on which Invoice is created."),
                'holiday_type': fields.selection([('employee','By Employee'),('category','By Employee Category')], 'Allocation Type', help='By Employee: Allocation/Request for individual Employee, By Employee Category: Allocation/Request for group of employees in category', required=True,invisible=True),
                'employee_id': fields.many2one('hr.employee', "Employee", select=True, invisible=False, readonly=True, states={'draft':[('readonly',False)]}, help='Leave Manager can let this field empty if this leave request/allocation is for every employee'),
                'year'        :fields.many2one('account.fiscalyear','Year'), 
                }
    
    _defaults = {
              'year':get_fiscalyear,
              } 
      
    def onchange_date_from(self, cr, uid, ids, date_to, date_from,employee_id,holiday_status_id):
        """inherited to pass employee_id as perameter"""
        result = {}
        if date_to and date_from:
            diff_day = self._get_number_of_days(date_from, date_to,cr,uid,employee_id,holiday_status_id)
            result['value'] = {
                'number_of_days_temp': round(diff_day)+1
            }
            return result
        result['value'] = {
            'number_of_days_temp': 0,
        }
        return result
    
    def _get_number_of_days(self, date_from, date_to,cr,uid,employee_id,holiday_status_id):
        """Returns a float equals to the timedelta between two dates given as string.
        inherited for removing weekend days from leave requests"""
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        emp_obj=self.pool.get('hr.employee').browse(cr,uid,employee_id)
        public_holi_id=self.pool.get('public.holidays').search(cr,uid,[('date','>=',date_from),('date','<=',date_to)])
        day=0.0
        ############# if emp is allowed for saturday,sunday off#############3
        if holiday_status_id:         #added holiday_status_id
            status_obj=self.pool.get('hr.holidays.status').browse(cr,uid,holiday_status_id)
            
            if status_obj.lop == True:
                pass
            else:
            
                if emp_obj.week_off_on_sat:
                    from datetime import timedelta
                    while to_dt is None or from_dt <= to_dt:
                      if (from_dt.weekday()==5) or (from_dt.weekday()==6):
                          day+=1
                      from_dt+=timedelta(days = 1)
                else:  
                    ############# if emp is allowed for saturday woking and sunday off#############3   
                   from datetime import timedelta
                   while to_dt is None or from_dt <= to_dt:
                      if (from_dt.weekday()==6):
                          day+=1
                      from_dt+=timedelta(days = 1)
                if public_holi_id:
                   pub_holi_obj=self.pool.get('public.holidays').browse(cr,uid,public_holi_id[0])
                   pub_day = datetime.datetime.strptime(pub_holi_obj.date+' '+"00:00:00", DATETIME_FORMAT)
                   if emp_obj.week_off_on_sat:
                      if (from_dt.weekday() != 5) or (from_dt.weekday() != 6):
                          day+=1 
                   elif pub_day.weekday() != 5 and pub_day.weekday() != 6:
                          day += 1
                   from_dt += timedelta(days = 1) 
                if day:
                    diff_day=diff_day-day    
            return diff_day
        else: 
            return diff_day
    
    def lop_validate(self, cr, uid, ids, context=None):
        """To call when lop is to approve"""
        s=self.holidays_validate(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        return self.write(cr, uid, ids, {'state':'validate', 'manager_id': manager})
    
    def is_leap_year(self,cr,uid,ids,year):
        """TO check current year leap year or not"""
        if year % 400 == 0:
            return 366
        elif year % 100 == 0:
            return 365
        elif year % 4 == 0:
            return 366
        else:
            return 365
          
    def lengthmonth(self,cr, uid, ids,year, month):
      """TO calculate no.of days from jan to applyed month"""
      if ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
          feb=29
      else:    
          feb=28
      return [0, 31, feb+31, 31+feb+31, 30+31+feb+31, 31+30+31+feb+31, 30+31+30+31+feb+31, 31+30+31+30+31+feb+31, 31+31+30+31+30+31+feb+31, 30+31+31+30+31+30+31+feb+31, 31+30+31+31+30+31+30+31+feb+31, 30+31+30+31+31+30+31+30+31+feb+31, 31+30+31+30+31+31+30+31+30+31+feb+31][month]

    
    def check_holidays(self, cr, uid, ids,context=None):
        """Override Function, which is to restrict number of leavse for month """
        parent_email=[]
        cr.execute('select work_email from hr_employee  where get_email=True')
        res = cr.dictfetchall()
        if res:
            parent_email=[k.values()[0] for k in res]

        holi_status_obj = self.pool.get('hr.holidays.status')
        for record in self.browse(cr, uid, ids):
            if record.holiday_type == 'employee' and record.type == 'remove' and not record.lop:
                if record.employee_id.date_of_join and  record.employee_id.date_of_join > record.date_from:
                        raise osv.except_osv(_('Warning!'),_('You are not eligible for leaves.') )
                if record.employee_id and not record.holiday_status_id.limit :
                    leaves_rest = holi_status_obj.get_days( cr, uid, [record.holiday_status_id.id], record.employee_id.id, False)[record.holiday_status_id.id]['remaining_leaves']
                    max_leaves  = holi_status_obj.get_days( cr, uid, [record.holiday_status_id.id], record.employee_id.id, False)[record.holiday_status_id.id]['max_leaves']
                   ####################Leave type has NO Rules################33
                    if record.holiday_status_id.no_rules:
                        if leaves_rest >= record.number_of_days_temp:
                            dest=[]
                            if record.employee_id.parent_id:
                                    dest.append(record.employee_id.parent_id.work_email)
                            dest.append(record.employee_id.work_email)
                            body="\n \n \bHi  \n \n \b\b Employee : "+record.employee_id.name+"\n\n \b\b Leave type : "+record.holiday_status_id.name+"\n\n \b\b Reason : \n\n \b\b Number of days : From "+str(record.date_from[0:10])+" To "+str(record.date_to[0:10])+" i.e for "+str(int(record.number_of_days_temp))+" days."+"\n\n  Please don't treat this email as approval , Get your Supevisor's approval before going for the leave"
                            mail_message = self.pool.get('mail.message')
                            mail_server = self.pool.get('ir.mail_server').search(cr,uid,[])
                            mail_obj=self.pool.get('ir.mail_server').browse(cr,uid,mail_server[0])
                            src = mail_obj.smtp_user
                            sub=record.name
                            if dest and (record.state == 'draft'):
                              msg_id=mail_message.schedule_with_attach(cr, uid, src, dest, sub, body,email_cc=parent_email, context=context)
                              mail_message.send(cr, uid, [msg_id], context=context) 
                            if dest and (record.state == 'confirm'):
                              manager_name=""
                              if  record.employee_id.parent_id.user_id.id == uid:
                                   manager_name=str(record.employee_id.parent_id.name)
                              elif uid == 1:
                                   manager_name=str(record.employee_id.parent_id.name)
                              else:
                                 raise osv.except_osv(_('Warning!'),_('Manager should approve the leave') ) 
                              notes=""
                              if record.notes:
                                  notes=str(record.notes)
                              
                              
                              body="\n \n \bHi  \n \n \b\b Employee : "+record.employee_id.name+"\n\n \b\b Leave type : "+record.holiday_status_id.name+"\n\n \b\b Reason : "+notes+"\n\n \b\b Number of days : From "+str(record.date_from[0:10])+" To "+str(record.date_to[0:10])+" i.e for "+str(int(record.number_of_days_temp))+" days."+"\n\n \b\b You are hereby notified that the above leave applied by you are now approved by your supervisor "+str(manager_name)+" Thanks"
                              msg_id=mail_message.schedule_with_attach(cr, uid, src, dest, sub, body,email_cc=parent_email, context=context)
                              mail_message.send(cr, uid, [msg_id], context=context) 
                            return True
                        elif record.holiday_status_id.carry_forwarded:
                            if leaves_rest >= record.number_of_days_temp:
                                dest=[]
                                if record.employee_id.parent_id:
                                        dest.append(record.employee_id.parent_id.work_email)
                                body="\n \n \bHi  \n \n \b\b Employee : "+record.employee_id.name+"\n\n \b\b Leave type : "+record.holiday_status_id.name+"\n\n \b\b Reason : \n\n \b\b Number of days : From "+str(record.date_from[0:10])+" To "+str(record.date_to[0:10])+" i.e for "+str(int(record.number_of_days_temp))+" days."+"\n\n  Please don't treat this email as approval , Get your Supevisor's approval before going for the leave"
                                mail_message = self.pool.get('mail.message')
                                mail_server = self.pool.get('ir.mail_server').search(cr,uid,[])
                                mail_obj=self.pool.get('ir.mail_server').browse(cr,uid,mail_server[0])
                                src = mail_obj.smtp_user
                                sub=record.name
                                if dest and (record.state=='draft'):
                                  msg_id=mail_message.schedule_with_attach(cr, uid, src, dest, sub, body,email_cc=parent_email, context=context)
                                  mail_message.send(cr, uid, [msg_id], context=context) 
                                return True
                        else:
                            raise osv.except_osv(_('Warning!'),_('You cannot take leaves because few remaining days (%s).') % (leaves_rest))
                    ###################################3    
                    year=record.date_to[0:4]
                    month=record.date_to[5:7]
                    no_of_days_in_year=self.is_leap_year(cr, uid, ids,int(year))
                    no_of_days_in_month=self.lengthmonth(cr, uid, ids,int(year),int(month))
                    ############### when employee join in middle of the year #################
                    now = datetime.datetime.now()
                    if (now.year==int(record.employee_id.date_of_join and record.employee_id.date_of_join[0:4])):
                        join=record.employee_id.date_of_join
                        if join:
                            tacken_leaves=holi_status_obj.get_days( cr, uid, [record.holiday_status_id.id], record.employee_id.id, False)[record.holiday_status_id.id]['leaves_taken']
                            if join > record.date_to:
                                raise osv.except_osv(_('Warning!'),_('You are not eligible for leaves.') )
                            monthdays=self.lengthmonth(cr, uid, ids,int(join[0:4]),int(join[5:7]))
                            days=no_of_days_in_year
                            no_of_days_in_month=no_of_days_in_month-monthdays
                            no_of_days_in_year=no_of_days_in_year-monthdays
                            leaves=math.ceil(((no_of_days_in_year*max_leaves)/days))
                            ml=leaves-tacken_leaves
                            if ml<record.number_of_days_temp:
                                   raise osv.except_osv(_('Warning!'),_('You cannot take leaves because few remaining days (%s).') % (leaves-tacken_leaves))
                    #######################################   
                    new_codition=((max_leaves/no_of_days_in_year)*no_of_days_in_month)-(max_leaves-leaves_rest)
                    if leaves_rest < record.number_of_days_temp:
                        raise osv.except_osv(_('Warning!'),_('You cannot take leaves because few remaining days (%s).') % (leaves_rest))
                    elif float(new_codition) < .5:
                        raise osv.except_osv(_('Warning!'),_('You are  not eligible for %s leave for this month') % (record.holiday_status_id.name)) 
                    elif record.number_of_days_temp>round(new_codition):
                        raise osv.except_osv(_('Warning!'),_('You are eligible for %s only %s number of days for this month') % (record.holiday_status_id.name,round(new_codition)))   
            ###########when emp has no leaves and it is taken as lop and mail send to that emp###########
            #print record.state,"record.state-------------"
            if record.state=='draft' and record.type=='remove':
                        """TO Send email only when the applicant press confirm button """
                        mail_message = self.pool.get('mail.message')
                        mail_server = self.pool.get('ir.mail_server').search(cr,uid,[])
                        mail_obj=self.pool.get('ir.mail_server').browse(cr,uid,mail_server[0])
                        src = mail_obj.smtp_user
                        name = record.employee_id.name
                        dest=[]
                        if record.employee_id.work_email:
                                    dest.append(record.employee_id.work_email)
                                    dest.append(record.employee_id.parent_id.work_email)
                        sub=record.name
                        if record.employee_id :
                            if record.employee_id.parent_id:
                                dest.append(record.employee_id.parent_id.work_email)
                                dest.append(record.employee_id.work_email)
                            if  record.notes:
                                 body="\n \n \bHi  \n \n \b\b Employee : "+record.employee_id.name+"\n\n \b\b Leave type : "+record.holiday_status_id.name+"\n\n \b\b Reason : "+(record.notes and record.notes)+"\n\n \b\b Number of days : From "+str(record.date_from[0:10])+" To "+str(record.date_to[0:10])+" i.e for "+str(int(record.number_of_days_temp))+" days."+"\n\n  Please don't treat this email as approval , Get your Supevisor's approval before going for the leave"
                            else :
                                 body="\n \n \bHi  \n \n \b\b Employee : "+record.employee_id.name+"\n\n \b\b Leave type : "+record.holiday_status_id.name+"\n\n \b\b Reason : \n\n \b\b Number of days : From "+str(record.date_from[0:10])+" To "+str(record.date_to[0:10])+" i.e for "+str(int(record.number_of_days_temp))+" days."+"\n\n  Please don't treat this email as approval , Get your Supevisor's approval before going for the leave"
                        #print dest,parent_email,'parent_email---'
#                            print task
                        if dest or parent_email:
                            
                         msg_id=mail_message.schedule_with_attach(cr, uid, src, dest, sub, body,email_cc=parent_email, context=context)
                         mail_message.send(cr, uid, [msg_id], context=context) 
            elif record.state == 'confirm' and record.type == 'remove':
                  mail_message = self.pool.get('mail.message')
                  mail_server = self.pool.get('ir.mail_server').search(cr,uid,[])
                  mail_obj=self.pool.get('ir.mail_server').browse(cr,uid,mail_server[0])
                  src = mail_obj.smtp_user
                  parent_email=[]
                  cr.execute('select work_email from hr_employee  where get_email=True')
                  res = cr.dictfetchall()
                  if res:
                        parent_email=[k.values()[0] for k in res] 
                  sub=record.name
                  dest=[]
                  if record.employee_id.parent_id and record.employee_id.parent_id.work_email:
                    parent_email.append(record.employee_id.parent_id.work_email)
                    
                  if record.employee_id.work_email:
                    dest=[record.employee_id.work_email] 
                  if parent_email or dest:
                    manager_name=""
                    if  record.employee_id.parent_id.user_id.id == uid :
                           manager_name=str(record.employee_id.parent_id.name)
                    elif uid == 1:
                         manager_name = str(record.employee_id.parent_id.name)
                    else:
                        raise osv.except_osv(_('Warning!'),_('Manager should approve the leave') ) 
                    notes=""
                    if record.notes:
                        notes=str(record.notes)
                    body="\n \n \bHi  \n \n \b\b Employee : "+record.employee_id.name+"\n\n \b\b Leave type : "+record.holiday_status_id.name+"\n\n \b\b Reason : "+notes+"\n\n \b\b Number of days : From "+str(record.date_from[0:10])+" To "+str(record.date_to[0:10])+" i.e for "+str(int(record.number_of_days_temp))+" days."+"\n\n \b\b You are hereby notified that the above leave applied by you are now approved by your supervisor "+str(manager_name)+" Thanks"
                    
                    msg_id=mail_message.schedule_with_attach(cr, uid, src, dest, sub, body,email_cc=parent_email, context=context)
                    mail_message.send(cr, uid, [msg_id], context=context)
                
        return True

    def holidays_refuse(self, cr, uid, ids, approval, context=None):
        ''' override the function for sending email to hr and administrator while refuse the request''' 
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        mail_message = self.pool.get('mail.message')
        mail_server = self.pool.get('ir.mail_server').search(cr,uid,[])
        mail_obj=self.pool.get('ir.mail_server').browse(cr,uid,mail_server[0])
        src = mail_obj.smtp_user
        if approval == 'first_approval':
            self.write(cr, uid, ids, {'state': 'refuse', 'manager_id': manager})
        else:
            self.write(cr, uid, ids, {'state': 'refuse', 'manager_id2': manager})
        self.holidays_cancel(cr, uid, ids, context=context)
        ########### Here i added the code for sending mail##############
        for rec in self.browse(cr, uid, ids, context=context):
            user_obj=self.pool.get('res.users').browse(cr,uid,uid)
            user_name=user_obj.name
            parent_email=[]
            if user_obj.user_email:
               parent_email.append(user_obj.user_email)
            emp_hr_ids=self.pool.get('hr.employee').search(cr,uid,[('ishr','=',True)])
            dest=[]
            for hr in emp_hr_ids:
                emp_obj=self.pool.get('hr.employee').browse(cr,uid,hr)
                if emp_obj.work_email:
                   dest.append(emp_obj.work_email)
            sub=rec.name
            notes=""
            if rec.notes:
               notes=str(rec.notes)
            sub=rec.name
            notes=""
            if rec.notes:
               notes=str(rec.notes)
            body="\n \n \bHi  \n \n \b\b Employee : "+rec.employee_id.name+"\n\n \b\b Leave type : "+rec.holiday_status_id.name+"\n\n \b\b Reason : "+notes+"\n\n \b\b Number of days : From "+str(rec.date_from[0:10])+" To "+str(rec.date_to[0:10])+" i.e for "+str(int(rec.number_of_days_temp))+" days."+"\n\n \b\b This Leave Request has been refused "+"  By "+str(user_name)+" Thanks"
            msg_id=mail_message.schedule_with_attach(cr, uid, src, dest, sub, body,email_cc=parent_email, context=context)
            mail_message.send(cr, uid, [msg_id], context=context)
        return True
    
    
    def unlink(self, cr, uid, ids, context=None):
        ''' override the function for sending email to hr and administrator while deleting  the request''' 
        mail_message = self.pool.get('mail.message')
        mail_server = self.pool.get('ir.mail_server').search(cr,uid,[])
        mail_obj=self.pool.get('ir.mail_server').browse(cr,uid,mail_server[0])
        src = mail_obj.smtp_user
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state<>'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete a leave which is not in draft state !'))
            else:
                parent_email=[]
                user_obj=self.pool.get('res.users').browse(cr,uid,uid)
                user_name=user_obj.name
                if user_obj.user_email:
                   parent_email.append(user_obj.user_email)
                emp_hr_ids=self.pool.get('hr.employee').search(cr,uid,[('ishr','=',True)])
                dest=[]
                for hr in emp_hr_ids:
                    emp_obj=self.pool.get('hr.employee').browse(cr,uid,hr)
                    if emp_obj.work_email:
                       dest.append(emp_obj.work_email)
                sub=rec.name
                notes=""
                if rec.notes:
                   notes=str(rec.notes)
                body="\n \n \bHi  \n \n \b\b Employee : "+rec.employee_id.name+"\n\n \b\b Leave type : "+rec.holiday_status_id.name+"\n\n \b\b Reason : "+notes+"\n\n \b\b Number of days :  "+str(int(rec.number_of_days_temp))+" days."+"\n\n \b\b This Leave Request has been deleted "+"  By "+str(user_name)+" Thanks"
                msg_id=mail_message.schedule_with_attach(cr, uid, src, dest, sub, body,email_cc=parent_email, context=context)
                mail_message.send(cr, uid, [msg_id], context=context)
        return super(hr_holidays, self).unlink(cr, uid, ids, context)
   

hr_holidays()  


class public_holidays(osv.osv):
    _name = 'public.holidays'
    
    _columns = {
                'name':fields.char('Holiday',size=56),
                'date':fields.date('Date'),
                'year':fields.many2one('account.fiscalyear','Year')
                }
public_holidays()

    
