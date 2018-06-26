# Sample Test passing with nose and pytest
import pytest
import lazypandas


def test_pass():
    assert True, "dummy sample test"


def test_gimme():

    gimme = lazypandas.gimme_string()

    assert gimme == "Hello!"
