from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class SchoolTeacherSalaryHistory(models.Model):
    _name = ''
    _description = ''
    _order= 'id desc' # 'date desc, time_f desc'

    teacher_id = fields.Many2one('school.teacher', string="Teacher", required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='restrict') #ja és restrict per defecte.

    date = fields.Date('Date', required=True)
    time_f = fields.Float('Time-F', digits=(5,2), required=True) #La hora es guarda com a float -> Exemple. 18:30 --> 18,5
    time_s = fields.Char('Time-S', size=5, required=True) #Hora en string
    salary = fields.Integer('Salary', required=True)
