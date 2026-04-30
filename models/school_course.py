# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError

class SchoolCourse(models.Model):
    _name = 'school.course'
    _description = 'Course Management'
    _order = 'name'

    name = fields.Char('Name', size=60, required=True)
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    summary = fields.Text('Summary', required=False) #Alternativa: Html.
    
    manager_id = fields.Many2one('school.teacher', 'Manager', required=True) #, domain=[('country_id.code', '=', 'ES')])     #relacio Many to One: MANY CURSOS pot tenir ONE teacher. un teacher pot tenir molts cursos.
    thematic_id = fields.Many2one('school.thematic', string='Thematic', required=True)
    course_subject_ids = fields.One2many('school.course.subject', 'course_id', string='Subjects', readonly=True) 
    course_edition_ids = fields.One2many('school.course.edition', 'course_id', string='Editions')

    #Camps extra per a poder posar-los en les vistes
    manager_phone = fields.Char('Phone', related='manager_id.phone')
    manager_email = fields.Char('eMail', related='manager_id.email')
    manager_citizenship = fields.Many2one('res.country', string='Citizenship', related='manager_id.country_id')     #manager_citizenship = fields.Char('Citizenship', related='manager_id.country_id.name')


    @api.constrains('hours')
    def check_hours(self):
        for crs in self:
            if crs.hours <= 0:
                raise ValidationError(_('Hours must be positive.'))

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.name = self.name.capitalize()
  

