# encoding:utf-8
import requests
import logging
import json

from flask import Flask, jsonify, render_template, g, url_for, redirect, request, session, abort
from flask.ext.babel import gettext, ngettext
from sqlalchemy import and_, desc
from sqlalchemy.sql import func

from meta import app as application, db, db_session, engine, LANGUAGE
from models import User, Association, MostViewedQuestion, Action
from suggested_question import get_suggested_question_ids_with_views, get_suggested_question_pagination
from local_settings import STACKEXCHANGE_CLIENT_SECRET, STACKEXCHANGE_CLIENT_ID, STACKEXCHANGE_CLIENT_KEY

STACKEXCHANGE_ADD_COMMENT_ENDPOINT = "https://api.stackexchange.com/2.2/posts/{id}/comments/add"
STACKEXCHANGE_ANSWER_API_ENDPOINT = "https://api.stackexchange.com/2.2/answers/{id}/?";

@application.before_request
def before_request():
    g.user = None
    if 'account_id' in session:
        g.user = User.query.filter_by(account_id=session['account_id']).first()
        
@application.after_request
def after_request(response):
    db_session.close()
    db_session.remove()
    engine.dispose()

    return response    

@application.route("/index.html")
@application.route("/")
def index():
    if g.user is None:
        return redirect(url_for('welcome'))  
    page = max(int(request.args.get("page", "1")), 1)
    paginator = get_suggested_question_pagination(page)
    return render_template('question_pag_list.html', paginator=paginator, base_url=url_for("index"))

@application.route("/no-way")
@application.route("/no-way/")
def no_way():
    return render_template('no_way.html')    

@application.route("/welcome")
@application.route("/welcome/")
def welcome():
    return render_template('welcome.html', language=LANGUAGE)    

@application.route("/questions/<question_id>")
@application.route("/questions/<question_id>/")
def question(question_id):
    if g.user is None:
        return redirect(url_for('welcome'))
    q = MostViewedQuestion.query.filter(and_(MostViewedQuestion.is_associated==False, MostViewedQuestion.question_id==question_id)).first()
    
    if q is None:
        abort(404)
    skip = Action.query.filter(and_(Action.user_id==g.user.id, 
        Action.most_viewed_question_id==q.id, 
        Action.action_name==Action.action_skip_name, 
        Action.canceled==False)).first()
    translate_request = Action.query.filter(and_(Action.user_id==g.user.id, 
        Action.most_viewed_question_id==q.id, 
        Action.action_name==Action.action_translate_request_name, 
        Action.canceled==False)).first()
    translate_request_count = db.session.query(func.count(Action.id)).filter(and_(Action.most_viewed_question_id==q.id,
        Action.action_name==Action.action_translate_request_name, 
        Action.canceled==False)).scalar()

    return render_template('question.html', 
        question_id=q.question_id, 
        question_views=q.view_count, 
        skip=skip,
        translate_request=translate_request,
        translate_request_count=translate_request_count)    

@application.route("/api/suggested_question_ids_with_views")
def suggested_question_ids_with_views():
    ids = get_suggested_question_ids_with_views()
    return jsonify(**ids)    

@application.route("/api/add_association")
@application.route("/api/add_association/")
def add_association():
    access_token = session.get("access_token", None)
    if g.user is None or access_token is None:
        abort(404)

    soen_id = -1
    soint_id = -1

    try:
        soen_id = int(request.args.get("soen_id"))
        soint_id = int(request.args.get("soint_id"))
    except:
        abort(404)
    
    count = Association.query.filter_by(soen_id=soen_id).count()
    if count > 0:
        # TODO add something better then 404
        abort(404)

    url = STACKEXCHANGE_ADD_COMMENT_ENDPOINT.replace("{id}", str(soint_id))
    association_tag = gettext(u"association")
    params = {
       "body" : association_tag + u": http://stackoverflow.com/questions/" + str(soen_id) + "/",
       "access_token": access_token,
       "key": STACKEXCHANGE_CLIENT_KEY,
       "site": "ru.stackoverflow",
       "preview": "false"
    }
    
    r = requests.post(url, data=params) 
    comment_id = -1
    data = json.loads(r.text)
    if data.get("items", None) is not None:
        for item in data["items"]:
            if item.get("comment_id", None) is not None:
                comment_id = item["comment_id"]
                break
    resp = {
        "comment_id": comment_id,
        "full_response": r.text
    }

    association = Association(g.user.id, soen_id, soint_id, comment_id)
    db_session.add(association)
    db_session.commit()

    questions = MostViewedQuestion.query.filter_by(question_id=soen_id).all()
    # There should be only one
    for question in questions:
        question.is_associated = True
    db.session.commit()

    return jsonify(**resp)

@application.route("/api/get-answers")
@application.route("/api/get-answers/")
def get_answers():
    access_token = session.get("access_token", None)
    if g.user is None or access_token is None:
        abort(404)

    ids = request.args.get("ids", None)
    site = request.args.get("site", None)

    if ids is None or site is None:
        abort(404)

    url = STACKEXCHANGE_ANSWER_API_ENDPOINT.replace("{id}", ids)
    params = {
       "access_token": access_token,
       "key": STACKEXCHANGE_CLIENT_KEY,
       "site": site,
       "order": "desc",
       "sort": "votes",
       "filter": "!)s4ZC4Cto10(q(Yp)zK*"
    }    
    r = requests.get(url, data=params) 
    data = json.loads(r.text)
    return jsonify(**data)    


def do_action_helper(action_name):
    if g.user is None:
        abort(404)

    soen_id = -1
    try:
        soen_id = int(request.args.get("soen_id"))
    except:
        abort(404)
    
    question = MostViewedQuestion.query.filter_by(question_id=soen_id).first()
    if question is None:
        abort(404)
        
    action = Action.query.filter(and_(Action.user_id==g.user.id, Action.most_viewed_question_id==question.id, Action.action_name==action_name)).first()
    if action is not None:
        action.canceled = not action.canceled
        db.session.commit()
    else:
        action = Action(g.user.id, question.id, action_name)
        db_session.add(action)
        db_session.commit()

    resp = {
        "status": action.canceled
    }

    return jsonify(**resp)    

@application.route("/api/skip_most_viewed_question")
@application.route("/api/skip_most_viewed_question/")
def skip_most_viewed_question():
    return do_action_helper(Action.action_skip_name)

@application.route("/api/translation_request")
@application.route("/api/translation_request/")
def translation_request():
    return do_action_helper(Action.action_translate_request_name)