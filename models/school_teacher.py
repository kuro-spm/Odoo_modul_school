# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ , tools
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ..utils.utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py a la carpeta de nivell superior:
#from ..utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py a mateixa carpeta:
#from .utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py a la carpeta de 2 nivells per damunt:
# from ...utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py en una subcarpeta xxx:
# from .xxx.utils import is_valid_email


class SchoolTeacher(models.Model):
    #El _ al davant indica que és privat.
    _name = 'school.teacher'
    _description = 'Teacher Management'
    _rec_name = 'display_name' #Per defecte és Name, però no tenim aquest camp
    _order = 'last_name,first_name'

    _sql_constraints=[
        ('ck_salari','check(salary>=0)','Salary must be positive (controlled by BD)')
    ]
    #_sql_constraints=[('ck_salari','check(salary>=0)','Salary must be positive (controlled by BD)''')
    # No és habitual incorporar una check a la BD. S'utilitzen les @api.constraints
    # on Odoo controla la restricció abans d'enviar la instrucció insert/update a la BD
    # Aquí s'ha incorporat com exemple

    first_name = fields.Char('First Name', size=30, required=True)
    last_name = fields.Char('Last Name', size=40, required=True)
    birthdate = fields.Date('Birthdate', required=True)
    tin = fields.Char('Tax ID', size=14)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other','Other')],'Gender')
    salary = fields.Integer('Salary')
    email = fields.Char('eMail', size=60, required=True)
    phone = fields.Char('Phone')
    photo = fields.Binary(string="Photo", required=True, attachment=False) #obligar a guardar la foto sencera directament dins de la taula del professor     #max_width=1024, max_height=1024, si és Image
    active = fields.Boolean('Active?', default=True)
    
    
    course_ids = fields.One2many('school.course', 'manager_id', string='Courses', readonly=True)     #Relacio One2Many: ONE TEACHER pot tenir MANY cursos. Un curs pot tenir un teacher. 
    country_id = fields.Many2one('res.country','Citizenship', required=True)
    subject_ids = fields.Many2many(comodel_name='school.subject',relation='school_teacher_subject_rel', column1='teacher_id', column2='subject_id',string='Subjects authorized')
    #Relació inversa: teacher_ids = fields.Many2many(comodel_name='school.teacher', relation='school_teacher_subject_rel', column1='subject_id', column2='teacher_id', string='Teachers authorized', readonly=True)
    #comodel_name= nom de la relació a la que apunta
    #relation = nom de la nova taula que es crea i que conté la relació
    #column1 i column2 han d'estar girades respecte la many2many definida a teacher!!

    #Computed fields:
    n_manager = fields.Integer(string='Num. courses', compute='_compute_n_manager')
    n_subject = fields.Integer(string='Num. subject', compute='_compute_n_subject')
    n_teaching = fields.Integer(string='Num. teaching', compute='_compute_n_teaching')
    age =fields.Integer('Age', compute='_compute_age', store=False)
    #full_name= fields.Char('Full name', compute='_compute_full_name', store=False) #Treiem el full_name perquè farem servir display_name.
    birthday_this_year = fields.Date(string='Birthday', compute='compute_birthday')
    age_celebrated =fields.Integer(string='Age celebrated', compute='_compute_age_celebrated')

#CONSTRAINS:
    @api.constrains('salary')
    def check_salary(self):
        for tchr in self:
            if tchr.salary<0:
                raise ValidationError(_('Salary must be positive.'))
    
    @api.constrains('email')
    def check_email(self):
        for tchr in self:
            if tchr.email and not is_valid_email(tchr.email):
                raise ValidationError(_("The teacher's email is invalid."))

    @api.constrains('phone')
    def check_phone(self):
        for tchr in self:
            if tchr.phone and not tchr.phone.isdigit():
                raise ValidationError(_("The teacher's phone number can only contain digits."))

#ONCHANGE                
    @api.onchange('tin')
    def _onchange_tin(self):
        if(self.tin):
            self.tin = self.tin.upper()

#ÍNDEX ÚNIC _AUTO_INIT
    def _auto_init(self):
        res = super(SchoolTeacher, self)._auto_init()
        tools.create_unique_index(self._cr, 'school_teacher_unique_tin',
                                  self._table, ['lower(tin)'])
        return res

