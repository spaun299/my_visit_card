import tornado.web
import tornado.gen
import tornado.escape
from utils import send_email_async, get_location_by_ip, \
    get_date_and_time_with_timezone, call_blocking_func_async_returning, date_formatting
import tornado.ioloop


class Base(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db_async

    @property
    def db_connect(self):
        return self.application.db_connect

    @tornado.gen.coroutine
    def save_file(self, file, path):
        if file:
            with open(path, 'wb') as out:
                out.write(file[0]['body'])
        return

    @tornado.gen.coroutine
    def save_user(self, ip):
        ignore = yield self.db.execute(""" SELECT COUNT(*) FROM ignore_ips WHERE ip='%s';""" % ip)
        exist_ip_in_ignore = ignore.fetchone()[0]
        if not exist_ip_in_ignore:
            location = yield call_blocking_func_async_returning(get_location_by_ip, ip)
            date = yield call_blocking_func_async_returning(get_date_and_time_with_timezone)
            time = yield call_blocking_func_async_returning(get_date_and_time_with_timezone,
                                                            date=False, time=True)
            yield self.db.execute(""" INSERT INTO users (location, date, time, ip)
                                  VALUES ('{location}', '{date}', '{time}', '{ip}')""".format(
                location=location, date=date, time=time, ip=ip
            ))


class TestTemplate(Base):

    def get(self):
        self.render('example.html')


class IndexHanler(Base):

    @tornado.gen.coroutine
    def get(self):
        tornado.ioloop.IOLoop.current().spawn_callback(self.save_user, self.request.remote_ip)
        me = yield self.db.execute(""" SELECT * FROM me; """)
        skills = yield self.db.execute(""" SELECT a.name, a.icon_link, a.web_site FROM my_skills m
                                       LEFT JOIN all_skills a ON m.skill_id=a.id
                                       ORDER BY m.priority DESC;""")
        experience = yield self.db.execute("""SELECT * FROM experience ORDER BY date_from DESC;""")
        projects = yield self.db.execute(""" SELECT p.*, s.name as skill_name,
                                         s.icon_link as skill_icon, s.web_site as skill_www,
                                         c.company_name as company_name
                                         FROM projects p
                                         LEFT JOIN projects_skills_assoc pss ON pss.project_id=p.id
                                         LEFT JOIN all_skills s ON pss.skill_id=s.id
                                         LEFT JOIN experience c ON p.company_id=c.id
                                         ORDER BY p.id DESC ;""")
        projects = projects.fetchall()
        projects = {project['id']: {'data': dict(project.items()),
                                    'skills': {proj['skill_name']: {'icon': proj['skill_icon'],
                                                                    'web_site': proj['skill_www']}
                                               for proj in projects if proj['id'] == project[
                                                   'id']}}
                    for project in projects}
        educations = yield self.db.execute(""" SELECT * FROM education
                                               ORDER BY date_from DESC ;""")
        for proj in projects:
            projects[proj]['data']['short_description'] = \
                projects[proj]['data']['description'][:400] if \
                    len(projects[proj]['data']['description']) > 400 else None
        self.render('base.html', me=me.fetchone(), skills=skills.fetchall(),
                    experience=experience.fetchall(), projects=projects,
                    educations=educations.fetchall(),
                    date_formatting=date_formatting)

    @tornado.gen.coroutine
    def post(self):
        message = """ Message from %(from)s \n
                      User email %(email)s \n
                      Subject: %(subject)s \n
                      Message: %(message)s""" % {'from': self.get_argument('name'),
                                                 'email': self.get_argument('email'),
                                                 'subject': self.get_argument('subject'),
                                                 'message': self.get_argument('message')}
        passw = yield self.db.execute(""" SELECT email_pass FROM admin; """)
        send_email_async(message, passw.fetchone()['email_pass'])
