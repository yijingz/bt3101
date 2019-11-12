# -*- encoding: utf-8 -*-
"""
Material Dashboard - coded in Flask
Author: AppSeed.us - App Generator 
"""

# all the imports necessary
from flask import json, url_for, redirect, render_template, flash, g, session, jsonify, request, send_from_directory, render_template_string
from werkzeug.exceptions import HTTPException, NotFound, abort

import os

from app  import app

from flask       import url_for, redirect, render_template, flash, g, session, jsonify, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from app         import app, lm, db, bc
from . models    import User
from . common    import COMMON, STATUS
from . assets    import *
from . forms     import LoginForm, RegisterForm

import os, shutil, re, cgi
        
# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# authenticate user
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('index'))

# register user
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    
    # define login form here
    form = RegisterForm(request.form)

    msg = None

    # custommize your pate title / description here
    page_title       = 'Register - Flask Material Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Material Dashboard, registration page.'

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        name     = request.form.get('name'    , '', type=str) 
        email    = request.form.get('email'   , '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'
        
        else:                    
            pw_hash = bc.generate_password_hash(password)

            user = User(username, pw_hash, name, email)

            user.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'     

    # try to match the pages defined in -> /pages/
    return render_template( 'layouts/default.html',
                            title=page_title,
                            content=render_template( 'pages/register.html', form=form, msg=msg) )

# authenticate user
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    
    # define login form here
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # custommize your page title / description here
    page_title = 'Login - Flask Material Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Material Dashboard, login page.'

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        if user:
            
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unkkown user"

    # try to match the pages defined in -> themes/light-bootstrap/pages/
    return render_template( 'layouts/default.html',
                            title=page_title,
                            content=render_template( 'pages/login.html', 
                                                     form=form,
                                                     msg=msg) )

# Used only for static export
@app.route('/icons.html')
def icons():

    # custommize your page title / description here
    page_title = 'Icons - Flask Material Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Material Dashboard, the icons page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/icons.html') )

# Used only for static export
@app.route('/notifications.html')
def notifications():

    # custommize your page title / description here
    page_title = 'Notifications - Flask Material Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Material Dashboard, the notifications page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/notifications.html') )

# Used only for static export
@app.route('/user.html')
def user():

    # custommize your page title / description here
    page_title = 'Profile - Flask Material Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Material Dashboard, the profile page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/user.html') )

# Used only for static export
@app.route('/tables.html')
def table():

    # custommize your page title / description here
    page_title = 'Tables - Flask Material Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Material Dashboard, the tables page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/tables.html') )

# Used only for static export
@app.route('/typography.html')
def typography():

    # custommize your page title / description here
    page_title = 'Typography - Flask Material Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Material Dashboard, the tables page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/typography.html') )

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    content = None

    try:

        # try to match the pages defined in -> themes/light-bootstrap/pages/
        return render_template('layouts/default.html',
                                content=render_template( 'pages/'+path) )
    except:
        abort(404)

@app.route('/hsi')
def stock_display_page():
    from os import listdir
    from os.path import isfile, join

    path = '/Users/miazhang/flask-material-dashboard/app/data'
    stock_files = [f for f in listdir(path) if isfile(join(path, f))]
    stock_files_without_csv = list(map(lambda x: x[:-4], stock_files))
    return render_template('layouts/default.html',
                           content=render_template('pages/stocks_display_page.html', lst=stock_files_without_csv))




@app.route('/hsi/<comp>')
def stock_page(comp):
    from app import stock_analysis as sa
    from app import company_profile as cp
    import math
    company = cp.get_company_name(comp)
    company_name = company[0]
    industry = company[1]

    profile_dic = cp.get_historical_price_summary(comp)

    data = sa.preprocess_data(comp)
    gjson = sa.get_tempo_buying_chart(data)


    from app import sales_volume as sv
    parameter_dic = sv.get_alpha_delta_adtv(comp, 0)
    extra_dic = sv.get_sig_gamma_eta(comp)

    def myround(n):
        if n == 0:
            return 0
        sgn = -1 if n < 0 else 1
        scale = int(-math.floor(math.log10(abs(n))))
        if scale <= 0:
            scale = 1
        factor = 10 ** scale
        return sgn * math.floor(abs(n) * factor) / factor

    for par in extra_dic:
        val = myround(extra_dic[par])
        extra_dic[par] = val


    return render_template('layouts/default.html',
                                content=render_template('pages/' + 'index.html', comp=comp, graphJSON=gjson, company_name=company_name, industry=industry, profile_dic=profile_dic,
                                                        parameter_dic=parameter_dic, extra_dic=extra_dic))


@app.route('/show_history')
def show_history():
    from app import stock_analysis as sa

    text = request.args.get('jsdata')
    linejson = sa.get_historical_chart(text)

    return render_template('pages/historical_chart.html', linejson=linejson)

global num
global days
global spread

global optimal_cost
global sig_gamma_eta_dic
global x

