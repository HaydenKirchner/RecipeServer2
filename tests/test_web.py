"""Tests for the user-facing web blueprint."""
from __future__ import annotations


def test_homepage_renders_successfully(client):
    """The homepage should render without server errors."""

    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to Recipe Planner" in response.data
