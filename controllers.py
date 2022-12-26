from flask import render_template, request, redirect, url_for, flash, send_file, after_this_request
from flask_login import *
from forms import *
from models import *
from datetime import datetime
from password import hasher
from io import BytesIO
import pandas as pd
from app import app, db, login_manager
from api import api
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import base64
import matplotlib

matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False
matplotlib.rcParams['font.family'] = 'monospace'
matplotlib.rcParams['font.sans-serif'] = ['Verdana']
matplotlib.rcParams['font.size'] = 16


@login_manager.user_loader
def user_loader(user_id):
    return db.session.query(User).get(user_id)

@app.route('/')
def home():
    return render_template('pages/home.html', today=datetime.date(datetime.now()), color_code="BE8C63")


@app.route('/about')
def about():
    return render_template('pages/about.html', current_user=current_user, color_code="FBFBFB")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=hasher(form.username.data, form.password.data))
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template('forms/register.html', form=form, color_code="F4F5D2", photo_no=0)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():

        user = user_loader(form.username.data)
        login_user(user)
        return redirect(url_for("home"))

    return render_template('forms/login.html', form=form, color_code="D3CEDF", photo_no=5)


@app.route('/add/list', methods=['GET', 'POST'])
@login_required
def add_list():
    form = ListForm(request.form)

    if form.validate_on_submit():

        list = List(name=form.name.data,
                    description=form.description.data,
                    username=current_user.username)
        db.session.add(list)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('forms/list.html', form=form, list=[], color_code="F0CCDC", photo_no=2)


@app.route('/update/list/<list_id>', methods=['GET', 'POST'])
@login_required
def update_list(list_id):
    list = db.session.query(List).get(list_id)
    form = ListForm(request.form, name=list.name, description=list.description)

    if form.validate_on_submit():

        list.name = form.name.data
        list.description = form.description.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('forms/list.html', form=form, list=list, color_code="C6EFCA", photo_no=3)


@app.route('/delete/list/<list_id>')
@login_required
def delete_list(list_id):
    list = db.session.query(List).get(list_id)
    db.session.delete(list)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/delete/list/<list_id>/<xlist_id>')
@login_required
def move_tasks(list_id, xlist_id):

    list = db.session.query(List).get(list_id)
    list_tasks = list.tasks
    db.session.delete(list)

    for task in list_tasks:
        task.list_id = xlist_id
        db.session.add(task)

    db.session.commit()

    return redirect(url_for('home'))


@app.route('/add/task/<list_id>', methods=['GET', 'POST'])
@login_required
def add_task(list_id):

    default_list = db.session.query(List).get(list_id)
    list_names = [(list.id, list.name) for list in current_user.lists]
    # todate = datetime.now().strftime('%d/%m/%y')

    form = TaskForm(request.form,
                    list=default_list.id,
                    update=False)
    form.list.choices = list_names

    if form.validate_on_submit():

        task = Task(title = form.title.data,
                    content = form.content.data,
                    deadline = form.deadline.data,
                    status = form.status.data,
                    created = datetime.now(),
                    updated = datetime.now(),
                    list_id = form.list.data)
        db.session.add(task)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('forms/task.html', form=form, list=default_list, color_code="D6AD98", photo_no=4)


@app.route('/update/task/<list_id>/<task_title>', methods=['GET', 'POST'])
@login_required
def update_task(list_id, task_title):

    task = db.session.query(Task).get((task_title, list_id))
    list_names = [(list.id, list.name) for list in current_user.lists]
    form = TaskForm(request.form,
                    list = task.list_id,
                    title = task.title,
                    content = task.content,
                    deadline = task.deadline)
    form.update = True

    form.list.choices = list_names

    if form.validate_on_submit():

        task.title = form.title.data
        task.content = form.content.data
        task.deadline = form.deadline.data
        task.status = form.status.data
        task.updated = datetime.now()
        task.list_id = form.list.data

        db.session.commit()

        return redirect(url_for('home'))

    return render_template('forms/task.html', form=form, list=list, task=task, color_code="FCF5DC", photo_no=1)


@app.route('/delete/task/<list_id>/<task_title>')
@login_required
def delete_task(list_id, task_title):
    task = db.session.query(Task).get((task_title, list_id))
    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/summary')
