"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

import json
import os
from datetime import datetime
import uuid

from instance.config import CREATE_ORDER_EVENT_CODE, UPDATE_ORDER_EVENT_CODE, PATH_TO_WRITE_PAYLOAD
from marshmallow import fields
from sqlalchemy import desc, asc

from FWVisonKitAPI import db, ma, app
from FWVisonKitAPI.EdgeSettingAPI.model import FWVEdgeSetup
from FWVisonKitAPI.ExternalMMAPI.qc_order_api import get_qc_order_data, post_order_data, update_order_data
from FWVisonKitAPI.HomeAPI.control import get_update_payload_c, update_payload_c
from FWVisonKitAPI.ProductAPI.model import FWVProducts
from FWVisonKitAPI.SupplierAPI.model import FWVSupplier
from sqlalchemy.dialects import postgresql


class FWVOrders(db.Model):
    """this is the FWVOrders table"""
    fwv_order_id = db.Column(db.Integer, primary_key=True)
    fwv_order_code = db.Column(db.String, nullable=False)
    fw_tenant_id = db.Column(db.Integer, nullable=False)
    fwv_supplier_id = db.Column(db.Integer, db.ForeignKey('fwv_supplier.fwv_supplier_id'), nullable=True)
    fwv_part_id = db.Column(db.String, nullable=False)
    fwv_order_details = db.Column(db.String, nullable=True)
    fwv_order_qty = db.Column(db.Numeric, nullable=True)
    fwv_order_qty_uom = db.Column(db.String, nullable=True)
    fwv_order_expect_quality = db.Column(db.Integer, nullable=True)
    fwv_order_date = db.Column(db.DateTime, nullable=True)
    fwv_order_status = db.Column(db.String, nullable=False, default='Open')
    fwv_asset_id = db.Column(db.Integer, nullable=True)
    is_active_data = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_by_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_by_date = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)


class FWVOrdersSchema(ma.Schema):
    """this is the Order Schema"""
    fwv_order_id = fields.Int()
    fwv_order_code = fields.Str()
    fw_tenant_id = fields.Int()
    fwv_order_details = fields.Str()
    fwv_order_qty = fields.Int()
    fwv_order_qty_uom = fields.Str()
    fwv_order_expect_quality = fields.Int()
    fwv_order_date = fields.DateTime()
    fwv_order_status = fields.Str()
    fwv_asset_id = fields.Int()
    is_active_data = fields.Bool()
    created_by = fields.Str()
    updated_by = fields.Str()
    created_by_date = fields.DateTime()
    updated_by_date = fields.DateTime()

    fwv_part_id = fields.Str()
    fwv_part_name = fields.Method('get_part_name')

    def get_part_name(self, obj):
        """this function will return the part name"""
        if obj.fwv_part_id:
            part_ids = str(obj.fwv_part_id).split(',')
            part_names = FWVProducts.query.filter(FWVProducts.fwv_part_id.in_(part_ids),
                                                 FWVProducts.is_active == True).all()
            if part_names:
                return [part_name.fwv_part_name for part_name in part_names]
            else:
                return None

    fwv_part_category = fields.Method('get_part_category')

    def get_part_category(self, obj):
        """this function will return the part category"""
        if obj.fwv_part_id:
            part_ids = str(obj.fwv_part_id).split(',')
            part_categories = FWVProducts.query.filter(FWVProducts.fwv_part_id.in_(part_ids),
                                                     FWVProducts.is_active == True).all()
            if part_categories:
                return [part_category.fwv_part_category for part_category in part_categories]
            else:
                return None

    fwv_supplier_id = fields.Int()
    fwv_supplier_name = fields.Method('get_supplier_name')

    def get_supplier_name(self, obj):
        """this function will return the supplier name"""
        if obj.fwv_supplier_id:
            supplier_name = FWVSupplier.query.filter(FWVSupplier.fwv_supplier_id == obj.fwv_supplier_id,
                                                     FWVSupplier.is_active_data == True).first()
            if supplier_name:
                return supplier_name.fwv_supplier_name
            else:
                return None


orders_schema = FWVOrdersSchema()


# This function will fetch all the quality control orders.
def get_qc_order_m():
    """this function will return the all order from the order table which are active"""
    try:
        orders = FWVOrders.query.filter_by(is_active_data=True).all()
        order_schema = orders_schema.dump(orders, many=True)
        if not order_schema:
            return {'Unsuccessful': 'Data not found'}, 404
        return {'orders': order_schema}, 200
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


def parse_and_format_date(date_str):
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date string '{date_str}' does not match any expected formats")


