from flask import Blueprint, render_template, flash, url_for, redirect, current_app
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import StringField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Length, URL
import urllib.request
from .db import Rickroll, db
from random import randrange
from slugify import slugify

bp = Blueprint('core', __name__)


class CreateRickrollForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[
            DataRequired("You need to provide a title"),
            Length(max=64, message="Title can't be longer than 64 characters")
        ])
    imgurl = URLField(
        'Preview image URL',
        validators=[
            DataRequired("You need to provide a preview image"),
            URL("The image URL doesn't seem valid..."),
            Length(
                max=1024,
                message=
                "The image URL is too long, please find a different image")
        ])
    redirecturl = URLField(
        'Redirect to',
        validators=[
            DataRequired(
                "You need to provide a URL to redirect to, use the buttons for inspiration"
            ),
            URL("The redirect URL doesn't seem valid..."),
            Length(
                max=1024,
                message=
                "The redirect URL is too long, please user different target or a URL shortener like bit.ly"
            )
        ])

    def validate_imgurl(_, field):
        ok = False
        try:
            if urllib.request.urlopen(
                    urllib.request.Request(
                        field.data,
                        headers={
                            "Accept":
                            "*/*",
                            "User-Agent":
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
                        },
                        method="HEAD")).info()["content-type"] in ("image/png",
                                                                   "image/jpeg",
                                                                   "image/gif"):
                ok = True
        finally:
            if not ok:
                raise ValidationError(
                    "The URL you provided doesn't seem to point to an image...")


@bp.route('/', methods=("GET", "POST"))
def home():
    form = CreateRickrollForm()
    if form.validate_on_submit():
        url = slugify(
            form.title.data, max_length=48, word_boundary=True,
            save_order=True) + "-" + str(randrange(10000, 100000))
        rr = Rickroll(
            title=form.title.data,
            imgurl=form.imgurl.data,
            url=url,
            redirecturl=form.redirecturl.data)
        db.session.add(rr)
        db.session.commit()
        flash(
            'Rickroll created, send this url to the fellas: <a href="{0}">{0}</a>'
            .format("https://newsfeedmerge.herokuapp.com" +
                    url_for(".roll", url=url)))
        return redirect(url_for(".ok"))
    else:
        for field in form.errors.values():
            for e in field:
                flash(e)
    return render_template(
        "create.html",
        form=form,
        rickrolls=current_app.config.get('RICKROLL_URLS', None))


@bp.route('/ok')
def ok():
    return render_template("ok.html")


@bp.route('/BBC/<url>')
def roll(url):
    try:
        fn = Rickroll.query.filter_by(url=url).first()
        return render_template(
            "roll.html",
            title=fn.title,
            url=url,
            imgurl=fn.imgurl,
            redirecturl=fn.redirecturl)
    except:
        return '<!doctype html><html><head><title>Oopsie</title></head><body><p>Oopsie... Someone tried to rickroll you, but either him, or this application, fucked up. However, you can <a href="/">create your own rickroll</a>.</p></body></html>'
