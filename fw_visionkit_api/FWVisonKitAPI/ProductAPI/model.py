"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

from sqlalchemy import func, text
from FWVisonKitAPI import db, ma, create_app, app
from datetime import datetime
from FWVisonKitAPI.ExternalMMAPI.product_api import get_product_data
from FWVisonKitAPI.EdgeSettingAPI.model import FWVEdgeSetup


class FWVProducts(db.Model):
     '''this is the product table'''
     fwv_part_id = db.Column(db.Integer, primary_key=True)
     fw_tenant_id = db.Column(db.Integer, nullable=False)
     fwv_part_code = db.Column(db.String, nullable=False)
     fwv_part_name = db.Column(db.String, nullable=False)
     fwv_part_desc = db.Column(db.String, nullable=True)
     fwv_part_is_assembled = db.Column(db.Boolean, nullable=False)
     fwv_part_is_child = db.Column(db.Boolean, nullable=False)
     fwv_part_is_purchasable = db.Column(db.Boolean, nullable=False)
     fwv_part_qty_in_stock = db.Column(db.Integer, default=0, nullable=True)
     fwv_part_lead_time_mins = db.Column(db.Float, nullable=True)
     fwv_part_uom = db.Column(db.String, nullable=True)
     fwv_part_variant = db.Column(db.String, nullable=True)
     fwv_part_weight = db.Column(db.Integer, nullable=True)
     fwv_part_category = db.Column(db.String, nullable=False)
     is_active = db.Column(db.Boolean, nullable=False, default=True)
     created_by = db.Column(db.String, nullable=False)
     updated_by = db.Column(db.String, nullable=True)
     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
     updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
     fwv_part_quality_rationale = db.Column(db.String, nullable=True)


class FWVProductsSchema(ma.SQLAlchemyAutoSchema):
     '''this is the product schema'''
     class Meta:
          model = FWVProducts


product_schema = FWVProductsSchema()


# This function will fetch all the products.
def get_products_m():
     '''this function will return all the product which are active'''
     try:
          products = FWVProducts.query.filter_by(is_active=True).all()
          products_schema_data = product_schema.dump(products, many=True)
          if not products_schema_data:
               return {'Unsuccessful': 'Data not found'}, 404
          return {'products': products_schema_data}, 200
     except Exception as error_info:
          app.logger.error(error_info)
          return {"Unsuccessful": "Something went wrong"}, 500
     finally:
          db.session.close()


# This function will fetch all the products.
def sync_products_m():
     '''
     this function will sync the product first it will check the tenant
     and then it will call the web application api to get data and then it is update it
     '''
     try:
          check_tenant = FWVEdgeSetup.query.first()
          if check_tenant:
               existing_data = FWVProducts.query.filter_by(is_active=True).first()
               if existing_data:
                    db.session.query(FWVProducts).delete()
                    db.session.commit()
                    new_data = get_product_data(check_tenant.fw_tenant_id)
                    if new_data[1] == 200:
                         new_data_json = new_data[0]
                         for item in new_data_json:
                              item["created_at"] = datetime.strptime(item["created_by_date"], "%Y-%m-%dT%H:%M:%S")
                              if item.get("updated_at"):
                                   item["updated_at"] = datetime.strptime(item["updated_at"], "%Y-%m-%dT%H:%M:%S")
                         db.session.bulk_insert_mappings(FWVProducts, new_data_json)
                         db.session.commit()
                         return dict(Successful="Product data synced"), 200
                    else:
                         return new_data[0], new_data[1]
               else:
                    new_data = get_product_data(check_tenant.fw_tenant_id)
                    if new_data[1] == 200:
                         for item in new_data[0]:
                              item["created_at"] = datetime.strptime(item["created_by_date"], "%Y-%m-%dT%H:%M:%S")
                              if item.get("updated_at"):
                                   item["updated_at"] = datetime.strptime(item["updated_at"], "%Y-%m-%dT%H:%M:%S")
                         db.session.bulk_insert_mappings(FWVProducts, new_data[0])
                         db.session.commit()
                         return dict(Successful="Product data synced"), 200
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

# this function will return the all distinct product name
def get_product_name_m():
     try:
          check_tenant = FWVEdgeSetup.query.first()
          if check_tenant:
               distinct_products = db.session.query(func.min(FWVProducts.fwv_part_id).label("fwv_part_id"),FWVProducts.fwv_part_name)\
                    .filter(FWVEdgeSetup.fw_tenant_id==check_tenant.fw_tenant_id).group_by(FWVProducts.fwv_part_name).all()
               if distinct_products:
                    products_schema_data = product_schema.dump(distinct_products, many=True)
                    return {'products': products_schema_data}, 200
               else:
                    return {'Unsuccessful': 'Data not found'}, 404
          else:
               return dict(Unsuccessful="Configure edge setting"), 400
     except Exception as error_info:
          db.session.rollback()
          app.logger.error(error_info)
          return {"Unsuccessful": "Something went wrong"}, 500
     finally:
          db.session.close()


def get_all_products_avg_weight():
    try:
        weights_product_name = db.session.query(func.avg(FWVProducts.fwv_part_weight), FWVProducts.fwv_part_name) \
                                        .filter(FWVProducts.is_active) \
                                        .group_by(FWVProducts.fwv_part_name).all()
        weight = { product_name: round(float(weights), 3) for weights, product_name in weights_product_name if weights}
        return weight
    except Exception as e:
        app.logger.error(e)
        return False
    finally:
        db.session.close()
