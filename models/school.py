# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import validationError
from datetime import date
from dateutil.relativedelta import relativedelta
from ..utils.utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py a la carpeta de nivell superior:
#from ..utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py a la carpeta de 2 nivells per damunt:
# from ...utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py en una subcarpeta xxx:
# from .xxx.utils import is_valid_email



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
    thematic_id = fields.Many2one('school.thematic', string='Thematic', required=True)


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'

    name = fields.Char('Name', size=60, required=True, translate=True) #S'ha de poder traduir
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    teacher_ids = fields.Many2many('school.teacher', 'school_teacher_subject_rel',
                                   'subject_id', 'teacher_id', string='Teachers authorized', readonly=True)
    course_ids = fields.Many2many('school.course', 'school_course_subject_rel',
                                  'subject_id', 'course_id', readonly=True)


class SchoolTeacher(models.Model):
    #El _ al davant indica que és privat.
    _name = 'school.teacher'
    _description = 'Teacher Management'
    _rec_name = 'display_name' #Per defecte és Name, però no tenim aquest camp

    first_name = fields.Char('First Name', size=30, required=True)
    last_name = fields.Char('Last Name', size=40, required=True)
    birthdate = fields.Date('Birthdate', required=True)
    tin = fields.Char('Tax ID', size=14)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],'Gender')
    salary = fields.Integer('Salary')
    email = fields.Char('eMail', size=60, required=True)
    phone = fields.Char('Phone')
    #Relacio One2Many: ONE TEACHER pot tenir MANY cursos. Un curs pot tenir un teacher. 
    course_ids = fields.One2many('school.course', 'manager_id', string='Courses', readonly=True)    #_rec_name= "first_name"
    subject_ids = fields.Many2many(
        comodel_name='school.subject',
        relation='school_teacher_subject_rel', 
        column1='teacher_id',                   
        column2='subject_id',
        string='Subjects authorized'
    )
    #comodel_name= nom de la relació a la que apunta
    #relation = nom de la nova taula que es crea i que conté la relació
    #column1 i column2 han d'estar girades respecte la many2many definida a teacher!!
    #20260209
    active = fields.Boolean('Active?', default=True)
    country_id = fields.Many2one('res.country','Citizenship', required=True)
    #Camps calculats:
    #full_name= fields.Char('Full name', compute='_compute_full_name', store=False)
    #Treiem el full_name perquè farem servir display_name.
    age =fields.Integer('Age', compute='_compute_age', store=False)

    #El _ al davant indica que és privat.
    @api.depends('first_name', 'last_name')
    def _compute_display_name(self):
        #self és equivalent a this.
        #és el conjunt de registres (recordset) sobre el que es necessita executar el mètode.
        for tchr in self:
            if tchr.first_name and tchr.last_name:
                tchr.display_name = tchr.last_name + ", " + tchr.first_name
            else:
                tchr.display_name = ''
            
    @api.depends('birthdate')
    def _compute_age(self):
        avui = date.today()
        for tchr in self:
            if tchr.birthdate: 
                tchr.age = relativedelta(avui, tchr.birthdate).years
            else:
                tchr.age = 0

    @api.constrains('salary')
    def check_salary(self):
        for tchr in self:
            if tchr.salary<0:
                raise ValidationError(_('Salary must be positive.'))



    
class SchoolThematic(models.Model):
    _name = 'school.thematic'
    _description = 'Thematic Management'

    name = fields.Char('Name', required=True)

    course_ids = fields.One2many('school.course', 'thematic_id', string='Courses', readonly=True)
    #Relacio recursiva:
    parent_id = fields.Many2one('school.thematic','Parent Thematic')
    child_ids = fields.One2many('school.thematic','parent_id','Child Thematics', readonly=True)