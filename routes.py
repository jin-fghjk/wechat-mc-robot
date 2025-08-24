"""
Web路由定义
"""
from flask import render_template, request, jsonify
from flask_login import login_required

def init_routes(app, robot):
    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/groups')
    @login_required
    def groups_list():
        groups = robot.get_groups_list()
        return render_template('groups/list.html', groups=groups)

    @app.route('/top_list')
    @login_required
    def top_list():
        top_data = robot.get_top_list_data()
        return render_template('top_list.html', top_list=top_data)

    @app.route('/settings/<group_id>', methods=['GET', 'POST'])
    @login_required
    def group_settings(group_id):
        if request.method == 'POST':
            settings = request.form.to_dict()
            success = robot.update_group_settings(group_id, settings)
            return jsonify({"success": success})

        return render_template('groups/settings.html', group_id=group_id)