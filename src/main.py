# -*- coding: utf-8 -*-

from datetime import datetime, tzinfo, timedelta
import io
import csv
from google.cloud import datastore
from google.cloud.datastore.entity import Entity
from flask import Flask, jsonify, request, render_template, make_response

app = Flask(__name__)
datastore_client = datastore.Client()

class JST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=9)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return 'JST'

tz = JST()

# フォームアクセス

def getText(form, name):
    value = None
    if name in form:
        value = form[name]
    return value

def getBool(form, name):
    value = None
    if name in form:
        if form[name] == 'true':
            value = True
        else:
            value = False
    return value

# データ型

class Meeting:
    id = None
    title = None
    password = None
    detail_url = None
    accept_entry = None
    accept_search = None

class Attendance:
    id = None
    name1 = None
    name2 = None
    group1 = None
    group2 = None
    email = None
    attendance1 = None
    attendance2 = None
    anonymous = None
    message = None
    zip1 = None
    zip2 = None
    address = None
    tel = None
    fax = None
    office = None
    officetel = None
    created = None
    updated = None
    
    def match(self, conditions):
        result = True
        for c in conditions:
            if not (not self.anonymous and self.name1 and (c in self.name1) or \
                    not self.anonymous and self.name2 and (c in self.name2) or \
                    self.group1 and (c in self.group1) or \
                    self.group2 and (c in self.group2)):
                result = False
        return result


# データアクセス
# TODO: memcache 対応

def get_meeting(meeting_id):
    query = datastore_client.query(kind='meeting')
    key = datastore_client.key('meeting', meeting_id)
    query.key_filter(key)
    meetings = list(query.fetch())
    meeting = None
    if len(meetings) == 1:
        meeting = Meeting()
        m_src = meetings[0]
        meeting.id = m_src.key.name
        if 'title' in m_src:
            meeting.title = m_src['title']
        if 'password' in m_src:
            meeting.password = m_src['password']
        if 'detail_url' in m_src:
            meeting.detail_url = m_src['detail_url']
        if 'accept_entry' in m_src:
            meeting.accept_entry = m_src['accept_entry']
        if 'accept_search' in m_src:
            meeting.accept_search = m_src['accept_search']
    return meeting

def get_attendances(meeting):
    meeting_key = datastore_client.key('meeting', meeting.id)
    query = datastore_client.query(kind='attendance', ancestor=meeting_key)
    attendances = []
    for a_src in (query.fetch()):
        a = Attendance()
        a.id = a_src.key.id
        if 'name1' in a_src:
            a.name1 = a_src['name1']
        if 'name2' in a_src:
            a.name2 = a_src['name2']
        if 'group1' in a_src:
            a.group1 = a_src['group1']
        if 'group2' in a_src:
            a.group2 = a_src['group2']
        if 'email' in a_src:
            a.email = a_src['email']
        if 'attendance1' in a_src:
            a.attendance1 = a_src['attendance1']
        if 'attendance2' in a_src:
            a.attendance2 = a_src['attendance2']
        if 'anonymous' in a_src:
            a.anonymous = a_src['anonymous']
        if 'message' in a_src:
            a.message = a_src['message']
        if 'zip1' in a_src:
            a.zip1 = a_src['zip1']
        if 'zip2' in a_src:
            a.zip2 = a_src['zip2']
        if 'address' in a_src:
            a.address = a_src['address']
        if 'tel' in a_src:
            a.tel = a_src['tel']
        if 'fax' in a_src:
            a.fax = a_src['fax']
        if 'office' in a_src:
            a.office = a_src['office']
        if 'officetel' in a_src:
            a.officetel = a_src['officetel']
        if 'created' in a_src:
            a.created = a_src['created'].astimezone(tz)
        if 'updated' in a_src:
            a.updated = a_src['updated'].astimezone(tz)
        attendances.append(a)
    return attendances

def put_attendance(meeting, attendance):
    exkeys = ['name1', 'name2', 'group1', 'group2', 'email',
              'attendance1', 'attendance2', 'anonymous', 'message',
              'zip1', 'zip2', 'address', 'tel', 'fax', 'office', 'officetel',
              'created', 'updated']
    key = None
    if not attendance.id:
        key = datastore_client.key('meeting', meeting.id, 'attendance')
    else:
        key = datastore_client.key('meeting', meeting.id, 'attendance', attendance.id)
    entity = Entity(key=key, exclude_from_indexes=exkeys)
    entity['name1'] = attendance.name1
    entity['name2'] = attendance.name2
    entity['group1'] = attendance.group1
    entity['group2'] = attendance.group2
    entity['email'] = attendance.email
    entity['attendance1'] = attendance.attendance1
    entity['attendance2'] = attendance.attendance2
    entity['anonymous'] = attendance.anonymous
    entity['message'] = attendance.message
    entity['zip1'] = attendance.zip1
    entity['zip2'] = attendance.zip2
    entity['address'] = attendance.address
    entity['tel'] = attendance.tel
    entity['fax'] = attendance.fax
    entity['office'] = attendance.office
    entity['officetel'] = attendance.officetel
    entity['created'] = attendance.created
    entity['updated'] = attendance.updated
    datastore_client.put(entity)


