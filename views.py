import hashlib

from flask import url_for, render_template, request, redirect, abort, send_from_directory, g, flash, session
from __init__ import app
import forms
from CleaningRepo import *

gr = CleaningRepo()
STR_LEN = 45


@app.route("/")
def index():
    return render_template('index.html', title="Главная")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('loggedin'):
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = gr.login_user(form.login.data, hashlib.md5(form.password.data.encode('utf-8')).hexdigest())
        if user:
            flash('Вы авторизовались!')
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))


@app.route("/users")
def users():
    return render_template('users.html', title="Работники", us=gr.get_users(), rs=gr.get_roles())


@app.route("/users/add", methods=['POST'])
def users_add():
    if session.get('role') == gr.ROLE_SUPERVISOR:
        u = request.form['username']
        p = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()
        f = request.form['fio']
        r = request.form.get('role')
        if 0 < len(u) < STR_LEN and 0 < len(p) < STR_LEN and 0 < len(f) < STR_LEN and 0 < len(r) < STR_LEN:
            if len(f) < 60 and len(u) < 10:
                if not gr.reg_user(u, p, f, int(r)):
                    flash("Пользователь уже существует")
            else:
                flash("ФИО или логин слишком длинные")
        else:
            flash("Заполните форму")
    else:
        flash("Недостаточно прав")
    return redirect(url_for("users"))


@app.route("/users/rm/<int:id>")
def users_remove(id):
    if session.get('role') == gr.ROLE_SUPERVISOR and id:
        gr.rm_user(id)
    else:
        flash("Недостаточно прав")
    return redirect(url_for("users"))


@app.route("/clients")
def clients():
    return render_template('clients.html', title="Клиенты", cs=gr.get_clients())


@app.route("/clients/add", methods=['POST'])
def clients_add():
    if session.get('role') == gr.ROLE_SUPERVISOR or session.get('role') == gr.ROLE_INSPECTOR:
        fio = request.form['fio']
        n = request.form['number']
        a = request.form['address']
        if 0 < len(fio) < STR_LEN and 0 < len(n) < STR_LEN and 0 < len(a) < STR_LEN:
            n = int(n)
            if n > 0:
                gr.add_client(fio, n, a)
            else:
                flash("Введите корректный номер")
        else:
            flash("Заполните форму")
    else:
        flash("Недостаточно прав")
    return redirect(url_for("clients"))


@app.route("/clients/rm/<int:id>")
def clients_remove(id):
    if session.get('role') == gr.ROLE_SUPERVISOR and id:
        gr.rm_client(id)
    else:
        flash("Недостаточно прав")
    return redirect(url_for("clients"))


@app.route("/orders")
def orders():
    return render_template('orders.html', title="Заказы", os=gr.get_orders(), cs=gr.get_clients(), ts=gr.get_types(), cls=gr.get_cleanings(), sts=gr.get_statuses())


@app.route("/orders/add", methods=['POST'])
def orders_add():
    if session.get('role') == gr.ROLE_SUPERVISOR or session.get('role') == gr.ROLE_INSPECTOR:
        c = request.form.get('client')
        t = request.form.get('type')
        n = request.form['name']
        cl = request.form.get('cleaning')
        if c and t and 0 < len(n) < STR_LEN and cl:
            gr.add_order(int(c), int(t), n, int(cl))
        else:
            flash("Заполните форму")
    else:
        flash("Недостаточно прав")
    return redirect(url_for("orders"))


@app.route("/orders/change", methods=['POST'])
def orders_change():
    if session.get('role') == gr.ROLE_SUPERVISOR or session.get('role') == gr.ROLE_CLEANER:
        i = request.form.get('id')
        s = request.form.get('status')
        if i and s:
            gr.change_order_status(int(i), int(s))
        else:
            flash("Заполните форму")
    else:
        flash("Недостаточно прав")
    return redirect(url_for("orders"))


@app.route("/orders/rm/<int:id>")
def orders_remove(id):
    if session.get('role') == gr.ROLE_SUPERVISOR and id:
        gr.rm_order(id)
    else:
        flash("Недостаточно прав")
    return redirect(url_for("orders"))


@app.route("/types")
def types():
    if session.get('role') >= gr.ROLE_SUPERVISOR:
        return render_template('types.html', title="Типы вещей", ts=gr.get_types())
    else:
        flash("Недостаточно прав")
        return redirect(url_for("index"))


@app.route("/types/add", methods=['POST'])
def types_add():
    if session.get('role') >= gr.ROLE_SUPERVISOR:
        n = request.form['name']
        if 0 < len(n) < STR_LEN:
            gr.add_type(n)
        else:
            flash("Заполните форму")
    return redirect(url_for("types"))


@app.route("/types/rm/<int:id>")
def types_rm(id):
    if session.get('role') >= gr.ROLE_SUPERVISOR:
        gr.rm_type(id)
    return redirect(url_for("types"))


@app.route("/cleanings")
def cleanings():
    if session.get('role') >= gr.ROLE_SUPERVISOR:
        return render_template('cleanings.html', title="Типы химчисток", cs=gr.get_cleanings())
    else:
        flash("Недостаточно прав")
        return redirect(url_for("index"))


@app.route("/cleanings/add", methods=['POST'])
def cleanings_add():
    if session.get('role') >= gr.ROLE_SUPERVISOR:
        n = request.form['name']
        p = request.form['price']
        if 0 < len(n) < STR_LEN and 0 < len(p) < STR_LEN:
            p = int(p)
            if 0 < p < 10000:
                gr.add_cleaning(n, p)
            else:
                flash("Введите цену больше 0 или меньше 10000")
        else:
            flash("Заполните форму")
    return redirect(url_for("cleanings"))


@app.route("/cleanings/rm/<int:id>")
def cleanings_rm(id):
    if session.get('role') >= gr.ROLE_SUPERVISOR:
        gr.rm_cleaning(id)
    return redirect(url_for("cleanings"))


@app.route("/stats")
def stats():
    if session.get('role') >= gr.ROLE_SUPERVISOR:
        return render_template('stats.html', title="Статистика", ss=gr.get_stats())
    else:
        flash("Недостаточно прав")
        return redirect(url_for("index"))


@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/favicon.ico')
@app.route('/style.css')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='Ошибка'), 404