#COMPUTE:
    #El _ al davant indica que és privat.
    #Aqui configurem el display name!!!
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
            

    @api.depends('birthdate')
    def _compute_birthday(self):
        avui = date.today()
        for tchr in self:
            if tchr.birthdate:
                try:
                    # Intentem crear la data amb l'any actual
                    tchr.birthday_this_year = tchr.birthdate.replace(year=avui.year)
                except ValueError:
                    # Si falla (és 29 de febrer i l'any actual no és de traspàs)
                    # segons el dossier, ho posem al 1 de març 
                    tchr.birthday_this_year = tchr.birthdate.replace(year=avui.year, month=3, day=1)
            else:
                tchr.birthday_this_year = False


    @api.depends('course_ids')
    def _compute_n_manager(self):
        #contar cursos dins de course_ids
        for teacher in self:
            teacher.n_manager = len(teacher.course_ids)

    @api.depends('subject_ids')
    def _compute_n_subject(self):
        for teacher in self:
            teacher.n_subject = len(teacher.subject_ids)

    #Hem de fer servir el searchcount perque no tenim els cursos dins del model de teacher
    def _compute_n_teaching(self):
        for tchr in self:
            tchr.n_t
            
    @api.depends('birthdate', 'birthday_this_year')
    def _compute_age_celebrated(self):
        for tchr in self:
            if tchr.birthdate and tchr.birthday_this_year:
                # L'edat que celebra és la diferència d'anys
                tchr.age_celebrated = tchr.birthday_this_year.year - tchr.birthdate.year
            else:
                tchr.age_celebrated = 0


#OVERRIDE

    @api.model_create_multi
    def create(self, values):
        # values és una llista de diccionaris amb els valors dels camps dels registres a inserir
        for d in values:
            if 'tin' in d and d['tin'] != False:
                d['tin'] = d['tin'].upper()
        r = super().create(values)
        # Incorporem informació del salari a SchoolTeacherSalaryHistory
        momentActual = fields.Datetime.context_timestamp(self, datetime.now())
        for teacher in r:  # Per cada teacher inserit
            history = {}
            history['teacher_id'] = teacher.id
            history['user_id'] = self.env.uid
            history['date'] = momentActual.strftime('%Y-%m-%d')
            history['time_s'] = momentActual.strftime('%H:%M')
            history['time_f'] = int(momentActual.strftime('%H')) + float(momentActual.strftime('%M')) / 60
            history['salary'] = teacher.salary
            self.env['school.teacher.salary.history'].create(history)
        return r

    def write(self, values):
        # self conté els registres a modificar
        # values conté els camps a modificar
        if 'tin' in values and values['tin'] != False:
            values['tin'] = values['tin'].upper()
        r = super().write(values)
        # Incorporem informació del salari a SchoolTeacherSalaryHistory
        momentActual = fields.Datetime.context_timestamp(self, datetime.now())
        if r == True and 'salary' in values:
            for teacher in self:
                history = {}
                history['teacher_id'] = teacher.id
                history['user_id'] = self.env.uid
                history['date'] = momentActual.strftime('%Y-%m-%d')
                history['time_s'] = momentActual.strftime('%H:%M')
                history['time_f'] = int(momentActual.strftime('%H')) + float(momentActual.strftime('%M')) / 60
                history['salary'] = teacher.salary
                self.env['school.teacher.salary.history'].create(history)
        return r

    def unlink(self): #sobreescriu el mètode.
        for tchr in self:
            #accions previes a la eliminació
            #qt = self.env('school.course').search_count(['manager_id', '=', tchr.id]) #nomes compta els actius
            q = self.env['school.course'].search_count([
                    ('manager_id', '=', tchr.id),
                    '|',
                    ('active', '=', True),
                    ('active', '=', False) #fa que comptin els actius i els no actius!
                ])
            if q>0:
                raise UserError(_(
                    "Teacher '%s' cannot be deleted because this teacher is manager of %s courses."
                ) % (tchr.display_name, q))
        
        #Per a cada profe, eliminem les docencies
        for tchr in self:
            teachings = self.env['school.teaching'].search([('teacher_id', '=', tchr.id)])
            teachings.unlink()
        # S'executa l'eliminació de tot el recordset en una sola crida
        return super(SchoolTeacher, self).unlink()
    
