
"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

from sqlalchemy import text
from FWVisonKitAPI import db, ma, create_app, app
from datetime import datetime
from FWVisonKitAPI.EdgeSettingAPI.model import FWVEdgeSetup
from FWVisonKitAPI.ExternalMMAPI.supplier_api import get_supplier_data

class FWVSupplier(db.Model):
    '''this is the supplier table'''
    fwv_supplier_id = db.Column(db.Integer, primary_key=True)
    fw_tenant_id = db.Column(db.Integer, nullable=False)
    fwv_supplier_code = db.Column(db.String, nullable=False)
    fwv_supplier_name = db.Column(db.String, nullable=True)
    fwv_contact_name = db.Column(db.String, nullable=True)
    fwv_supplier_address = db.Column(db.String, nullable=True)
    fwv_contact_number = db.Column(db.BIGINT, nullable=True)
    fwv_email_address = db.Column(db.String, nullable=True)
    fwv_supplier_website = db.Column(db.String, nullable=True)
    fwv_supplier_type = db.Column(db.String, nullable=True)
    fwv_supplier_note = db.Column(db.String, nullable=True)
    is_active_data = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_by_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_by_date = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)


class FWVSuppliersSchema(ma.SQLAlchemyAutoSchema):
    '''this is the supplier schema'''
    class Meta:
        model = FWVSupplier


supplier_schema = FWVSuppliersSchema()

# This function will fetch all the products.
def get_suppliers_m():
    '''this function will return the all suppliers which are active'''
    try:
        suppliers = FWVSupplier.query.filter_by(is_active_data=True).all()
        suppliers_schema = supplier_schema.dump(suppliers, many=True)
        if not suppliers_schema:
            return {'Unsuccessful': 'Data not found'}, 404
        return {'suppliers':suppliers_schema}, 200
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# This function will fetch all the products.
def sync_suppliers_m():
    '''
    this function will sync the supplier first it will check the tenant
    and then it will call the web application api and then it will update the data
    '''
    try:
        check_tenant = FWVEdgeSetup.query.first()
        if check_tenant:
            existing_data = FWVSupplier.query.filter_by(is_active_data=True).first()
            if existing_data:
                db.session.query(FWVSupplier).delete()
                db.session.commit()
                new_data = get_supplier_data(check_tenant.fw_tenant_id)
                if new_data[1] == 200:
                    for item in new_data[0]:
                            item["created_by_date"] = datetime.strptime(item["created_by_date"], "%Y-%m-%dT%H:%M:%S")
                            if item.get("updated_at"):
                                item["updated_at"] = datetime.strptime(item["updated_at"], "%Y-%m-%dT%H:%M:%S")
                    db.session.bulk_insert_mappings(FWVSupplier, new_data[0])
                    db.session.commit()
                    return dict(Successful="Supplier data synced"), 200
                return new_data[0], new_data[1]
            else:
                new_data = get_supplier_data(check_tenant.fw_tenant_id)
                if new_data[1] == 200:
                    for item in new_data[0]:
                            item["created_by_date"] = datetime.strptime(item["created_by_date"], "%Y-%m-%dT%H:%M:%S")
                            if item.get("updated_at"):
                                item["updated_at"] = datetime.strptime(item["updated_at"], "%Y-%m-%dT%H:%M:%S")
                    db.session.bulk_insert_mappings(FWVSupplier, new_data[0])
                    db.session.commit()
                    return dict(Successful="Supplier data synced"), 200
                else:
                    return new_data[0], new_data[1]
        else:
            return dict(Unsuccessful="Configure edge setting"), 400
    except Exception as error_info:
        db.session.rollback()
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()
