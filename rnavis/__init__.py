from flask import Flask
import os
app = Flask(__name__)

import rnavis.view
import rnavis.matrix_manip_api


port = int(os.environ.get("PORT", 33507))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
