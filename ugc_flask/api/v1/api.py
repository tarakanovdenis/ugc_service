from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    jwt_required,
    # get_jwt
)

from producer import send_message_to_kafka
from settings import ClickTrackingTopics


api = Blueprint('api', __name__, )


@api.route('/quality-change', methods=['POST'])
@jwt_required(optional=True)
def quality_change():
    try:
        data = request.get_json()
        send_message_to_kafka(
            ClickTrackingTopics.QUALITY_CHANGE_CLICK.value,
            body=data
        )
        return jsonify(
            {'status': 'success'}
        ), 200
    except Exception as e:
        return jsonify(
            {
                'status': 'error',
                'message': str(e)
            }
        ), 500


@api.route('/pause', methods=['POST'])
@jwt_required(optional=True)
def pause():
    try:
        data = request.get_json()
        send_message_to_kafka(
            ClickTrackingTopics.PAUSE_CLICK.value,
            body=data
        )
        return jsonify(
            {'status': 'success'}
        ), 200
    except Exception as e:
        return jsonify(
            {
                'status': 'error',
                'message': str(e)
            }
        ), 500


@api.route('/full-view', methods=['POST'])
@jwt_required(optional=True)
def full_view():
    try:
        data = request.get_json()
        send_message_to_kafka(
            ClickTrackingTopics.FULL_VIEW.value,
            body=data
        )
        return jsonify(
            {'status': 'success'}
        ), 200
    except Exception as e:
        return jsonify(
            {
                'status': 'error',
                'message': str(e)
            }
        ), 500
