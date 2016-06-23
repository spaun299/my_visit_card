import tornado.web
import tornado.gen
import tornado.escape
from utils import call_blocking_func_async
import tornado.ioloop


class AdminBase(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie('user')

    @property
    def db(self):
        return self.application.db_async

    @property
    def db_connect(self):
        return self.application.db_connect

    @tornado.gen.coroutine
    def save_file(self, file, path):
        if file:
            with open(path.replace(' ', '_'), 'wb') as out:
                out.write(file[0]['body'])
        return


class AdminAuth(AdminBase):

    @tornado.gen.coroutine
    def get(self):
        self.render('admin/login.html')

    @tornado.gen.coroutine
    def post(self):
        cursor = yield self.db.execute(""" SELECT name, password FROM admin; """)
        fields = cursor.fetchone()
        if fields['name'] == self.get_argument('name') and fields['password'] \
                == self.get_argument('password'):
            self.set_secure_cookie('user', self.get_argument('name'))
            self.redirect('/admin')
        else:
            self.redirect('/admin/login')


class AdminPanelAboutMe(AdminBase):

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        english_levels = ['Pre Intermediate', 'Intermediate',
                          'Upper Intermediate', 'Advanced', 'Fluent']
        cursor = yield self.db.execute(""" SELECT * FROM me; """)
        me = cursor.fetchone()
        self.render('admin/about_me.html', english_levels=english_levels,
                    me=me)

    @tornado.gen.coroutine
    def post(self):
        required_fields = ['phone', 'skype', 'github_link', 'linkedin_link',
                           'bitbucket_link', 'facebook_link', 'email', 'email_password',
                           'location', 'english_level', 'status',
                           'description', 'short_description']
        dict_fields = {}
        for field in required_fields:
            dict_fields[field] = self.get_argument(field, None)
        cursor = yield self.db.execute(""" SELECT COUNT(*) FROM me; """)
        (exists, ) = cursor.fetchone()
        if exists:
            cursor = yield self.db.execute(""" UPDATE me SET description='{description}',
                                           short_description='{short_description}',
                                           github_link='{github_link}',
                                           linkedin_link='{linkedin_link}',
                                           bitbucket_link='{bitbucket_link}',
                                           facebook_link='{facebook_link}', email='{email}',
                                           email_password='{email_password}', location='{location}',
                                           status='{status}', skype='{skype}', phone='{phone}',
                                           english_level='{english_level}' """.format(
                **dict_fields))
        else:
            cursor = yield self.db.execute(""" INSERT INTO me(description, short_description,
                                               github_link, linkedin_link, bitbucket_link,
                                               facebook_link, email, email_password, location,
                                               status, skype, phone, english_level)
                                               VALUES ('{description}', '{short_description}',
                                               '{github_link}', '{linkedin_link}',
                                               '{bitbucket_link}',
                                               '{facebook_link}', '{email}', '{email_password}',
                                               '{location}', '{status}', '{skype}', '{phone}',
                                               '{english_level}') """.format(**dict_fields))
        # cursor.commit()
        tornado.ioloop.IOLoop.current().spawn_callback(call_blocking_func_async,
                                                       self.save_file,
                                                       self.request.files.get('photo'),
                                                       'static/images/avatar.png')
        # self.save_avatar(self.request.files.get('photo'))
        self.redirect('/admin')


class AdminIgnoredIps(AdminBase):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        cursor = yield self.db.execute(""" SELECT ip FROM ignore_ips; """)
        ips = cursor.fetchall()
        self.render('admin/ignored_ips.html', ips=ips)

    @tornado.gen.coroutine
    def post(self):
        ip = self.get_argument('ip')
        if self.get_argument('add') == 'true':
            yield self.db.execute(""" INSERT INTO ignore_ips (ip) VALUES ('%s');""" % ip)
        else:
            yield self.db.execute(""" DELETE FROM ignore_ips WHERE ip='%s' """ % ip)


class AdminUsers(AdminBase):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        cursor = yield self.db.execute(""" SELECT * FROM users ORDER BY date DESC; """)
        users = cursor.fetchall()
        self.render('admin/visits.html', users=users)


class AdminAllSkills(AdminBase):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        cursor = yield self.db.execute(""" SELECT * FROM all_skills; """)
        skills = cursor.fetchall()
        self.render('admin/all_skills.html', skills=skills)

    @tornado.gen.coroutine
    def post(self):
        file = self.request.files.get('file_skill')
        file_name = '%s.png' % self.get_argument('skill_name')
        file_path = 'images/skills/%s' % file_name
        yield call_blocking_func_async(self.save_file,
                                       file, 'static/%s' % file_path)
        yield self.db.execute(""" INSERT INTO all_skills (name, icon_link, web_site)
                              VALUES('{skill_name}', '{file_link}', '{web_site}')""".format(
            skill_name=self.get_argument('skill_name'), file_link=file_path.replace(' ', '_'),
            web_site=self.get_argument('web_site')
        ))
        self.redirect('/admin/all_skills')


class AdminMySkills(AdminBase):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        all_skills_str = """ SELECT all_.*, my_.priority as priority FROM all_skills all_
                             LEFT OUTER JOIN my_skills my_ ON all_.id = my_.skill_id;"""
        cursor_all = yield self.db.execute(all_skills_str)
        all_skills = cursor_all.fetchall()
        self.render('admin/my_skills.html',
                    all_skills=all_skills)

    @tornado.gen.coroutine
    def post(self):
        name = self.get_argument('name')
        priority = self.get_argument('priority', 0)
        checked = tornado.escape.json_decode(self.get_argument('checkbox_value'))
        tornado.ioloop.IOLoop.current().spawn_callback(self.save_update_my_skills,
                                                       name, checked, priority)
        return

    @tornado.gen.coroutine
    def save_update_my_skills(self, name, checked, priority, ):
        str_to_execute = None
        flag = yield self.db.execute(""" SELECT my_skills.skill_id FROM my_skills
                                     LEFT JOIN all_skills ON my_skills.skill_id = all_skills.id
                                     WHERE all_skills.name='{skill_name}'; """.format(
            skill_name=name
        ))

        flag = flag.fetchone()
        if not flag and checked:
            str_to_execute = """ INSERT INTO my_skills(skill_id, priority)
                                 VALUES ((SELECT id FROM all_skills
                                 WHERE all_skills.name = '{skill_name}'), '{priority}'); """.format(
                skill_name=name, priority=priority or 0
            )

        elif not checked and flag:
            str_to_execute = """ DELETE FROM my_skills WHERE skill_id = '{skill_id}'; """.format(
                skill_id=flag['skill_id']
            )
        elif not flag:
            pass
        else:
            str_to_execute = """ UPDATE my_skills SET priority='{priority}'
                                 WHERE skill_id='{skill_id}'; """.format(priority=priority,
                                                                         skill_id=flag['skill_id'])
        if str_to_execute:
            yield self.db.execute(str_to_execute)


class AdminExperience(AdminBase):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        my_experience = yield self.db.execute(""" SELECT * FROM experience ORDER BY date_from; """)
        self.render('admin/experience.html', experience=my_experience.fetchall())

    @tornado.gen.coroutine
    def post(self):
        required_fields = ['company_name', 'position', 'date_from', 'date_to',
                           'company_description', 'my_responsobility',
                           'workers_amount', 'location', 'web_site']
        dict_fields = {}
        for field in required_fields:
            dict_fields[field] = self.get_argument(field)
        if dict_fields.get('date_to') == 'None':
            del dict_fields['date_to']
        tornado.ioloop.IOLoop.current().spawn_callback(self.save_update_company,
                                                       **dict_fields)
        self.redirect(self.request.path)

    @tornado.gen.coroutine
    def save_update_company(self, **kwargs):
        flag = yield self.db.execute(""" SELECT id FROM experience
                                     WHERE experience.company_name='{company_name}';""".format(
            company_name=kwargs.get('company_name')
        ))
        experience_id = flag.fetchone()
        if experience_id:
            if kwargs.get('date_to'):
                str_to_execute = """ UPDATE experience SET company_name='{company_name}',
                                 position='{position}', date_from='{date_from}',
                                 date_to='{date_to}', company_description='{company_description}',
                                 my_responsobility='{my_responsobility}',
                                 workers_amount='{workers_amount}', location='{location}',
                                 web_site='{web_site}' WHERE id='{exp_id}';""".format(
                    exp_id=experience_id['id'], **kwargs)
            else:
                str_to_execute = """ UPDATE experience SET company_name='{company_name}',
                     position='{position}', date_from='{date_from}',
                     company_description='{company_description}',
                     my_responsobility='{my_responsobility}',
                     workers_amount='{workers_amount}', location='{location}',
                     web_site='{web_site}' WHERE id='{exp_id}';""".format(
                    exp_id=experience_id['id'], **kwargs)
        else:
            if kwargs.get('date_to'):
                str_to_execute = """ INSERT INTO experience(company_name, position,
                                 date_from, date_to, company_description, my_responsobility,
                                 workers_amount, location, web_site) VALUES(
                                 '{company_name}', '{position}', '{date_from}', '{date_to}',
                                 '{company_description}', '{my_responsobility}',
                                 '{workers_amount}', '{location}', '{web_site}') ;""".format(
                    **kwargs)
            else:
                str_to_execute = """ INSERT INTO experience(company_name, position,
                     date_from, company_description, my_responsobility,
                     workers_amount, location, web_site) VALUES(
                     '{company_name}', '{position}', '{date_from}',
                     '{company_description}', '{my_responsobility}',
                     '{workers_amount}', '{location}', '{web_site}') ;""".format(
                    **kwargs)
        yield self.db.execute(str_to_execute)


class AdminProjects(AdminBase):

    @tornado.gen.coroutine
    def get(self):
        projects = yield self.db.execute(""" SELECT p.*, e.company_name, s.name as skill_name,
                                         s.icon_link as skill_icon, s.id as skill_id FROM projects p
                                         LEFT JOIN experience e ON p.company_id=e.id
                                         LEFT JOIN projects_skills_assoc ps ON ps.project_id=p.id
                                         LEFT JOIN all_skills s ON ps.skill_id = s.id;""")
        projects = projects.fetchall()
        projects = {project['id']:{'name': project['name'], 'type': project['type'],
                                   'web_site': project['web_site'],
                                   'company_name': project['company_name'],
                                   'description': project['description'],
                                   'status': project['status'],
                                   'team_size': project['team_size'],
                                   'months_spend': project['months_spend'],
                                   'skills': [proj['skill_id']
                                              for proj in projects if proj['id']==project['id']]}
                    for project in projects}
        skills_companies = yield self.db.execute(""" SELECT e.company_name,
                                                 e.id as company_id, s.id as skill_id,
                                                 s.name as skill_name, s.icon_link as skill_icon
                                                 FROM experience e
                                                 CROSS JOIN all_skills s;""")
        skills_companies = skills_companies.fetchall()
        skills = {sc['skill_id']: {'name': sc['skill_name'],
                                   'icon_link': sc['skill_icon']} for sc in skills_companies}
        companies = {sc['company_id']: {'name': sc['company_name']} for sc in skills_companies}
        self.render('admin/projects.html', skills=skills, companies=companies,
                    projects=projects)

    @tornado.gen.coroutine
    def post(self):
        required_fields = ['name', 'type', 'web_site', 'status', 'company_id',
                           'description', 'project_id', 'team_size', 'months_spend']
        dict_field = {}
        for field in required_fields:
            dict_field[field] = self.get_argument(field, '')
        dict_field.update({'skills_id': self.get_arguments('skill')})
        tornado.ioloop.IOLoop.current().spawn_callback(self.save_update_projects,
                                                       **dict_field)
        self.redirect('/admin')

    @tornado.gen.coroutine
    def save_update_projects(self, **kwargs):

        str_to_execute = """SELECT p.id as project_id, s.skill_id as skill_id
                            FROM projects p LEFT JOIN projects_skills_assoc s ON
                            p.id = s.project_id"""
        p_id = kwargs.get('project_id')
        if not p_id:
            str_to_execute += """ WHERE p.name='{project_name}'; """.format(
            project_name=kwargs.get('name'))
        else:
            str_to_execute += """ WHERE p.id='{project_id}'; """.format(
            project_id=p_id)
        flag = yield self.db.execute(str_to_execute)
        str_to_execute = 'BEGIN;'
        project = flag.fetchall()
        if project:
            str_to_execute += """UPDATE projects SET company_id='{company_id}',
                              name='{project_name}', type='{type}', web_site='{web_site}',
                              logo_link='{logo_link}', description='{description}',
                              status='{status}', team_size='{team_size}',
                              months_spend='{months_spend}'
                              WHERE projects.id='{id}';""".format(
            id=p_id, company_id=kwargs.get('company_id'), project_name=kwargs.get('name'),
            type=kwargs.get('type'), web_site=kwargs.get('web_site'),
                logo_link=(yield self.get_path_save_file(kwargs.get('name'),
                                                         self.request.files.get('image'))),
                description=kwargs.get('description'), status=kwargs.get('status'),
                team_size=kwargs.get('team_size'), months_spend=kwargs.get('months_spend'))
            skills_id = kwargs.get('skills_id')
            unprocessed_skills = skills_id[:]
            for item in project:
                if item.get('skill_id') in skills_id:
                    unprocessed_skills.remove(item.get('skill_id'))
                elif not item.get('skill_id'):
                    unprocessed_skills = []
                    for id_ in skills_id:
                        str_to_execute += """ INSERT INTO projects_skills_assoc(skill_id,
                                          project_id) VALUES('{skill_id}',
                                          '{project_id}');""".format(skill_id=id_, project_id=p_id)
                elif item.get('skill_id') not in skills_id:
                    str_to_execute += """ DELETE FROM projects_skills_assoc
                                      WHERE skill_id='{skill_id}'
                                      AND project_id='{project_id}'; """.format(
                        skill_id=item.get('skill_id'), project_id=p_id
                    )

            for id_ in unprocessed_skills:
                str_to_execute += """ INSERT INTO projects_skills_assoc(skill_id, project_id)
                          VALUES('{skill_id}', '{project_id}');""".format(
                    skill_id=id_, project_id=p_id)
        else:
            project_id = yield self.db.execute(""" INSERT INTO projects(company_id, name, type,
                                               web_site, logo_link, description, status, team_size,
                                               months_spend)
                                               VALUES('{company_id}', '{project_name}', '{type}',
                                               '{web_site}', '{logo_link}',
                                               '{description}', '{type}', '{team_size}',
                                               '{months_spend}')
                                               RETURNING id;""".format(
                company_id=kwargs.get('company_id'), project_name=kwargs.get('name'),
                type=kwargs.get('type'), web_site=kwargs.get('web_site'),
                logo_link=(yield self.get_path_save_file(kwargs.get('name'),
                                 self.request.files.get('image'))),
                description=kwargs.get('description'), status=kwargs.get('status'),
                team_size=kwargs.get('team_size'), months_spend=kwargs.get('months_spend')))
            project_id = project_id.fetchone()['id']
            for skill_id in kwargs.get('skills_id'):
                str_to_execute += """ INSERT INTO projects_skills_assoc(skill_id, project_id)
                              VALUES {list_} ;""".format(
                    list_=tuple([skill_id, project_id]))
        str_to_execute += 'COMMIT;'
        yield self.db.execute(str_to_execute)

    @tornado.gen.coroutine
    def get_path_save_file(self, filename, file):
        path = 'images/projects/%s.png' % filename
        if file:
            tornado.ioloop.IOLoop.current().spawn_callback(call_blocking_func_async,
                                                           self.save_file,
                                                           file, 'static/%s' % path)
        return path.replace(' ', '_')


class AdminEducation(AdminBase):

    @tornado.gen.coroutine
    def get(self):
        educations = yield self.db.execute(""" SELECT * FROM education ORDER BY date_from;""")
        self.render("admin/education.html", educations=educations.fetchall())

    @tornado.gen.coroutine
    def post(self):
        required_fields = ['name', 'school_name', 'date_from', 'date_to', 'location']
        dict_fields = {}
        for field in required_fields:
            dict_fields[field] = self.get_argument(field, None) if self.get_argument(field, None) \
                                                                   != 'None' else None
        yield self.save_update_education(**dict_fields)
        self.redirect(self.request.path)

    @tornado.gen.coroutine
    def save_update_education(self, **kwargs):
        flag = yield self.db.execute(""" SELECT id FROM education WHERE name='{name}'; """.format(
            name=kwargs.get('name')
        ))
        education = flag.fetchone()
        if education:
            if kwargs.get('date_to'):
                str_to_execute = """ UPDATE education SET name='{name}',
                                 school_name='{school_name}', date_from='{date_from}',
                                 date_to='{date_to}', location='{location}'
                                 WHERE id='{id}';""".format(id=education['id'], **kwargs)
            else:
                str_to_execute = """ UPDATE education SET name='{name}',
                     school_name='{school_name}', date_from='{date_from}', date_to=NULL,
                      location='{location}' WHERE id='{id}';""".format(id=education['id'], **kwargs)
        else:
            if kwargs.get('date_to'):
                str_to_execute = """ INSERT INTO education(name, school_name, date_from, date_to,
                                 location) VALUES('{name}', '{school_name}', '{date_from}',
                                 '{date_to}', '{location}');""".format(**kwargs)
            else:
                str_to_execute = """ INSERT INTO education(name, school_name, date_from,
                                 location, date_to) VALUES('{name}', '{school_name}', '{date_from}',
                                 '{location}', NULL);""".format(**kwargs)
        yield self.db.execute(str_to_execute)