@login_required
def summary():

    labels = ['complete', 'incomplete', 'passed']
    colors = ['#54BAB9', '#F7D59C', '#BB6464']

    data = dict()
    pies = dict()
    bars = dict()
    gantts = dict()

    for list in current_user.lists:
        if list.tasks:
            
            data[list.id] = {'labels':[], 'complete':[], 'incomplete':[], 'passed':[]}
            dates = dict()

            for task in sorted(list.tasks, key=lambda t: t.deadline):
                date = task.deadline.strftime('%d-%b')
                try:
                    dates[date]
                except:
                    dates[date] = {'complete':0, 'incomplete':0, 'passed':0}
                finally:
                    if task.status:
                        dates[date]['complete'] += 1
                    elif task.deadline >= datetime.date(datetime.now()):
                        dates[date]['incomplete'] += 1
                    else:
                        dates[date]['passed'] += 1

            all_dates = [i.strftime('%d-%b') for i in sorted(remove_duplicates([task.created.date() for task in list.tasks] + [task.deadline for task in list.tasks]))]

            task_names = []
            task_widths = []
            task_lefts = []
            task_colours = []

            print(all_dates)
            for task in sorted(list.tasks, key=lambda t:t.created):
                date_created = task.created.strftime('%d-%b')
                date_deadline = task.deadline.strftime('%d-%b')
                left = all_dates.index(date_created)
                days_between = all_dates.index(date_deadline) - left

                if days_between>0:
                    task_names.append(task.title)
                    task_widths.append(days_between)
                    task_lefts.append(left)

                if task.status:
                    task_colours.append(colors[0])
                elif task.deadline >= datetime.date(datetime.now()):
                    task_colours.append(colors[1])
                else:
                    task_colours.append(colors[2])

            for i in dates:
                data[list.id]['labels'].append(i)
                data[list.id]['complete'].append(dates[i]['complete'])
                data[list.id]['incomplete'].append(dates[i]['incomplete'])
                data[list.id]['passed'].append(dates[i]['passed'])

            data[list.id]['pie'] = [sum(data[list.id][i]) for i in ['complete', 'incomplete', 'passed']]

            pie_fig = Figure(figsize=(11, 11))
            pie_ax = pie_fig.subplots()
            pie_ax.pie(data[list.id]['pie'], colors=colors, explode=(0.05, 0.05, 0.05))
            pie_buf = BytesIO()
            pie_fig.savefig(pie_buf, format="png", transparent=True)
            pie = base64.b64encode(pie_buf.getbuffer()).decode("ascii")
            pies[list.id] = {'pie':pie, 'data':data[list.id]['pie']}

            bar_fig = Figure(figsize=(7, 7))
            bar_ax = bar_fig.subplots()
            bar_ax.bar(data[list.id]['labels'], data[list.id]['incomplete'], color=colors[1])
            bar_ax.bar(data[list.id]['labels'], data[list.id]['passed'], color=colors[2], bottom=data[list.id]['incomplete'])
            bar_ax.bar(data[list.id]['labels'], data[list.id]['complete'], color=colors[0], bottom=[i+j for i,j in zip(data[list.id]['passed'], data[list.id]['incomplete'])])
            bar_ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            bar_ax.set_xlabel('Deadline')
            bar_buf = BytesIO()
            bar_fig.savefig(bar_buf, format="png", transparent=True)
            bar = base64.b64encode(bar_buf.getbuffer()).decode("ascii")
            bars[list.id] = bar

            gantt_fig = Figure(figsize=(10, 10))
            gantt_ax = gantt_fig.subplots()
            gantt_ax.barh(task_names, task_widths, left=task_lefts, height=0.7, color=colors)
            gantt_ax.set_xticks(range(len(all_dates)), all_dates, rotation ='vertical')

            gantt_buf = BytesIO()
            gantt_fig.savefig(gantt_buf, format="png", transparent=True)
            gantt = base64.b64encode(gantt_buf.getbuffer()).decode("ascii")
            gantts[list.id] = gantt

    return render_template('pages/summary.html', pies=pies, bars=bars, gantts=gantts, color_code="8BA1AD")


@app.route('/stats/list/<list_id>', methods=['GET'])
@login_required
def list_stat(list_id):
    list = db.session.query(List).get(list_id)
    if list:
        if list.username != current_user.username:
            return render_template('errors/500.html', error='Specified list is not under logged in user scope')
    else:
        return render_template('errors/500.html', error='List id does not exist')

    table = []
    for task in list.tasks:
        table.append([str(i) for i in [task.title, task.content, task.deadline, task.status, task.created, task.updated]])

    df = pd.DataFrame(table, columns=['Title', 'Content', 'Deadline', 'Status', 'Created', 'Updated'])

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = f"{list.name}")
    writer.close()

    output.seek(0)

    return send_file(output, mimetype="application/msexcel", attachment_filename=f"{current_user.username}_{list.name}.xlsx", as_attachment=True)


@app.route('/stats/user', methods=['GET'])
@login_required
def user_stat():

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    table = [[list.id, list.name, list.description] for list in current_user.lists]
    df = pd.DataFrame(table, columns=['List ID', 'Name', 'Description'])

    df.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = f"{current_user.username} Lists")

    for list in current_user.lists:
        table = []
        for task in list.tasks:
            table.append([str(i) for i in [task.title, task.content, task.deadline, task.status, task.created, task.updated]])
        df = pd.DataFrame(table, columns=['Title', 'Content', 'Deadline', 'Status', 'Created', 'Updated'])
        df.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = f"{list.name}")

    writer.close()
    output.seek(0)
    return send_file(output, mimetype="application/msexcel", attachment_filename=f"{current_user.username}_lists.xlsx", as_attachment=True)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

remove_duplicates = lambda i: list(set(i))
