# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError

class SchoolCourseEdition(models.Model):
    _name='school.course.edition'
    _description='Course Editions Management'
    _order='date_start'
    _sql_constraints = {
        ('unique_course_date_start', 'unique(course_id, date_start)',
         _('It''s not possible 2 course editions with same course and same date start'))
    }

    name = fields.Char('Course edition', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_stop = fields.Date('Finish Date')

    # Com que SchoolCourseEdition té una relació de composició amb curs, si s'elimina el curs, s'han d'eliminar les edicions també.
    course_id = fields.Many2one('school.course', string='Course', required=True, ondelete='cascade')  

    #Camps calculats
    n_teachers = fields.Integer(string='N. Teachers', compute='_compute_n_teachers')

    @api.constrains('date_start', 'date_stop')
    def _check_dates(self):
        for edition in self:
            if edition.date_start and edition.date_stop:
                if edition.date_stop < edition.date_start:
                    raise ValidationError(_("The finish date cannot be earlier than the start date."))

    @api.onchange('name')
    def _onchange_name(self):
        if self.name!=False:
            # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
            # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False")
            self.name = self.name.title() #ho posa tot en majúscula?

#ONCHANGE
    @api.depends('name', 'course_id')
    def _compute_display_name(self):
        for edition in self:
            if edition.name and edition.course_id:
                edition.display_name = edition.course_id.name + " - " + edition.name
            else:
                edition.display_name = " - "

    #Exercici de matrícula
    def _compute_n_teachers(self):
        for edition in self:
            #Fem un SEARCH (No search_count)
            teachings = self.env['school.teaching'].search([('edition_id', '=', edition.id)])
            teachers = []
            #Fem un recorregut per la llista teachings mirant si el teacher ja esta a teachers
            for t in teachings:
                if t.teacher_id not in teachers:
                    teachers.append(t.teacher_id)
            edition.n_teachers = len(teachers)

#OVERRIDES
    @api.model_create_multi
    def create(self, values):
        # values és una llista de diccionaris amb els valors dels camps dels registres a inserir
        for diccionari in values:
            if 'name' in diccionari and diccionari['name'] != False:
                diccionari['name'] = diccionari['name'].title()
        r = super().create(values)
        return r

    def write(self, values):
        # self conté els registres a modificar
        # values conté els camps a modificar
        if 'name' in values and values['name'] != False:
            values['name'] = values['name'].title()
        register = super().write(values)
        return register

