"""
WSGI shim for Render or hosting environments looking for wsgi:app or wsgi:application in root.
"""
from app import application, app
