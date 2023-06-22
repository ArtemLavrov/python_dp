from jinja2 import Template, FileSystemLoader, FunctionLoader, Environment
#№1
# name = ""
# age = int
# tm = Template("Привет {{name}} поздравляю с {{age}}-летием")
# message = tm.render(name="Артём", age=10) # функция Render перенимает всё что указано в template
# print(message)


# data = '''{%raw%}я не хочу преобразовывать эти строчки
# потому что они мне нравятся, я {{name}} и мне {{age}}{%endraw%}'''
# tm = Template(data)
# message = tm.render(name = "Артём", age = 15)
# print(message)


#№2
# class_8b = [{'id': 1, 'name': 'Кирилл'},
#             {'id': 2, 'name': 'Николай'},
#             {'id': 3, 'name': 'Артём'}]
# message = '''<select name="class_8b">
# {% for i in class_8b -%}
# {% if i.id > 2  -%}
#     <option value="{{i['id']}}">{{i['name']}}</option>
# {%else -%}
#     {{i['name']}}
# {% endif -%}
# {% endfor -%}
# </select>'''
# #Можно выводить и без тегов достаточно пользоваться конструкцией {{i[ключ/значение]}}
#
# tm = Template(message)
# msg = tm.render(class_8b = class_8b)
# print(msg)

#№3
# cars = [{'model':'Ауди', 'prise': 10000},
#         {'model':'BMW', 'prise': 20000},
#         {'model':'Mersedes', 'prise': 100000},
#         {'model':'Wolkswagen', 'prise': 15000},
#         {'model':'Reno', 'prise': 9000},
#         ]
# message = "В сумме все автомобили будут стоить - {{car | sum(attribute='prise')}}"
# tm = Template(message)
# msg = tm.render(car=cars)
# print(msg)

# persons = [{'name': 'Artem', 'age': 22, 'weight': 85},
#            {'name': 'Nikolay', 'age': 23, 'weight': 70},
#            {'name': 'Maria', 'age': 22, 'weight': 65},
#            {'name': 'Kirill', 'age': 23 , 'weight': 80},
# ]
# message = '''
# {%- for i in persons -%}
# {% filter upper %}{{i.name}}{% endfilter %}
# {% endfor -%}
# '''
# tm = Template(message)
# msg = tm.render(persons=persons)
# print(msg)

#№4

# crypto_methods = [{'id': 1, 'name_method': 'RSA'},
#                   {'id': 2, 'name_method': 'magma'}
# ]
#
# file_loader = FileSystemLoader('templates')
# env = Environment(loader=file_loader)
#
# tm = env.get_template('contents.html')
# msg = tm.render(methods_name=crypto_methods, domain='http://shifr.ru', title="Сайтик для шифрования файлов")
#
# print(msg)

#5

crypto_methods = [{'id': 1, 'name_method': 'RSA'},
                      {'id': 2, 'name_method': 'magma'}
                      ]
message = '''
<ul>
{% for i in methods_name -%}
    <li>
        <a href="/{{ i.name_method }}">{{i.name_method}}</a>>
    </li>
{% endfor -%}
</ul>
'''
tm = Template(message)
msg=tm.render(methods_name=crypto_methods)
print(msg)