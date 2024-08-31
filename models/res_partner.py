from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    orgut_country_id = fields.Many2one('res.country', string='Country')
    orgut_region_id = fields.Many2one('orgut.region', string='Region', required=True)
    orgut_state_id = fields.Many2one('orgut.state', string='State', required=True)
    orgut_city_id = fields.Many2one('orgut.city', string='City', required=True)

    company_type = fields.Boolean(default=False)

    register_date = fields.Date(string="Üyelik Tarihi", track_visibility="always")
    gender = fields.Selection(
        [("erkek", "ERKEK"), ("kadin", "KADIN"), ("lgbti", "LGBTİ+"), ("none", "Belirtmek İstemiyorum")],
        string="Cinsiyet", )
    aidat_tutari = fields.Integer(string='Aidat Tutarı', help="Aidat Tutarı")
    birthdate = fields.Date(string="Doğum Tarihi")
    edu = fields.Selection(
        [("ilkokul", "İlk Öğretim"), ("ortaokul", "Orta Öğretim"), ("lise", "Lise"), ("onlisans", "Ön Lisans"),
         ("lisans", "Lisans"), ("yükseklisans", "Yüksek Lisans"), ("doktora", "Doktora"),
         ("lisansustu", "Lisans Üstü")], string="Eğitim Durumu"
    )
    family_contact = fields.Char(string="Aile Tel")
    blood_type_aob = fields.Selection(selection=[("ap", "A Rh+"), ("bp", "B Rh+"), ("abp", "AB Rh+"), ("op", "0 Rh+"),
                                                 ("an", "A Rh-"), ("bn", "B Rh-"), ("abn", "AB Rh-"), ("on", "0 Rh-")],
                                      string="Kan Grubu", )
    member_nufus_il = fields.Many2one('res.country.state', string='Nüfusa Kayıtlı İl')
    member_nufus_ilce = fields.Many2one('res.city', string='Nüfusa Kayıtlı İlçe')

    is_employed = fields.Selection(selection=[("sgk", "SGK"), ("bagkur", "BAĞKUR"),
                                                            ("emekli", "EMEKLİ"), ("calismiyor", "ÇALIŞMIYOR")],
                                                 string="Çalışma Durumu", default="calismiyor")
    member_work_sector = fields.Selection(
        selection=[("1", "1-)Avcılık, Balıkçılık, Tarım ve Ormancılık"), ("2", "2-)Gıda Sanayi"),
                   ("3", "3-)Madencilik ve Taş Ocakları"), ("4", "4-)Petrol Kimya, Lastik, Plastik ve İlaç"),
                   ("5", "5-)Dokuma, Hazır Giyim ve Deri"), ("6", "6-)Ağaç ve Kâğıt"), ("7", "7-)İletişim"),
                   ("8", "8-)Basın, Yayın ve Gazetecilik"), ("9", "9-)Banka, Finans ve Sigorta"),
                   ("10", "10-)Ticaret, Büro, Eğitim ve Güzel Sanatlar"), ("11", "11-)Çimento, Toprak ve Cam"),
                   ("12", "12-)Metal"), ("13", "13-)İnşaat"), ("14", "14-)Enerji"), ("15", "15-)Taşımacılık"),
                   ("16", "16-)Gemi Yapımı ve Deniz Taşımacılığı, Ardiye ve Antrepoculuk"),
                   ("17", "17-)Sağlık ve Sosyal Hizmetler"), ("18", "18-)Konaklama ve Eğlence İşleri"),
                   ("19", "19-)Savunma ve Güvenlik"), ("20", "20-)Genel İşler")
                   ], string="İş Kolu", )


    @api.onchange('user_id')
    def _onchange_user(self):
        if self.env.user.has_group('orgut_yonetimi.orgut_bolge_sorumlusu'):
            region = self.env.user.partner_id.orgut_region_id
            if region:
                self.orgut_region_id = region.id
        elif self.env.user.has_group('orgut_yonetimi.orgut_il_sorumlusu'):
            state = self.env.user.partner_id.orgut_state_id
            if state:
                self.orgut_state_id = state.id
                self.orgut_region_id = state.region.id
        elif self.env.user.has_group('orgut_yonetimi.orgut_ilce_sorumlusu'):
            city = self.env.user.partner_id.orgut_city_id
            if city:
                self.orgut_city_id = city.id
                self.orgut_state_id = city.state.id
                self.orgut_region_id = city.region.id


    @api.onchange('orgut_region_id')
    def _onchange_orgut_region_id(self):
        self.orgut_state_id = False
        self.orgut_city_id = False

    @api.onchange('orgut_state_id')
    def _onchange_orgut_state_id(self):
        self.orgut_city_id = False

    @api.onchange('is_employed')
    def _onchange_is_employed(self):
        self.member_work_sector = False

