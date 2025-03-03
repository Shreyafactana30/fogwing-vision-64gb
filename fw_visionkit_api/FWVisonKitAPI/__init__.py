"""  * Copyright (C) 2019 Factana Computing Pvt Ltd.
     * All Rights Reserved.
     * This file is subject to the terms and conditions defined in
     * file 'LICENSE.txt', which is part of this source code package."""


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from FWVisonKitAPI.config import Config
from flask_cors import CORS
from instance.config import SQLALCHEMY_DATABASE_URI

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{SQLALCHEMY_DATABASE_URI}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
ma = Marshmallow()
CORS(app)


def create_app(config_class=Config):
     app.config.from_object(Config)
     db.init_app(app)
     ma.init_app(app)
     with app.app_context():
          from FWVisonKitAPI.LoginAPI.view import fwvision_usermgmt_bp
          app.register_blueprint(fwvision_usermgmt_bp)
          from FWVisonKitAPI.CloudConnectionAPI.view import fwvision_cloudconn_bp
          app.register_blueprint(fwvision_cloudconn_bp)
          from FWVisonKitAPI.EdgeSettingAPI.view import fwvison_edgeset_bp
          app.register_blueprint(fwvison_edgeset_bp)
          from FWVisonKitAPI.ProductAPI.view import fwv_product_bp
          app.register_blueprint(fwv_product_bp)
          from FWVisonKitAPI.SupplierAPI.view import fwv_supplier_bp
          app.register_blueprint(fwv_supplier_bp)
          from FWVisonKitAPI.QCOrderAPI.view import fwv_qcorder_bp
          app.register_blueprint(fwv_qcorder_bp)
          from FWVisonKitAPI.HomeAPI.view import fwv_home_bp
          app.register_blueprint(fwv_home_bp)
          from FWVisonKitAPI.QCInspection.view import fwv_qcinspection_bp
          app.register_blueprint(fwv_qcinspection_bp)
          from FWVisonKitAPI.DeviceSettingAPI.view import fwvison_deviceset_bp
          app.register_blueprint(fwvison_deviceset_bp)
          # db.create_all()
     return app
