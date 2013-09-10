# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import time
from datetime import datetime, timedelta
import datetime
from osv import fields, osv
from crm import crm
import tools
import collections
import binascii
import tools
from tools.translate import _
from dateutil.relativedelta import relativedelta

class hr_job(osv.osv):
    '''
    job_code:its unique vaule 
    'month':after how many months again reapply for this job
    '''
    _inherit = "hr.job"
    
    def _check_job_code_unique(self, cr, uid, ids, context=None):
        '''for checking job code unique '''
        lines = self.browse(cr, uid, ids, context=context)
        for l in lines:
            exit_id=self.search(cr,uid,[('job_code','=',l.job_code),('id','!=',l.id)])
            if exit_id:
               raise osv.except_osv(_('Error !'),
                           _('Job Code should be unique!'))
            else:
                return True
       
        return True

    _columns = {
        'job_code': fields.char('Job Code',size=56),
        'month':fields.selection([('01','1'), ('02','2'), ('03','3'), ('04','4'),
                        ('05','5'), ('06','6'), ('07','7'), ('08','8'), ('09','9'),
                        ('10','10'), ('11','11'), ('12','12')], 'Re-apply(months)',required=True), 
    }
    _constraints = [
        (_check_job_code_unique, 'Job Code should be unique!', ['job_code']),
    ]
hr_job()


class hr_applicant(osv.osv):
    '''
    override the message_new for adding job code,state, stage rename the file name 
     '''
    _inherit = 'hr.applicant'
    _columns={
              'imp_pending':fields.boolean('IMP Empoyee'),
              'not_visiblel':fields.char('test',size=56)             
              }
    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """Automatically called when new email message arrives"""
        subject = msg.get('subject') or _("No Subject")
        body = msg.get('body_text')
        msg_from = msg.get('from')
        priority = msg.get('priority')
        msg['attachments']
        for i in range(len(msg['attachments'])):
                l=list(msg['attachments'][i])
                name=msg['attachments'][i][0]+' '+str(time.strftime('%Y-%m-%d %H:%M:%S'))
                l[0]=name
                msg['attachments'][i]=tuple(l)
        cr.execute('SELECT * FROM hr_job')
        ids= map(lambda x: x[0],cr.fetchall())
        rows = self.pool.get('hr.job').browse(cr, uid, ids, context=None)
        k=[]
        for row in rows:
            job_code= row.job_code
            if job_code:
                if subject.find(job_code)>-1:
                   code=subject.find(job_code) 
                   k.append(row)
        cr.execute('SELECT state,stage_id FROM hr_applicant where email_from=%s and not_visiblel=%s ',(msg_from,"TEST"))
        hr_applicant_ids=cr.fetchall()
        stage_id=False
        state='draft'
        if hr_applicant_ids:
            state=hr_applicant_ids[0][0]
            stage_id=hr_applicant_ids[0][1]
        hr_app_ids=self.pool.get('hr.applicant').search(cr,uid,[('email_from','=',msg_from),('state','=','cancel'),('not_visiblel','=','TEST')])
        if hr_app_ids and k:
           hr_app_obj=self.pool.get('hr.applicant').browse(cr,uid,hr_app_ids[0])
           create_date=hr_app_obj.create_date
           c1=create_date.split(' ')
           c_main=c1[0].split('-')
           create_date_last=datetime.datetime(int(c_main[0]),int(c_main[1]),int(c_main[2]), 0, 0, 0,0)
           today = datetime.datetime.today()
           mon=int(k[0].month)
           after_six_months=create_date_last + relativedelta(months=mon)
           if after_six_months<=today:
               vals = {
                'name': subject,
                'email_from': msg_from,
                'email_cc': msg.get('cc'),
                'job_id':k[0].id,
                'state':'draft',
                'description': body,
                'user_id': False,
                'not_visiblel':"TEST",
            }
           else: 
               vals = {
                'name': subject,
                'email_from': msg_from,
                'email_cc': msg.get('cc'),
                'job_id':k[0].id,
                'state':'cancel',
                'description': body,
                'user_id': False,
                'not_visiblel':"TEST",
            }
           if priority:
                vals['priority'] = priority
           vals.update(self.message_partner_by_email(cr, uid, msg.get('from', False)))
           res_id = super(hr_applicant,self).message_new(cr, uid, msg, custom_values=custom_values, context=context)
           self.write(cr, uid, [res_id], vals, context)
           if after_six_months<=today:
               self.write(cr, uid, hr_app_ids, {'state':'draft'}, context)
           return res_id
        elif k and not hr_app_ids:
            vals = {
                'name': subject,
                'email_from': msg_from,
                'email_cc': msg.get('cc'),
                'job_id':k[0].id,
                'state':state,
                'stage_id':stage_id or False,
                'description': body,
                'user_id': False,
                'not_visiblel':"TEST",
            }
            if priority:
                vals['priority'] = priority
            vals.update(self.message_partner_by_email(cr, uid, msg.get('from', False)))
            res_id = super(hr_applicant,self).message_new(cr, uid, msg, custom_values=custom_values, context=context)
            self.write(cr, uid, [res_id], vals, context)
            return res_id
        else:
            vals = {
                'name': subject,
                'email_from': msg_from,
                'email_cc': msg.get('cc'),
                'stage_id':stage_id or False,
                'description': body,
                'user_id': False,
                'not_visiblel':"NOTEST",
            }
            if priority:
                vals['priority'] = priority
            vals.update(self.message_partner_by_email(cr, uid, msg.get('from', False)))
            res_id = super(hr_applicant,self).message_new(cr, uid, msg, custom_values=custom_values, context=context)
            self.write(cr, uid, [res_id], vals, context)
            #print res_id
            return res_id
    

hr_applicant()