@app.route('/get_num_shares', methods=['GET', 'POST'])
def get_num_shares():

    if request.method == 'GET':
        from app import sales_volume as sv
        import pickle


        text = request.args.get('jsdata')
        num = int(request.args.get('num'))
        lamb = request.args.get('lamb')
        days = request.args.get('days')
        spread = float(request.args.get('spread'))/100


        output_dic = sv.get_alpha_delta_adtv(text, num)

        if not lamb:
            lamb = 10**(-6)
        if not days:
            days = output_dic['days']

        stock_output_dic = {}
        stock_output_dic['num'] = num
        stock_output_dic['lamb'] = lamb
        stock_output_dic['days'] = days


        sig_gamma_eta_dic = sv.get_sig_gamma_eta(text)

        x = sv.get_trajectory(lamb, sig_gamma_eta_dic['sigma'], sig_gamma_eta_dic['gamma'], sig_gamma_eta_dic['eta'], int(num), days)
        sales_df = sv.get_optimal_sales_df(x, int(num), days)

        optimal_cost = sv.get_optimal_cost(x, sig_gamma_eta_dic['gamma'], num, spread, sig_gamma_eta_dic['eta'])

        daily_sales_dic = sv.get_daily_sales_dic(sales_df)
        barjson = sv.get_sales_chart(sales_df)
        position_bar_json = sv.get_position_chart(sales_df)

        delta_lst = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1]
        add_cost_lst = []
        for delta in delta_lst:
            cost = sv.get_additional_cost(delta, x,  sig_gamma_eta_dic['gamma'], num, sig_gamma_eta_dic['eta'], spread, optimal_cost)
            add_cost_lst.append(cost)

        params = {}
        params['num'] = num
        params['days'] = days
        params['spread'] = spread
        params['optimal_cost'] = optimal_cost
        params['sig_gamma_eta_dic'] = sig_gamma_eta_dic
        params['x'] = x

        with open('params.pickle', 'wb') as handle:
            pickle.dump(params, handle, protocol=pickle.HIGHEST_PROTOCOL)


        return render_template('pages/sales_volume.html', output_dic=stock_output_dic, optimal_cost=optimal_cost,
                               delta_lst=delta_lst, delta_cost=add_cost_lst,
                               daily_dic=daily_sales_dic,barjson=barjson, position_barjson=position_bar_json)

    elif request.method == 'POST':
        print('method is post')


@app.route('/get_additional_cost_traj', methods=['GET', 'POST'])
def get_additional_cost_traj():
    if request.method == 'GET':
        from app import sales_volume as sv
        import pickle

        delta_index = int(request.args.get('delta'))

        with open('params.pickle', 'rb') as handle:
            param = pickle.load(handle)

        delta_lst = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1]
        delta = delta_lst[delta_index]
        print('delta, ', delta)


        num = param['num']
        days = param['days']
        spread = param['spread']
        optimal_cost = param['optimal_cost']
        sig_gamma_eta_dic = param['sig_gamma_eta_dic']
        x = param['x']

        traj = sv.get_new_traj(delta, x, sig_gamma_eta_dic['gamma'], num, sig_gamma_eta_dic['eta'], spread, optimal_cost)
        new_x = traj[0]
        cost = traj[1]
        sales_df = sv.get_optimal_sales_df(new_x, num, days)
        daily_sales_dic_new = sv.get_daily_sales_dic(sales_df)
        barjson = sv.get_sales_chart(sales_df)
        position_bar_json = sv.get_position_chart(sales_df)

        return render_template('pages/additional_cost.html', daily_dic_new=daily_sales_dic_new, barjson=barjson, position_bar_json=position_bar_json, cost=cost)
      #  return render_template_string(str(delta))








#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(app.root_path, 'static'),
#                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

#@app.route('/sitemap.xml')
#def sitemap():
#    return send_from_directory(os.path.join(app.root_path, 'static'),
#                               'sitemap.xml')

# ------------------------------------------------------

# error handling
# most common error codes have been added for now
# TO DO:
# they could use some styling so they don't look so ugly

def http_err(err_code):
	
    err_msg = 'Oups !! Some internal error ocurred. Thanks to contact support.'
	
    if 400 == err_code:
        err_msg = "It seems like you are not allowed to access this link."

    elif 404 == err_code:    
        err_msg  = "The URL you were looking for does not seem to exist."
        err_msg += "<br /> Define the new page in /pages"
    
    elif 500 == err_code:    
        err_msg = "Internal error. Contact the manager about this."

    else:
        err_msg = "Forbidden access."

    return err_msg
    
@app.errorhandler(401)
def e401(e):
    return http_err( 401) # "It seems like you are not allowed to access this link."

@app.errorhandler(404)
def e404(e):
    return http_err( 404) # "The URL you were looking for does not seem to exist.<br><br>
	                      # If you have typed the link manually, make sure you've spelled the link right."

@app.errorhandler(500)
def e500(e):
    return http_err( 500) # "Internal error. Contact the manager about this."

@app.errorhandler(403)
def e403(e):
    return http_err( 403 ) # "Forbidden access."

@app.errorhandler(410)
def e410(e):
    return http_err( 410) # "The content you were looking for has been deleted."

	