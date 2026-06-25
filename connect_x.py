from flask import Flask, render_template, request, session, redirect, url_for
import secrets, requests, hashlib, base64, os

def pkce_pair():
    verifier = base64.urlsafe_b64decode(secrets.token_bytes(32)).decode().rstrip("=")
    challenge = base64.urlsafe_b64decode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")
    return verifier, challenge

def connect():
    verifier, challenge = pkce_pair()
    session['verifier'] = verifier
    params = {
        "response_type":"code",
        "client_id":CLIENT_ID,
        "redirect_url":REDIRECT_URL,
        "scope":SCOPES,
        "state":secrets.token_urlsafe(16),
        "code_challenge":challenge,
        "code_challenge_method":"S256"
    }