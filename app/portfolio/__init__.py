from flask import Blueprint

portfolio_bp = Blueprint('portfolio', __name__)

from app.portfolio import routes