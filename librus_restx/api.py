from flask import Flask, request, jsonify, make_response, request
from flask_restx import Api, Resource, fields, reqparse
from librus_apix.exceptions import AuthorizationError, TokenError
from librus_apix.get_token import get_token, Token
from librus_apix.messages import get_recieved, message_content
from librus_apix.grades import get_grades
from librus_apix.attendance import get_attendance, get_detail
from librus_apix.schedule import get_schedule, schedule_detail
from librus_apix.timetable import get_timetable
from datetime import datetime
from librus_apix.announcements import get_announcements
from librus_apix.homework import get_homework, homework_detail

app = Flask(__name__)
api = Api(app)

model = api.model('Login', {
    'username': fields.String,
    'password': fields.String
})

#def header_to_token(auth_header: str):
#    token = Token(request.headers.get(auth_header))

def dictify(_list: list):
    return [val.__dict__ for val in _list]

@api.route('/login')
class Login(Resource):
    @api.doc(body=model)
    def post(self):
        try:
            token = get_token(api.payload['username'], api.payload['password'])
            return {"X-API-Key": token.API_Key}, 200
        except KeyError:
            return {"error": "Provide a proper Authorization header"}, 401
        except AuthorizationError as AuthError:
            return {"error": str(AuthError)}, 401
        
@api.route('/messages/<int:page>')
class Message(Resource):
    @api.header("X-API-Key", type=[str])
    def get(self, page):
        try:
            token = Token(request.headers.get("X-API-Key"))
            msgs = dictify(get_recieved(token, page))
        except TokenError() as tokenErr:
            msgs = {'error': tokenErr}
        return msgs
@api.route('/messages/content/<string:content_url>')
class MessageContent(Resource):
    def get(self, content_url: str):
        try:
            token = Token(request.headers.get("X-API-Key"))
            content = message_content(token, content_url)
        except TokenError() as tokenErr:
            content = {'error': tokenErr}
        return content
@api.route('/grades/<int:semester>')
class Grades(Resource):
    def get(self, semester: int):
        def to_dict(obj):
            initial = obj.__dict__
            initial.update({"value": obj.value})
            return initial
        try:
            token = Token(request.headers.get("X-API-KEY"))
            g = get_grades(token)
            grades = {}
            for subject in g[semester]:
                grades[subject] = list(map(to_dict, g[semester][subject]))

        except TokenError() as tokenErr:
           grades = {'error': tokenErr}
        
        return grades
@api.route('/attendance/<int:semester>')
class Attendance(Resource):
    def get(self, semester: int):
        try:
            token = Token(request.headers.get("X-API-KEY"))
            attendance = dictify(get_attendance(token)[semester])
        except TokenError() as tokenErr:
           attendance = {'error': tokenErr}
        return attendance
@api.route('/attendance/details/<string:detail_url>')
class AttendanceDetail(Resource):
    def get(self, detail_url: str):
        try:
            token = Token(request.headers.get("X-API-KEY"))
            detail = get_detail(token, detail_url)
        except TokenError() as tokenErr:
            detail = {'error': tokenErr}
        return detail
@api.route('/schedule/<string:year>/<string:month>')
class Schedule(Resource):
    def get(self, year: str, month: str):
        try:
            token = Token(request.headers.get("X-API-KEY"))
            schedule = dictify(get_schedule(token, month, year))
        except TokenError() as tokenErr:
            schedule = {'error': tokenErr}
        return schedule
@api.route('/schedule/details/<string:detail_prefix>/<string:detail_url>')
class ScheduleDetail(Resource):
    def get(self, detail_prefix: str, detail_url: str):
        try:
            token = Token(request.headers.get("X-API-KEY"))
            details = schedule_detail(token, detail_prefix, detail_url)
        except TokenError() as tokenErr:
            details = {'error': tokenErr}
        return details
@api.route('/timetable/<string:monday_date>')
class Timetable(Resource):
    def get(self, monday_date: str):
        try:
            token = Token(request.headers.get("X-API-KEY"))
            timetable = get_timetable(token, datetime.strptime(monday_date, '%Y-%m-%d'))
        except TokenError() as tokenErr:
            timetable = {'error': tokenErr}
        return timetable
@api.route('/announcements')
class Announcements(Resource):
    def get(self):
        try:
            token = Token(request.headers.get("X-API-KEY"))
            announcements = dictify(get_announcements(token))
        except TokenError() as tokenErr:
            announcements = {'error': tokenErr}
        return announcements
@api.route('/homework/details/<string:detail_url>')
class HomeworkDetails(Resource):
    def get(self, detail_url: str):
        try:
            token = Token(request.headers.get("X-API-KEY"))
            details = homework_detail(token, detail_url)
        except TokenError() as tokenErr:
            details = {'error': tokenErr}
        return details
@api.route('/homework/<string:date_from>/<string:date_to>')
class Homework(Resource):
    def get(self, date_from: str, date_to: str):
        try:
            token = Token(request.headers.get("X-API-KEY"))
            homework = dictify(get_homework(token, date_from, date_to))
        except TokenError() as tokenErr:
            homework = {'error': tokenErr}
        return homework

if __name__ == '__main__':
    app.run(debug=True)