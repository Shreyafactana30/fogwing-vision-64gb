"""  * Copyright (C) 2023 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""

from datetime import datetime

from sqlalchemy import func, or_, case
from FWVisonKitAPI import db, app, ma
from FWVisonKitAPI.EdgeSettingAPI.model import FWVEdgeSetup
from FWVisonKitAPI.HomeAPI.control import get_update_payload_c

from FWVisonKitAPI.ProductAPI.model import FWVProducts
from FWVisonKitAPI.QCOrderAPI.model import get_order_id


# this is table of quality control order inspection
class FWVOrdersQc(db.Model):
    """this the fwv_order_qc table for maintaining the good and rejection quantity"""
    fwv_order_qc_id = db.Column(db.Integer, primary_key=True)
    fw_tenant_id = db.Column(db.Integer, nullable=False)
    fwv_order_id = db.Column(db.Integer, db.ForeignKey('fwv_orders.fwv_order_id'), nullable=False)
    fwv_order_code = db.Column(db.String, nullable=False)
    fwv_sub_category = db.Column(db.String, nullable=False)
    fwv_sub_category_qty = db.Column(db.Integer, nullable=False)
    fwv_category_state = db.Column(db.String, nullable=False)
    is_active_data = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_by_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_by_date = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)


# creating schema here for FWVOrdersQc table
class FWVOrdersQcSchema(ma.SQLAlchemyAutoSchema):
    """this is the schema for FWVOrderQc table"""

    class Meta:
        model = FWVOrdersQc


schema_FWVOrdersQc = FWVOrdersQcSchema()


# this function will add the data in FWVOrderQc table and if data is there then it will update the data
def add_update_qcorder_m(json_data):
    """
    this function will check the order id, if order id is present in FWVORderQc table
    then it will update the data or else it adds the new record in table
    """
    try:
        if not json_data:
            return {"Unsuccessful": "Bad Request"}, 400
        products = db.session.query(FWVProducts.fwv_part_name).filter(FWVProducts.is_active == True) \
            .distinct(FWVProducts.fwv_part_name).all()
        if products:
            all_product_names = tuple(map(lambda items: (items[0].split('_')[0]), products))
        else:
            all_product_names = 'Unknown'
        check_tenant = FWVEdgeSetup.query.first()
        if check_tenant:
            odr_id_type = {"fwv_order_code": None, "fwv_order_id": None, "product_name": None}
            order_id = get_order_id(json_data.get("order_code"))
            odr_id_type["fwv_order_code"] = json_data.get("order_code") if json_data.get("order_code") else None
            odr_id_type["fwv_order_id"] = order_id if order_id else None
            odr_id_type["product_name"] = json_data.get("product_name") if json_data.get("product_name") else None
            del json_data["product_name"]
            del json_data["order_code"]
            # odr_id_type = get_update_payload_c()
            payload = json_data
            product_names = odr_id_type["product_name"]
            tenant_id = check_tenant.fw_tenant_id
            if odr_id_type.get("fwv_order_id"):
                order_id = odr_id_type.get("fwv_order_id")
            else:
                return {"Unsuccessful": "Order code not found"}, 404

            good_product, reject_product, unknown_product = {}, {}, {}
            for key, value in payload.items():
                product_key = key.lower().split("_")[0]
                if product_key in product_names:
                    good_product.update({key: value})
                elif product_key in all_product_names:
                    reject_product.update({key: value})
                else:
                    unknown_product.update({key: value})

            category_query = FWVOrdersQc.query.filter(FWVOrdersQc.fwv_order_id == order_id,
                                                   FWVOrdersQc.is_active_data == True
                                                   )

            if good_product:
                good_product_conditions = [FWVOrdersQc.fwv_sub_category.like(key) for key in good_product]
                good_product_filter = or_(*good_product_conditions)
                good_categories = category_query.filter(good_product_filter).all()

                if good_categories:
                    for good_category in good_categories:
                        good_category.fwv_sub_category_qty = good_category.fwv_sub_category_qty + payload.get(good_category.fwv_sub_category, 0)
                        del good_product[good_category.fwv_sub_category]

                if good_product:
                    for key, value in good_product.items():
                        add_data = {
                                'fw_tenant_id': tenant_id, 'fwv_order_id': order_id,
                                'fwv_order_code': odr_id_type.get("fwv_order_code"),
                                'fwv_sub_category': key, 'fwv_sub_category_qty': value,
                                'fwv_category_state': 'Good'
                                }
                        add_order_qc = FWVOrdersQc(**add_data)
                        db.session.add(add_order_qc)

            if reject_product:
                reject_product_conditions = [FWVOrdersQc.fwv_sub_category.like(key) for key in reject_product]
                reject_product_filter = or_(*reject_product_conditions)
                reject_categories = category_query.filter(reject_product_filter).all()

                if reject_categories:
                    for reject_category in reject_categories:
                        reject_category.fwv_sub_category_qty = reject_category.fwv_sub_category_qty + payload.get(reject_category.fwv_sub_category, 0)
                        del reject_product[reject_category.fwv_sub_category]

                if reject_product:
                    for key, value in reject_product.items():
                        add_data = {
                                'fw_tenant_id': tenant_id, 'fwv_order_id': order_id,
                                'fwv_order_code': odr_id_type.get("fwv_order_code"),
                                'fwv_sub_category': key, 'fwv_sub_category_qty': value,
                                'fwv_category_state': 'Rejection'
                                }
                        add_order_qc = FWVOrdersQc(**add_data)
                        db.session.add(add_order_qc)
            if unknown_product:
                unknown_product_conditions = [FWVOrdersQc.fwv_sub_category.like(key) for key in unknown_product]
                unknown_product_filter = or_(*unknown_product_conditions)
                unknown_categories = category_query.filter(unknown_product_filter).all()
                if unknown_categories:
                    for unknown_category in unknown_categories:
                        unknown_category.fwv_sub_category_qty = unknown_category.fwv_sub_category_qty + payload.get(unknown_category.fwv_sub_category, 0)
                        del unknown_product[unknown_category.fwv_sub_category]

                if unknown_product:
                    for key, value in unknown_product.items():
                        add_data = {
                                'fw_tenant_id': tenant_id, 'fwv_order_id': order_id,
                                'fwv_order_code': odr_id_type.get("fwv_order_code"),
                                'fwv_sub_category': key, 'fwv_sub_category_qty': value,
                                'fwv_category_state': 'Unknown'
                                }
                        add_order_qc = FWVOrdersQc(**add_data)
                        db.session.add(add_order_qc)
            db.session.commit()
            return {"Successful": "QC Order Created"}, 201
        else:
            return {"Unsuccessful": "Configure edge setting"}, 400
    except Exception as error_info:
        print(error_info)
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will return the good and rejected quantity based on order id and order type
def get_quantity_count_m(order_code, product_names):
    '''
    this function will return the good and rejected quantity
    based on order id and order type
    '''
    try:
        order_id = get_order_id(order_code)
        filter_conditions = [FWVOrdersQc.fwv_sub_category.ilike('{0}%'.format(key)) for key in product_names]
        combined_filter = or_(*filter_conditions)
        good = db.session.query(func.sum(FWVOrdersQc.fwv_sub_category_qty))\
                                .filter(FWVOrdersQc.fwv_order_id == order_id,
                                        FWVOrdersQc.fwv_order_code == order_code,
                                        combined_filter).scalar()
        all_qty = db.session.query(func.sum(FWVOrdersQc.fwv_sub_category_qty)).filter(
                                FWVOrdersQc.fwv_order_id == order_id,
                                FWVOrdersQc.fwv_order_code == order_code,
                                func.lower(FWVOrdersQc.fwv_category_state) != 'unknown').scalar()

        return {"Good": (good if good else 0), "Rejection": (all_qty if all_qty else 0) - (good if good else 0),
                "Total": all_qty if all_qty else 0, "good_count_weight": get_good_weight(order_id, product_names, order_code)}, 200
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()


# this function will display the all product category type based on order id
def get_category_type_m(order_code):
    """
    this function will display the all product category type based on order id
    """
    try:
        order_id = get_order_id(order_code)
        counts = {}
        products = db.session.query(FWVProducts.fwv_part_name).distinct(FWVProducts.fwv_part_name).all()
        if products:
            for product_name, in products:
                count = db.session.query(func.sum(case((FWVOrdersQc.fwv_sub_category.ilike(f'{product_name}%'), FWVOrdersQc.fwv_sub_category_qty)))) \
                                    .filter(FWVOrdersQc.fwv_order_id == order_id,
                                            FWVOrdersQc.fwv_order_code == order_code,
                                            FWVOrdersQc.is_active_data).scalar()
                if count:
                    counts[product_name] = count
        if not counts:
            return {"Unsuccessful": "Data not found"}, 404
        return counts, 200
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()

# This function will calculate the total weights of each product
def get_good_weight(order_id, product_names, order_code):
    try:
        from FWVisonKitAPI.ProductAPI.model import get_all_products_avg_weight
        good_count_weight = 0
        for i in product_names:
            search_key = '{0}%'.format(i)
            count = db.session.query(func.sum(case((FWVOrdersQc.fwv_sub_category.ilike(search_key), FWVOrdersQc.fwv_sub_category_qty), else_=0)).label(i))\
                                                .filter(FWVOrdersQc.fwv_order_id == order_id, FWVOrdersQc.fwv_order_code == order_code).first()
            weight = get_all_products_avg_weight()
            if weight and weight.get(i):
                good_count_weight += ((count[0] if count[0] else 0) * weight.get(i.lower(), 1))/1000
        return round(good_count_weight, 3)
    except Exception as error_info:
        app.logger.error(error_info)
        return 0
    finally:
        db.session.close()


# This function will give good, rejection, total, and category_type count.
def get_count_category_m(order_code, product_names):
    try:
        order_id = get_order_id(order_code)
        counts = db.session.query(func.sum(case((FWVOrdersQc.fwv_category_state == 'Good', FWVOrdersQc.fwv_sub_category_qty), else_=0)).label('good_count'),\
                                 func.sum(case((FWVOrdersQc.fwv_category_state == 'Rejection',FWVOrdersQc.fwv_sub_category_qty), else_=0)).label('rejected_count'),\
                                 func.sum(FWVOrdersQc.fwv_sub_category_qty).label('total_count')) \
                                 .filter(func.lower(FWVOrdersQc.fwv_category_state) != 'unknown',
                                         FWVOrdersQc.fwv_order_id == order_id, FWVOrdersQc.fwv_order_code == order_code).first()
        final_counts = tuple(0 if not item else item for item in counts)

        count_data = {"Good": final_counts[0], "Rejection": final_counts[1], "Total": final_counts[2],
                      "good_count_weight": get_good_weight(order_id, product_names, order_code)}

        # filter_conditions = [FWVOrdersQc.fwv_sub_category.ilike('%{0}%'.format(key)) for key in product_names]
        # combined_filter = or_(*filter_conditions)
        # good = db.session.query(func.sum(FWVOrdersQc.fwv_sub_category_qty))\
        #                         .filter(FWVOrdersQc.fwv_order_id == order_id,
        #                                 combined_filter).scalar()
        # all_qty = db.session.query(func.sum(FWVOrdersQc.fwv_sub_category_qty)).filter(
        #                         FWVOrdersQc.fwv_order_id == order_id, func.lower(FWVOrdersQc.fwv_category_state) != 'unknown').scalar()
        #
        # count_data = {"Good": (good if good else 0), "Rejection": (all_qty if all_qty else 0) - (good if good else 0),
        #         "Total": all_qty if all_qty else 0, "good_count_weight": get_good_weight(order_id, product_names)}

        counts = {}
        products = db.session.query(FWVProducts.fwv_part_name).distinct(FWVProducts.fwv_part_name).all()
        if products:
            for product_name, in products:
                count = db.session.query(func.sum(case((FWVOrdersQc.fwv_sub_category.ilike(f'{product_name}%'), FWVOrdersQc.fwv_sub_category_qty)))) \
                                    .filter(FWVOrdersQc.fwv_order_id == order_id,
                                            FWVOrdersQc.fwv_order_code == order_code,
                                            FWVOrdersQc.is_active_data==True).scalar()
                if count:
                    counts[product_name] = count

        count_data["category_type_counts"] = counts
        return count_data, 200
    except Exception as error_info:
        app.logger.error(error_info)
        return {"Unsuccessful": "Something went wrong"}, 500
    finally:
        db.session.close()
