from hanlers import IndexHanler, TestTemplate
from admin import AdminPanelAboutMe, AdminAuth, AdminAllSkills, \
    AdminMySkills, AdminExperience, AdminProjects, AdminEducation, AdminIgnoredIps, AdminUsers

routs = [
    (r'/', IndexHanler),
    (r'/test_template', TestTemplate),
    (r'/admin', AdminPanelAboutMe),
    (r'/admin/login', AdminAuth),
    (r'/admin/all_skills', AdminAllSkills),
    (r'/admin/my_skills', AdminMySkills),
    (r'/admin/experience', AdminExperience),
    (r'/admin/projects', AdminProjects),
    (r'/admin/education', AdminEducation),
    (r'/admin/ignored_ips', AdminIgnoredIps),
    (r'/admin/users', AdminUsers)
]
