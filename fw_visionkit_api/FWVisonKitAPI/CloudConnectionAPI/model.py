"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from FWVisonKitAPI import db, ma
from datetime import datetime


class FWVCloudConn(db.Model):
    '''this is the cloud connection table'''
    fwv_cloud_conn_id = db.Column(db.Integer, primary_key=True)
    fwv_mqtt_client_id = db.Column(db.String, nullable=False)
    fwv_apikey = db.Column(db.String, nullable=False)
    fwv_mqtt_username = db.Column(db.String, nullable=False)
    fwv_fogwing_apikey = db.Column(db.String, nullable=False)
    fwv_mqtt_password = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)


class FWVCloudConnSchema(ma.SQLAlchemyAutoSchema):
    '''this is the cloud connection schema'''
    class Meta:
        model = FWVCloudConn


cloud_conn_schema = FWVCloudConnSchema()

# This function will fetch cloud conn data.
def get_cloudconn_data_model():
    """
    Retrieve active cloud connection data and serialize it.
    Returns: dict: Serialized active cloud connection data in a dictionary.
            Key 'cloud_conn' holds the data, or 'Unsuccessful' on error.
    """
    try:
        cloud_conn = FWVCloudConn.query.filter_by(is_active=True).all()
        cloud_conn_schema_data = cloud_conn_schema.dump(cloud_conn, many=True)
        return dict(cloud_conn=cloud_conn_schema_data)
    except Exception:
        return dict(Unsuccessful="Something Went Wrong")
    finally:
        db.session.close()


# This function will add the cloud conn data into table.
def post_cloudconn_data_model(conn_data):
    """this function will take the cloud connection payload and add the cloud table"""
    try:
        cloud_conn_id = conn_data.get("fwv_cloud_conn_id")
        if cloud_conn_id:
            exist_cloudconn_data = FWVCloudConn.query.filter_by(is_active=True, fwv_cloud_conn_id=cloud_conn_id)
            if exist_cloudconn_data.first():
                exist_cloudconn_data.update(conn_data)
                db.session.commit()
                return dict(Successful="Cloud connection establised"), 201
        else:
            add_cloudconn_data = FWVCloudConn(**conn_data)
            db.session.add(add_cloudconn_data)
            db.session.commit()
            return dict(Successful="Cloud connection establised"), 201
    except Exception:
        return dict(Unsuccessful="Something Went Wrong"), 500
    finally:
        db.session.close()