# This function will fetch all the quality control orders.
def sync_qc_orders_m():
    """
    this function will sync the all order first it will check the edge settings
    and then it will call the web app API to update the record
    """
    try:
        check_tenant = FWVEdgeSetup.query.first()
        if check_tenant:
            existing_data = FWVOrders.query.filter_by(is_active_data=True).first()
            if existing_data:
                db.session.query(FWVOrders).delete()
                db.session.commit()
                new_data = get_qc_order_data(check_tenant.fw_tenant_id,check_tenant.fwv_dev_eui)
                if new_data[1] == 200:
                    new_data_json = new_data[0].get("Successful")
                    for item in new_data_json:
                        if isinstance(item["created_by_date"], str):
                            item["created_by_date"] = datetime.strptime(item["created_by_date"], "%Y-%m-%dT%H:%M:%S.%f")
                        if isinstance(item["fwv_order_date"], str):
                            item["fwv_order_date"] = parse_and_format_date(item["fwv_order_date"])  #datetime.strptime(item["fwv_order_date"], "%Y-%m-%dT%H:%M:%S.%f")
                        if item.get("updated_by_date") and isinstance(item["updated_by_date"], str):
                            item["updated_by_date"] = datetime.strptime(item["updated_by_date"], "%Y-%m-%dT%H:%M:%S.%f")
                        if item.get('fwv_part_id'):
                            item['fwv_part_id'] = ','.join(map(str, item.get('fwv_part_id')))
                    db.session.bulk_insert_mappings(FWVOrders, new_data_json)
                    db.session.commit()
                    order_id = get_update_payload_c()
                    order_status = get_order_status(order_id.get('fwv_order_code'))
                    if order_status == 'Completed':
                        data = {"fwv_order_code": None, "fwv_order_id": None, "product_name": None, "fwv_order_status": None}
                        update_payload_c(data)
                    return dict(Successful="Order data synced"), 200
                else:
                    return new_data[0], new_data[1]
            else:
                new_data = get_qc_order_data(check_tenant.fw_tenant_id, check_tenant.fwv_dev_eui)
                if new_data[1] == 200:
                    new_data_json = new_data[0].get("Successful")
                    for item in new_data_json:
                        if isinstance(item["created_by_date"], str):
                            item["created_by_date"] = datetime.strptime(item["created_by_date"], "%Y-%m-%dT%H:%M:%S.%f")
                        if isinstance(item["fwv_order_date"], str):
                            item["fwv_order_date"] = parse_and_format_date(item["fwv_order_date"])   #datetime.strptime(item["fwv_order_date"], "%Y-%m-%dT%H:%M:%S.%f")
                        if item.get("updated_by_date") and isinstance(item["updated_by_date"], str):
                            item["updated_by_date"] = datetime.strptime(item["updated_by_date"], "%Y-%m-%dT%H:%M:%S.%f")
                        if item.get('fwv_part_id'):
                            item['fwv_part_id'] = ','.join(map(str, item.get('fwv_part_id')))
                    db.session.bulk_insert_mappings(FWVOrders, new_data_json)
                    db.session.commit()
                    order_id = get_update_payload_c()
                    order_status = get_order_status(order_id.get('fwv_order_code'))
                    if order_status == 'Completed':
                        data = {"fwv_order_code": None, "fwv_order_id": None, "product_name": None, "fwv_order_status": None}
                        update_payload_c(data)
                    return dict(Successful="Order data synced"), 200
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


