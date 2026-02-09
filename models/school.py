# -*- coding: utf-8 -*-
from odoo import models,fields

class SchoolCourse(models.Model):
    _name = 'school.course'
    _description = 'Course Management'

    name = fields.Char('Name', size=60, required=True)
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    #relacio Many to One: MANY CURSOS pot tenir ONE teacher. un teacher pot tenir molts cursos.
    manager_id = fields.Many2one('school.teacher', 'Manager') #No és required perquè és 0..1
    subject_ids = fields.Many2many(
        comodel_name='school.subject',
        relation='school_course_subject_rel',
        column1='course_id',
        column2='subject_id',
        string='Subjects', readonly=True
    )
    thematic_id = fields.Many2one('school.thematic', string='Thematic')


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'

    name = fields.Char('Name', size=60, required=True, translate=True) #S'ha de poder traduir
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    teacher_ids = fields.Many2many('school.teacher', 'school_teacher_subject_rel',
                                   'subject_id', 'teacher_id', string='Teachers', readonly=True)
    course_ids = fields.Many2many('school.course', 'school_course_subject_rel',
                                  'subject_id', 'course_id', readonly=True)


class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher Management'
    _rec_name = 'last_name' #Per defecte és Name, però no tenim aquest camp

    first_name = fields.Char('First Name', size=30, required=True)
    last_name = fields.Char('Last Name', size=40, required=True)
    birthdate = fields.Date('Birthdate', required=True)
    tin = fields.Char('Tax ID', size=14)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],'Gender')
    salary = fields.Integer('Salary')
    email = fields.Char('eMail', size=60, required=True)
    phone = fields.Char('Phone')
    #Relacio One2Many: ONE TEACHER pot tenir MANY cursos. Un curs pot tenir un teacher. 
    course_ids = fields.One2many('school.course', 'manager_id', string='Courses')    #_rec_name= "first_name"
    subject_ids = fields.Many2many(
        comodel_name='school.subject',
        relation='school_teacher_subject_rel', 
        column1='teacher_id',                   
        column2='subject_id',
        string='Subjects'
    )
    #comodel_name= nom de la relació a la que apunta
    #relation = nom de la nova taula que es crea i que conté la relació
    #column1 i column2 han d'estar girades respecte la many2many definida a teacher!!
    #20260209

    
class SchoolThematic(models.Model):
    _name = 'school.thematic'
    _description = 'Thematic Management'
    course_ids = fields.One2many('school.course', 'thematic_id', string='Courses')