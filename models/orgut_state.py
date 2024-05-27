# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from . import utils

#İller
class OrgutState(models.Model):
    _name = 'orgut.state'
    _description = 'İl Örgütü'
    _inherit = ['mail.thread']

    _sql_constraints = [
        ('unique_state', 'unique(name)', 'Bu il Örgütü zaten mevcut.')
    ]

    name = fields.Many2one('res.country.state', string='State', required=True)
    region = fields.Many2one('orgut.region', string='Region', required=True)
    country = fields.Many2one('res.country', string='Country', default=lambda self: self.env['res.country'].browse(224), required=True)
    member_line_ids = fields.Many2many(
        'res.partner',
        string='Yöneticiler',
        domain=[('id', '!=', 3)],  # Administrator partner ID'sini filtrele
        track_visibility='onchange',
    )

    @api.onchange('country')
    def onchange_country(self):
        for rec in self:
            if not rec.country:
                rec.region = False
            else:
                rec.region = False
                return {'domain': {'region': [('country', '=', rec.country.id)]}}

    @api.onchange('region')
    def onchange_region(self):
        for rec in self:
            if not rec.region:
                rec.name = False
            else:
                rec.name = False
                return {'domain': {'region': [('region', '=', rec.name.id)]}}

    @api.model
    def create(self, vals):
        state = super(OrgutState, self).create(vals)
        state._assign_internal_user_access()
        utils.update_followers(state)
        return state

    def write(self, vals):
        old_members = set(self.member_line_ids.ids)

        result = super(OrgutState, self).write(vals)

        new_members = set(self.member_line_ids.ids)
        removed_members = old_members - new_members
        self._archive_removed_members(removed_members)

        self._assign_internal_user_access()

        utils.update_followers(self, old_members, new_members)

        return result

    def _assign_internal_user_access(self):
        internal_user_group = self.env.ref('base.group_user')
        orgut_il_sorumlusu_group = self.env.ref('orgut_yonetimi.orgut_il_sorumlusu')
        orgut_ilce_sorumlusu_group = self.env.ref('orgut_yonetimi.orgut_ilce_sorumlusu')
        group_partner_manager_group = self.env.ref('base.group_partner_manager')

        for partner in self.member_line_ids:
            existing_user = self.env['res.users'].with_context(active_test=False).search([('partner_id', '=', partner.id)], limit=1)
            if existing_user:
                # Kullanıcı varsa, yeniden etkinleştir ve gerekli grupları ekle
                if not existing_user.active:
                    existing_user.active = True
                    # Parola sıfırlama talimatı gönder
                    existing_user.action_reset_password()
                groups_to_add = []
                if not existing_user.has_group('base.group_user'):
                    groups_to_add.append(internal_user_group.id)
                if not existing_user.has_group('orgut_yonetimi.orgut_il_sorumlusu'):
                    groups_to_add.append(orgut_il_sorumlusu_group.id)
                if not existing_user.has_group('orgut_yonetimi.orgut_ilce_sorumlusu'):
                    groups_to_add.append(orgut_ilce_sorumlusu_group.id)
                if not existing_user.has_group('base.group_partner_manager'):
                    groups_to_add.append(group_partner_manager_group.id)
                if groups_to_add:
                    existing_user.write({'groups_id': [(4, group_id) for group_id in groups_to_add]})
            else:
                # Kullanıcı yoksa, yeni kullanıcı oluştur ve gerekli grupları ekle
                user_vals = {
                    'name': partner.name,
                    'login': partner.email,
                    'partner_id': partner.id,
                    'groups_id': [(6, 0, [
                        internal_user_group.id,
                        orgut_il_sorumlusu_group.id,
                        orgut_ilce_sorumlusu_group.id,
                        group_partner_manager_group.id
                    ])]
                }
                self.env['res.users'].sudo().create(user_vals)

    def _archive_removed_members(self, removed_member_ids):
        if removed_member_ids:
            removed_partners = self.env['res.partner'].browse(removed_member_ids)
            for partner in removed_partners:
                if partner.user_ids:
                    user = partner.user_ids[0]
                    user.active = False
                    groups_to_remove = [
                        self.env.ref('base.group_user'),
                        self.env.ref('orgut_yonetimi.orgut_il_sorumlusu'),
                        self.env.ref('orgut_yonetimi.orgut_ilce_sorumlusu'),
                        self.env.ref('base.group_partner_manager')
                    ]
                    user.write({'groups_id': [(3, group.id) for group in groups_to_remove]})

    @api.constrains('name')
    def _check_unique_state(self):
        for record in self:
            existing_state = self.search(
                [('name', '=', record.name.id), ('id', '!=', record.id)], limit=1)
            if existing_state:
                raise exceptions.ValidationError('Bu il örgütü zaten mevcut')