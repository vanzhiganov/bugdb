from flask import request
from flask_restful import Resource
from BugDB.db import database
from BugDB.Models import StatusesModel


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

    def post(self):
        status = StatusesModel()
        status.status = request.json.get('status')
        status.description = request.json.get('description')

        database.session.add(status)
        database.session.commit()
        database.session.flush()

        # TODO: add rollback with failed insert

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
        StatusesModel.query.filter_by(**filters).delete()
        return {}, 200
