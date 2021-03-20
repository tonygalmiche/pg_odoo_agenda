# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'


    @api.depends('partner_id')
    def _compute_is_user_id(self):
        for obj in self:
            print(obj,obj.partner_id)
            user_id=False
            if obj.partner_id:
                users = self.env['res.users'].search([
                    ('partner_id', '=', obj.partner_id.id),
                ])
                if users:
                    user_id=users[0].id
                print(users,user_id)
            obj.is_user_id=user_id


    is_user_id = fields.Many2one('res.users', 'Utilisateur', compute='_compute_is_user_id', store=True, readonly=True, index=True)




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
