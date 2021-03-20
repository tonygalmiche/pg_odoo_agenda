# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


# class Meeting(models.Model):
#     _inherit = 'calendar.event'


#     def _compute_is_je_participe(self):
#         for obj in self:
#             test=False
#             if self.env.user.partner_id in obj.partner_ids:
#                 test=True
#             obj.is_je_participe=test
#     is_je_participe = fields.Boolean('Je participe', compute='_compute_is_je_participe')




# class Meeting(models.Model):
#     _inherit = 'calendar.event'
 
#     @api.model_create_multi
#     def create(self, vals_list):
#         ## Bug création en double des repetitions sur la premiere journée ******
#         if vals_list:
#             v=vals_list[0]
#             user_id=v.get("user_id")
#             if user_id:
#                 print('user_id=',user_id,vals_list)
#                 start=v.get("start")
#                 events = self.env['calendar.event'].search([('user_id', '=', user_id),('start', '=', start)], limit=1)
#                 if events:
#                     return events
#         #***********************************************************************

#         res=super().create(vals_list)
#         return res
