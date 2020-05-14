# -*- coding: utf-8 -*-
from sawtooth_signing import create_context


class Sawtooth:
    def __init__(self, app=None):
        self.app = app
        self.context = create_context("secp256k1")
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.sawtooth_ctx = self.context


swt = Sawtooth()
