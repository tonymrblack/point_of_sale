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
#    GNU Affero General Public License for more summary.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
import time
from openerp.osv import osv, fields
from openerp import tools

import logging
_logger = logging.getLogger(__name__)


class pos_summary(osv.osv_memory):
    _name = 'pos.summary'
    _description = 'Sales summary'

    _columns = {
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End', required=True),
        'user_ids': fields.many2many('res.users', 'pos_summary_report_user_rel', 'user_id', 'wizard_id', 'Salespeople'),
        'location_ids': fields.many2many('stock.location', 'pos_summary_report_location_rel', 'location_id', 'wizard_id', 'Locations', domain=[('usage', '=', 'internal')]),
        'show_details': fields.boolean('Show Details?', help="Check this box if you want to print details on invoices."),
}
    _defaults = {
        'date_start': fields.date.context_today,
        'date_end': fields.date.context_today,
        'show_details': True,
    }

    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end', 'location_ids','show_details'], context=context)
        res = res and res[0] or {}

        # get timedelta between user timezone and UTC
        utc_time = datetime.now()
        user_time = fields.datetime.context_timestamp(cr, uid, utc_time).replace(tzinfo=None)
        user_timedelta = utc_time - user_time
        res['date_start2'] = (datetime.strptime(res['date_start']+' 00:00:00',tools.DEFAULT_SERVER_DATETIME_FORMAT) + user_timedelta).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        res['date_end2'] = (datetime.strptime(res['date_end']+' 23:59:59',tools.DEFAULT_SERVER_DATETIME_FORMAT) + user_timedelta).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'pos_sales_summary.report_summaryofsales', data=datas, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
