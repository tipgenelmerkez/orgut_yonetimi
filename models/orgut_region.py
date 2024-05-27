from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from . import utils

class OrgutRegion(models.Model):
    _name = 'orgut.region'
    _description = 'Bölge Örgütü'
    _inherit = ['mail.thread']

    _sql_constraints = [
        ('unique_region_country', 'unique(name, country)', 'Bu bölge örgütü zaten mevcut.')
    ]

    name = fields.Char(string='Region', required=True)
    country = fields.Many2one('res.country', string='Country', default=lambda self: self.env['res.country'].browse(224), required=True)
    member_line_ids = fields.Many2many(
        'res.partner',
        string='Yöneticiler',
        domain=[('id', '!=', 3)],  # Administrator partner ID'sini filtrele
        track_visibility='onchange',
    )

    @api.model
    def create(self, vals):
        region = super(OrgutRegion, self).create(vals)
        region._assign_internal_user_access()
        utils.update_followers(region)
        return region

    def write(self, vals):
        # Önceki üyeleri almak için mevcut kaydı yükleyelim
        old_members = set(self.member_line_ids.ids)
        result = super(OrgutRegion, self).write(vals)

        # Güncellenmiş üyeleri almak için kaydı tekrar yükleyelim
        new_members = set(self.member_line_ids.ids)

        # Kaldırılan üyeleri bulalım
        removed_members = old_members - new_members

        # Kaldırılan üyeleri arşivle
        self._archive_removed_members(removed_members)

        # Yeni ve mevcut üyeleri işlemek için iç kullanıcı erişimi ver
        self._assign_internal_user_access()

        # Followers güncelle
        utils.update_followers(self, old_members, new_members)

        return result

    def _assign_internal_user_access(self):
        internal_user_group = self.env.ref('base.group_user')
        orgut_bolge_sorumlusu_group = self.env.ref('orgut_yonetimi.orgut_bolge_sorumlusu')
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
                if not existing_user.has_group('orgut_yonetimi.orgut_bolge_sorumlusu'):
                    groups_to_add.append(orgut_bolge_sorumlusu_group.id)
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
                        orgut_bolge_sorumlusu_group.id,
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
                        self.env.ref('orgut_yonetimi.orgut_bolge_sorumlusu'),
                        self.env.ref('orgut_yonetimi.orgut_il_sorumlusu'),
                        self.env.ref('orgut_yonetimi.orgut_ilce_sorumlusu'),
                        self.env.ref('base.group_partner_manager')
                    ]
                    user.write({'groups_id': [(3, group.id) for group in groups_to_remove]})

    @api.constrains('name', 'country')
    def _check_unique_region_country(self):
        for record in self:
            existing_region = self.search(
                [('name', '=', record.name), ('country', '=', record.country.id), ('id', '!=', record.id)], limit=1)
            if existing_region:
                raise exceptions.ValidationError('Bu bölge örgütü zaten mevcut.')