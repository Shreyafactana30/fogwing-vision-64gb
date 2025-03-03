""" * Copyright (C) 2021 Factana Computing Pvt Ltd.
    * All Rights Reserved.
    * This file is subject to the terms and conditions defined in
    * file 'LICENSE.txt', which is part of this source code package. """

import sys
import logging
from os import path
from FWVisonKitAPI import create_app

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# configure root logger
#logging.basicConfig(filename='fwvision.log',
                   # format='%(asctime)s %(levelname)s %(name)s : %(message)s',
                    #level=logging.WARNING)

app = create_app()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7077, debug=True)
