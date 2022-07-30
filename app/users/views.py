from app.users import bp_users
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from flask import render_template, redirect, url_for, flash, request
from app import db
from app.models import User, Chats, Message
from flask_socketio import SocketIO, send, emit, join_room, leave_room, \
    Namespace, disconnect
from app import socketio
import datetime
import os, time
import json

@bp_users.route('/my-profile')
def profile():
    return render_template('users/profile.html')


@bp_users.route('/new_chat', methods=["POST"])
def new_chat():
    user_id=current_user.id
    new_chat=request.form['username']

    if new_chat == current_user.username:
        flash('You can\'t add yourself!')
        return redirect(url_for("users.chat"))


    new_contact = User.query.filter_by(username=new_chat).first()
    if new_contact is None:
        flash('User not Found!')
        return redirect(url_for("users.chat"))
    # get chats for both users

    chats = Chats.query.filter_by(user_id=user_id).all()
    recipient_chats=Chats.query.filter_by(user_id=new_contact.id).all()


     # Check if the chat the users is trying to add has not been added before

    contacts=[]
    for item in chats:
        contacts.append(item.contact_id)

    if new_contact.id not in contacts:
        room_id = str(int(new_contact.id) + int(user_id))[-4:]
        contact=Chats(user_id=user_id, room_id=room_id, contact_id=new_contact.id)
        db.session.add(contact)
        db.session.commit()

        sender=Chats(user_id=new_contact.id, room_id=room_id, contact_id=user_id)
        db.session.add(sender)
        db.session.commit()

        flash('Chat added Successfully!')

    return redirect(url_for("users.chat"))

@bp_users.route('/chat/',methods=["GET", "POST"])
def chat():

    current_user.last_message_notification_time = datetime.datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()


    room_id = request.args.get("rid", None)

    data = []

    contacts = Chats.query.filter_by(user_id=current_user.id).order_by(Chats.timestamp.desc()).all()

    for i in contacts:
        user = User.query.filter_by(id=i.contact_id).first()
        username = user.username

        is_active = False

        if room_id == i.room_id:
            is_active = True


        messages = Message.query.filter_by(room_link=i.room_id).all()
        if len(messages) == 0:
            last_message="No messages..."
        else:
            m_message = messages[-1]
            last_message=m_message.body

        last_time = user.last_message_unread_time or datetime.datetime(1900, 1, 1)

        # unread_count = Message.query.filter_by(recipient_id=current_user.id, sender_id=user.id).filter(
        #     Message.timestamp > last_time).count()
        unread_count=0
        data.append({
            "user": user,
            "room_id": i.room_id,
            "is_active": is_active,
            "last_message": last_message,
            "unread_count": unread_count,
        })

    return render_template('users/chats.html', user=current_user, room_id=room_id, data=data)

@bp_users.route('/chatting/', methods=["GET", "POST"])
def chatting():

    room_id = request.args.get("rid", None)

    current_user.last_message_unread_time = datetime.datetime.utcnow()
    current_user.add_notification(room_id, 0)
    db.session.commit()


    contact = Chats.query.filter_by(user_id=current_user.id, room_id=room_id).first()

    if contact is not None:
        global recipient
        recipient= User.query.filter_by(id=contact.contact_id).first()
        contact.unread=datetime.datetime.utcnow()
        db.session.commit()

    messages=[]
    if room_id != None:
            messages = Message.query.filter_by(room_link=room_id).all()

    return render_template('users/chatting.html', user=current_user, room_id=room_id, messages=messages, recipient=recipient)

# @bp_users.template_filter("ftime")
# def ftime(date):
#     return datetime.fromtimestamp(int(date)).strftime("%m.%d. %H:%M")

@socketio.on("join-chat")
def join_private_chat(data):
    room = data["rid"]
    join_room(room=room)
    socketio.emit(
        "joined-chat",
        {"msg": f"{room} is now online."},
        room=room,
        # include_self=False,
    )

@socketio.on("outgoing")
def chatting_event(json, methods=["GET", "POST"]):
    room_id = json["rid"]
    timestamp=datetime.datetime.fromtimestamp(json["timestamp"]/1000.0, tz=datetime.timezone.utc)
    message = json["message"]
    sender_id = json["sender_id"]
    sender_username = json["sender_username"]


    chat= Chats.query.filter_by(room_id=room_id, user_id=sender_id).first_or_404()
    recipient_id = chat.contact_id


    new_message = Message(room_link=room_id, timestamp=timestamp,
    body=message, sender_id=sender_id, sender_username=sender_username, recipient_id=recipient_id)

    print(new_message)
    print(recipient_id)
    print(sender_username)

    db.session.add(new_message)
    db.session.commit()

    recipient= User.query.filter_by(id=recipient_id).first()
    recipient.add_notification('unread_message_count', recipient.new_messages_notification())
    recipient.add_notification(room_id, recipient.new_messages_unread())
    db.session.commit()


    socketio.emit(
        "message",
        json,
        room=room_id,
        timestamp=timestamp,
        include_self=False,
    )