# パスワード認証

def passwd_auth(meeting, req):
    if not meeting.password:
        return True
    password = req.cookies.get('password')
    if not password or password != meeting.password:
        return False
    return True

# ページ表示

@app.route('/<meeting_id>/')
def meeting_top(meeting_id):
    meeting = get_meeting(meeting_id)
    if not meeting:
        return render_template('meeting_not_found.html', meeting_id = meeting_id), 404
    if not passwd_auth(meeting, request):
        return render_template('password_required.html', meeting = meeting)
    return render_template('meeting.html', meeting=meeting)

@app.route('/<meeting_id>/entry/', methods=['POST'])
def meeting_entry(meeting_id):
    meeting = get_meeting(meeting_id)
    if not meeting:
        return render_template('meeting_not_found.html', meeting_id = meeting_id), 404
    if not meeting.accept_entry:
        return make_response('ただいま参加申込は受け付けておりません', 403)
    input_errors = []
    attendance = Attendance()
    form = request.form
    attendance.name1 = getText(form, 'name1')
    attendance.name2 = getText(form, 'name2')
    attendance.group1 = getText(form, 'group1')
    attendance.group2 = getText(form, 'group2')
    attendance.email = getText(form, 'email')
    attendance.attendance1 = getBool(form, 'attendance1')
    attendance.attendance2 = getBool(form, 'attendance2')
    attendance.anonymous = getBool(form, 'anonymous')
    attendance.message = getText(form, 'message')
    attendance.zip1 = getText(form, 'zip1')
    attendance.zip2 = getText(form, 'zip2')
    attendance.address = getText(form, 'address')
    attendance.tel = getText(form, 'tel')
    attendance.fax = getText(form, 'fax')
    attendance.office = getText(form, 'office')
    attendance.officetel = getText(form, 'officetel')
    attendance.created = datetime.now(tz)
    attendance.updated = attendance.created
    
    # 入力チェック
    if not attendance.name1:
        input_errors.append(('name1', 'お名前は必須です'))
    if not attendance.group1:
        input_errors.append(('group1', '在籍回生は必須です'))
    if attendance.attendance1 is None:
        input_errors.append(('attendance1', '総会・懇親会出欠は必須です'))
    if attendance.attendance2 is None:
        input_errors.append(('attendance2', '二次会出欠は必須です'))
    if attendance.anonymous is None:
        input_errors.append(('anonymous', '出欠の公開は必須です'))
    if len(input_errors):
        return make_response(jsonify({'input_errors': input_errors}), 403)
    
    put_attendance(meeting, attendance)
    return make_response('登録完了しました', 200)

@app.route('/<meeting_id>/search/')
def meeting_search(meeting_id):
    meeting = get_meeting(meeting_id)
    if not meeting:
        return make_response('', 404)
    if not meeting.accept_search:
        return make_response('ただいま参加者検索は受け付けておりません', 403)
    if not 'condition' in request.args.keys() or not request.args['condition']:
        return make_response('検索条件を入力してください', 403)
    conditions = request.args['condition'].split()
    attendances_out = []
    attendances = get_attendances(meeting)
    for a in attendances:
        if a.match(conditions):
            aout = {}
            if not a.anonymous:
                aout['name1'] = a.name1
                aout['name2'] = a.name2
            aout['group1'] = a.group1
            aout['group2'] = a.group2
            aout['attendance1'] = a.attendance1
            aout['attendance2'] = a.attendance2
            attendances_out.append(aout)
    return jsonify(attendances_out)

@app.route('/<meeting_id>/admin/export/')
def meeting_admin_export(meeting_id):
    # TODO: 権限制御
    meeting = get_meeting(meeting_id)
    if not meeting:
        return make_response('', 404)
    
    datetimefmt = '%Y/%m/%d %H:%M:%S'
    with io.StringIO() as f:
        w = csv.writer(f)
        w.writerow(['name1', 'name2', 'group1', 'group2', 'email', 'attendance1', 'attendance2', 'anonymous',
                    'zip1', 'zip2', 'address', 'tel', 'fax', 'office', 'officetel',
                    'created', 'updated'])
        
        attendances = get_attendances(meeting)
        for a in attendances:
            w.writerow([a.name1, a.name2, a.group1, a.group2, a.email, str(a.attendance1), str(a.attendance2), str(a.anonymous),
                        a.zip1, a.zip2, a.address, a.tel, a.fax, a.office, a.officetel,
                        a.created.strftime(datetimefmt), a.updated.strftime(datetimefmt)])
        
        res = make_response()
        res.headers['Content-Type'] = 'application/octet-stream'
        res.headers['Content-Disposition'] = u'attachment; filename=attendance.csv'
        res.data = f.getvalue().encode('MS932')
        return res

@app.route('/<meeting_id>/login/', methods=['POST'])
def login(meeting_id):
    meeting = get_meeting(meeting_id)
    if not meeting:
        return make_response('', 404)
    password = request.form['password']
    if password != meeting.password:
        return make_response('パスワードが一致しません', 403)
    resp = make_response('ログインに成功しました', 200)
    resp.set_cookie(key='password', value=password, path=('/%s/' % (meeting_id)), secure=request.is_secure)
    return resp

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