# this function will add the order details in qc order tabel:
def add_qc_order_m(add_order):
    '''this function will add the order in order table'''
    try:
        check_tenant = FWVEdgeSetup.query.first()
        if check_tenant:
            add_order["fw_tenant_id"] = check_tenant.fw_tenant_id
            add_order["fwv_order_date"] = datetime.strptime(add_order["fwv_order_date"], "%Y-%m-%d %H:%M:%S.%f")
            check_ord_code = FWVOrders.query.filter(FWVOrders.fwv_order_code == add_order["fwv_order_code"],
                                                    FWVOrders.is_active_data == True).filter(
                FWVOrders.fw_tenant_id == add_order['fw_tenant_id']).first()
            if check_ord_code:
                return {"unsuccessful": "Order Code already exists"}, 409
            data = FWVOrders(**add_order)
            db.session.add(data)
            db.session.commit()

            # Create order in cloud
            if add_order.get('fwv_part_id'):
                add_order['fwv_part_id'] = list(map(int, add_order.get('fwv_part_id').split(',')))
            add_order["fwv_order_date"] = datetime.strftime(add_order["fwv_order_date"], "%Y-%m-%d %H:%M:%S.%f")
            add_order["fwv_asset_id"] = None
            add_order["event_code"] = CREATE_ORDER_EVENT_CODE
            file_path = os.path.join(PATH_TO_WRITE_PAYLOAD, f"add_order_{add_order['fwv_order_code']}_{uuid.uuid4().hex[:8]}.json")
            with open(file_path, "w") as json_file:
                json.dump(add_order, json_file, indent=4)
            return dict(Successful="QC Order added"), 201
        else:
            return dict(Unsuccessful="Configure edge setting"), 400
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will return the all order which are in open status
def get_open_orders_m():
    """this function will return the all order which are in open status"""
    try:
        open_orders = FWVOrders.query.filter(FWVOrders.fwv_order_status != 'Completed',
                                            FWVOrders.is_active_data == True) \
            .order_by(desc(FWVOrders.fwv_order_id)).all()
        order_schema = orders_schema.dump(open_orders, many=True)
        if not order_schema:
            return {'Unsuccessful': 'Data not found'}, 404
        return {'orders': order_schema}, 200
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will fetch the particular order details
def get_order_m(order_code):
    """this fucntion will return the particular order details based on order code"""
    try:
        if order_code:
            open_orders = FWVOrders.query.filter(FWVOrders.fwv_order_code == order_code,
                                                 FWVOrders.is_active_data == True).first()
            if not open_orders:
                return {'Unsuccessful': 'Data not found'}, 404
            order_schema = orders_schema.dump(open_orders)
            return {'orders': order_schema}, 200
        else:
            data = get_open_orders_m()
            if data[1] == 200:
                payload_data = {
                    "fwv_order_code": data[0].get('orders')[0]['fwv_order_code'],
                    "fwv_order_id": data[0].get('orders')[0]['fwv_order_id'],
                    "product_name": data[0].get('orders')[0]['fwv_part_name'],
                    "fwv_order_status": data[0].get('orders')[0]['fwv_order_status']
                }
                update_payload_c(payload_data)
                return {'orders': data[0].get('orders')[0]}, 200
            else:
                return data[0], data[1]
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will delete the order from the order table
def delete_order_m(order_code):
    """
    this function will delete the Order based on order id only from the Device
    when we will sync the order agian that order will come
    """
    try:
        order_id = get_order_id(order_code)
        order_data = FWVOrders.query.get(order_id)
        if order_data:
            schema = orders_schema.dump(order_data)
            if schema.get("fwv_order_status") in ("Open", "Completed"):
                db.session.delete(order_data)
                db.session.commit()
                return {'Successful': 'QC Order Deleted'}, 200
            else:
                return {'Unsuccessful': "Unable to delete in-progress order"}, 422
        else:
            return {'Unsuccessful': 'QC Order not found'}, 400
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will update the order in order table
def update_qc_order_m(order_code, order_status):
    '''
    this function will update the order in order table and after updating
    we will call the web application update order api to update also there
    '''
    try:
        check_tenant = FWVEdgeSetup.query.first()
        if check_tenant:
            check_ord_code = FWVOrders.query.filter(FWVOrders.fwv_order_code == order_code)
            if check_ord_code.first() and check_ord_code.first().is_active_data:
                check_ord_code.first().fwv_order_status = order_status
                check_ord_code.first().updated_by_date = datetime.now()
                db.session.commit()

                update_data = {"fwv_order_code": order_code, "fwv_order_status": order_status, "event_code": UPDATE_ORDER_EVENT_CODE}
                file_path = os.path.join(PATH_TO_WRITE_PAYLOAD, f"update_order_{order_status}_{order_code}_{uuid.uuid4().hex[:8]}.json")
                with open(file_path, "w") as json_file:
                    json.dump(update_data, json_file, indent=4)
                return dict(Successful="QC Order updated"), 200
            else:
                return dict(Unsuccessful="QC Order not found"), 404
        else:
            return dict(Unsuccessful="Configure edge setting"), 400
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will update the payload, by taking inprogress and that function will call by log-in function
def update_payload_order_m():
    """
    this function will update the payload, by taking inprogress and
    that function will call by log-in function
    """
    try:
        check_tenant = FWVEdgeSetup.query.first()
        if check_tenant:
            inprogress_order = FWVOrders.query.filter(FWVOrders.fwv_order_status == 'In progress').first()
            if inprogress_order:
                order_schema = orders_schema.dump(inprogress_order)
                if order_schema:
                    data = {"fwv_order_code": order_schema.get("fwv_order_code"),
                            "fwv_order_id": order_schema.get("fwv_order_id"),
                            "product_name": order_schema.get("fwv_part_name"),
                            "fwv_order_status": order_schema.get("fwv_order_status")}
                    update_payload_c(data)
            else:
                return dict(Unsuccessful="QC Order not found"), 404
        else:
            return dict(Unsuccessful="Configure edge setting"), 400
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will return the status of the order
def get_order_status(order_code):
    try:
        if order_code:
            order = FWVOrders.query.filter(FWVOrders.fwv_order_code==order_code).filter(FWVOrders.is_active_data==True).first()
            if order :
                return order.fwv_order_status
            else:
                return False
        else:
            return False
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will return the order id based on order code
def get_order_id(order_code):
    if order_code:
        order = FWVOrders.query.filter(FWVOrders.fwv_order_code==order_code).filter(FWVOrders.is_active_data==True).first()
        if order :
            return order.fwv_order_id
        else:
            return False
    else:
        return False

# This function will fetch the QC order from the cloud.
def previous_order_m(current_order_code):
    try:
        privious_order = FWVOrders.query.filter(FWVOrders.fwv_order_code!=current_order_code, FWVOrders.is_active_data==True, FWVOrders.fwv_order_status!="Open").order_by(desc("updated_by_date")).first()
        if privious_order:
            privious_order_schema = FWVOrdersSchema(only=('fwv_order_code', 'fwv_order_id',
                                                    'fwv_order_status', 'fwv_part_name')).dump(privious_order)

            return privious_order_schema, 200
        else:
            return {"Unsuccessful": "Data not found"}, 404
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()
