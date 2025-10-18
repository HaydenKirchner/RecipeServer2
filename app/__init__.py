"""Application factory and Flask configuration helpers."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from config import config_by_name
from database import Base, get_tracked_test_engine
from .routes import api_bp
from .web import views_bp

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent

LOGGER = logging.getLogger(__name__)


def _ensure_extension_placeholders(app: Flask) -> None:
    """Initialise extension storage on the Flask app instance."""

    if not hasattr(app, "extensions"):
        app.extensions = {}

    app.extensions.setdefault("db_session_factory", None)
    app.extensions.setdefault("db_engine", None)
    app.extensions.setdefault("db_uri", None)


def _initialise_configuration(app: Flask, config_name: Optional[str]) -> None:
    """Load configuration and perform configuration specific initialisation."""

    config_name = (config_name or "default").lower()
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    initialise = getattr(config_class, "initialize", None)
    if callable(initialise):
        initialise()


def _reset_database_extensions(app: Flask) -> None:
    """Dispose of an existing engine and clear session factories."""

    engine = app.extensions.get("db_engine")
    if engine is not None:
        engine.dispose()

    app.extensions["db_engine"] = None
    app.extensions["db_session_factory"] = None
    app.extensions["db_uri"] = None


def _get_session_factory(app: Flask):
    """Return a scoped session factory for the current database URI."""

    target_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not target_uri:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is not configured")

    stored_uri = app.extensions.get("db_uri")
    session_factory = app.extensions.get("db_session_factory")

    if session_factory is None or stored_uri != target_uri:
        shared_engine = None
        if target_uri.startswith("sqlite:///:memory"):
            shared_engine = get_tracked_test_engine()

        if shared_engine is None:
            LOGGER.debug("Creating SQLAlchemy engine for %s", target_uri)
            if session_factory is not None:
                session_factory.remove()

            engine_kwargs = {"future": True}
            connect_args: dict[str, object] = {}

            if target_uri.startswith("sqlite"):
                connect_args["check_same_thread"] = False
                if target_uri.startswith("sqlite:///:memory"):
                    engine_kwargs["poolclass"] = StaticPool

            if connect_args:
                engine_kwargs["connect_args"] = connect_args

            engine = create_engine(target_uri, **engine_kwargs)
        else:
            engine = shared_engine
        Base.metadata.create_all(engine)
        session_factory = scoped_session(sessionmaker(bind=engine, autoflush=False))

        app.extensions["db_engine"] = engine
        app.extensions["db_session_factory"] = session_factory
        app.extensions["db_uri"] = target_uri

    return session_factory


def create_app(config_name: Optional[str] = None) -> Flask:
    """Application factory used by tests and production deployments."""

    static_dir = PROJECT_ROOT / "static"
    templates_dir = PROJECT_ROOT / "templates"

    app = Flask(
        __name__,
        static_folder=str(static_dir),
        template_folder=str(templates_dir),
    )

    _ensure_extension_placeholders(app)
    _initialise_configuration(app, config_name)
    _reset_database_extensions(app)

    # Lazily create the database engine/session factory based on the current
    # configuration.  This allows test code to change ``SQLALCHEMY_DATABASE_URI``
    # after the app has been created without having to recreate the Flask app.
    app.extensions["get_session_factory"] = lambda: _get_session_factory(app)

    @app.teardown_appcontext
    def remove_session(exception: Optional[BaseException] = None) -> None:  # pragma: no cover - defensive
        session_factory = app.extensions.get("db_session_factory")
        if session_factory is not None:
            session_factory.remove()

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    LOGGER.info("Flask application created using '%s' configuration", (config_name or "default"))

    return app


__all__ = ["create_app"]
