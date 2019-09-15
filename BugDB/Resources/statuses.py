from flask import request, current_app
from flask_restful import Resource
from BugDB.db import database
from BugDB.Models import StatusesModel
from BugDB.Decorators import check_schema


class StatusesResource(Resource):
    def get(self):
        payload = []

        for i in database.session.query(StatusesModel).all():
            payload.append({
                "id": i.id,
                "status": i.status,
                "description": i.description
            })

        return {
            "payload": payload
        }, 200

    @check_schema({
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "pattern": "^(a-zA-Z0-9){1,32}$"
            },
            "description": {
                "type": "string"
            }
        },
        "required": [
            "status",
            "description"
        ]
    })
    def post(self):
        status = StatusesModel()
        status.status = request.json.get('status')
        status.description = request.json.get('description')

        try:
            database.session.add(status)
            database.session.flush()
        except Exception as ex:
            current_app.logger.error(ex)
            database.session.rollback()

        return {
            "payload": {
                "id": status.id,
                "status": status.status,
                "description": status.description,
            }
        }, 201

    def delete(self):
        allowed_args = ["id", "status"]
        filters = dict()
        for i in request.args:
            if i in allowed_args:
                filters[i] = request.args.get(i)

        if database.session.query(StatusesModel).filter_by(**filters).count() == 0:
            return {}, 404

        StatusesModel.query.filter_by(**filters).delete()
        return {}, 200
