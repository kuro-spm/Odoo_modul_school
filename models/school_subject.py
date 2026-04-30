# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError

class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'
    _order = 'name'

    name = fields.Char('Name', size=60, required=True, translate=True) #S'ha de poder traduir
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    
    course_subject_ids = fields.One2many('school.course.subject', 'subject_id', string='Courses', readonly=True)
    #course_ids = fields.Many2many('school.course', 'school_course_subject_rel', 'subject_id', 'course_id', readonly=True)
    teacher_ids = fields.Many2many('school.teacher', 'school_teacher_subject_rel',
                                   'subject_id', 'teacher_id', string='Teachers authorized', readonly=True)
    @api.constrains('hours')
    def check_hours(self):
        for sbj in self:
            if sbj.hours<0:
                raise ValidationError(_('Hours must be positive.'))
            
    @api.onchange('name')
    def _onchange_name(self):
        if self.name!=False:
            # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
            # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False")
            self.name = self.name.capitalize()
            
