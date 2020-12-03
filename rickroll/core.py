from flask import (
    Blueprint,
    render_template,
    flash,
    url_for,
    redirect,
    current_app,
    session,
    request,
    get_flashed_messages,
)
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import StringField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Length, URL
import urllib.request
from .db import Rickroll, db
from random import randrange
from slugify import slugify
from collections import defaultdict

bp = Blueprint("core", __name__)


@bp.app_template_global()
def get_grouped_flashes():
    msgs = get_flashed_messages(with_categories=True)
    groups = defaultdict(list)
    for group, msg in msgs:
        groups[group].append(msg)
    return groups


@bp.app_template_global()
def get_redirect_title(url):
    return next(
        (k for k, v in current_app.config.get("RICKROLL_URLS", {}).items() if v == url),
        url,
    )


class CreateRickrollForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired("You need to provide a title"),
            Length(max=64, message="Title can't be longer than 64 characters"),
        ],
    )
    imgurl = URLField(
        "Preview image URL",
        validators=[
            DataRequired("You need to provide a preview image"),
            URL("The image URL doesn't seem valid..."),
            Length(
                max=1024,
                message="The image URL is too long, please find a different image",
            ),
        ],
    )
    redirecturl = URLField(
        "Redirect to",
        validators=[
            DataRequired(
                "You need to provide a URL to redirect to, use the buttons for inspiration"
            ),
            URL("The redirect URL doesn't seem valid..."),
            Length(
                max=1024,
                message="The redirect URL is too long, please user different target or a URL shortener like bit.ly",
            ),
        ],
    )

    def validate_imgurl(_, field):
        ok = False
        try:
            if urllib.request.urlopen(
                urllib.request.Request(
                    field.data,
                    headers={
                        "Accept": "*/*",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
                    },
                    method="HEAD",
                )
            ).info()["content-type"] in ("image/png", "image/jpeg", "image/gif"):
                ok = True
        finally:
            if not ok:
                raise ValidationError(
                    "The URL you provided doesn't seem to point to an image..."
                )


@bp.route("/", methods=("GET", "POST"))
def home():
    form = CreateRickrollForm()
    if form.validate_on_submit():
        url = (
            slugify(form.title.data, max_length=48, word_boundary=True, save_order=True)
            + "-"
            + str(randrange(10000, 100000))
        )
        rr = Rickroll(
            title=form.title.data,
            imgurl=form.imgurl.data,
            url=url,
            redirecturl=form.redirecturl.data,
        )
        db.session.add(rr)
        db.session.commit()
        flash(
            'Rickroll created, send this url to the fellas:<br /><a href="{0}">{1}</a>'.format(
                url_for(".roll", url=url), url_for(".roll", url=url, _external=True)
            ),
            "#4bb543",
        )
        if "rickrolls" not in session:
            session["rickrolls"] = [url]
        else:
            session["rickrolls"].append(url)
            session.modified = True  # session change is not picked up automatically because a mutable object is changed
        session.permanent = True
        return redirect(url_for(".list_rickrolls"), 303)
    else:
        for field in form.errors.values():
            for e in field:
                flash(e, "#f99")
    return render_template(
        "create.html",
        form=form,
        rickrolls=current_app.config.get("RICKROLL_URLS", None),
    )


@bp.route("/list")
def list_rickrolls():
    return render_template(
        "list.html",
        rickrolls=[Rickroll.query.get(url) for url in session.get("rickrolls", [])],
    )


@bp.route("/delete", methods=("POST",))
def delete():
    db.session.delete(Rickroll.query.get(request.form["id"]))
    db.session.commit()
    flash("Deleted sucessfully", "#ff6700")
    session["rickrolls"].remove(request.form["id"])
    session.modified = True
    return redirect(url_for(".list_rickrolls"), 303)


@bp.route("/BBC/<url>")
def roll(url):
    try:
        fn = Rickroll.query.get(url)
        fn.rollcount += 1
        db.session.commit()
        return render_template(
            "roll.html",
            title=fn.title,
            url=url,
            imgurl=fn.imgurl,
            redirecturl=fn.redirecturl,
        )
    except:
        return '<!doctype html><html><head><title>Oopsie</title></head><body><p>Oopsie... Someone tried to rickroll you, but either him, or this application, fucked up. However, you can <a href="/">create your own rickroll</a>.</p></body></html>'
