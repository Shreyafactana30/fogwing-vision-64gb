"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from FWVisonKitAPI import db, ma
from datetime import datetime

from FWVisonKitAPI.ExternalMMAPI.qc_order_api import get_shifts_data


class FWVEdgeSetup(db.Model):
    fwv_edge_setup_id = db.Column(db.Integer, primary_key=True)
    fw_tenant_id = db.Column(db.Integer, nullable=False)
    fwv_asset_code = db.Column(db.String, nullable=False)
    fwv_asset_name = db.Column(db.String, nullable=False)
    fwv_dev_eui = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)


class FWVEdgeSetupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FWVEdgeSetup


edge_setup_schema = FWVEdgeSetupSchema()


# this is the global variable for edge_eui and shifts
shifts_data = {
                "edge_eui": None,
                "shifts": None
                }

# This function will fetch all the vision edge setup screen data.
def get_edgeset_data_model():
    try:
        edge_setup = FWVEdgeSetup.query.filter_by(is_active=True).all()
        edge_setup_schema_data = edge_setup_schema.dump(edge_setup, many=True)
        return dict(edgesetup=edge_setup_schema_data)
    except Exception as e:
        return dict(Unsuccessful="Something Went Wrong"), 500
    finally:
        db.session.close()


# This function will fetch all the vision edge setup screen data.
def post_edgeset_data_model(edge_setup_data):
    try:
        edge_setup_id = edge_setup_data.get("fwv_edge_setup_id")
        if edge_setup_id:
            exist_edgesetup_data = FWVEdgeSetup.query.filter_by(is_active=True, fwv_edge_setup_id=edge_setup_id)
            if exist_edgesetup_data.first():
                exist_edgesetup_data.update(edge_setup_data)
                db.session.commit()
                return dict(Successful="Edge Setup Configured"), 201
        else:
            add_edgesetup_data = FWVEdgeSetup(**edge_setup_data)
            db.session.add(add_edgesetup_data)
            db.session.commit()
            return dict(Successful="Edge Setup Configured"), 201
    except Exception as e:
        return dict(Unsuccessful="Something Went Wrong"), 500
    finally:
        db.session.close()


# this function will call the eternal api and return the updated shifts data
def get_shifts_m():
    try:
        check_tenant = FWVEdgeSetup.query.first()
        if check_tenant:
            data = get_shifts_data(check_tenant.fw_tenant_id, check_tenant.fwv_dev_eui)
            if data[1] == 200:
                return data[0], 200
            else:
                return data[0], data[1]
        else:
            return dict(Unsuccessful="Configure edge setting"), 400
    except Exception as e:
        return dict(Unsuccessful="Something Went Wrong"), 500
    finally:
        db.session.close()
