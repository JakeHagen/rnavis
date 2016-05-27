from rnavis import app
from flask_restful import Resource, Api, reqparse
import pandas
import rnavis.gene_expression as ge
import sqlalchemy as sql
import psycopg2  # needs to imported because sqlalchemy uses it by default
import os
api = Api(app)

post_parser = reqparse.RequestParser()
post_parser.add_argument('schema', dest='schema', required=True,
                         location='json',
                         help='The schema representing experiment name')
post_parser.add_argument('table', dest='table', required=True, location='json',
                         help='Table name with count data')
post_parser.add_argument('batch', dest='batch', required=False,
                         location='json',
                         help='list of ints which specify batch')

engine = os.environ.get("ENGINE")
engine = sql.create_engine(engine)

mm = ge.matrix_manipulation()


class pca_points(Resource):

    def post(self):
        args = post_parser.parse_args()

        if args.batch:
            try:
                matrix_name = args.schema + '_' + args.table
                mm.make_batch_matrix(batch_list=list(args.batch),
                                     name=matrix_name)
                results = ge.pca_json(mm.get_batch_matrix(name=matrix_name))
            except KeyError:
                print("need voom normalized matrix before batch correcting")
        else:
            try:
                matrix_name = args.schema + '_' + args.table
                results = ge.pca_json(mm.get_norm_matrix(name=matrix_name))
            except KeyError:
                counts = pandas.read_sql_table(args.table,
                                               index_col='Gene',
                                               con=engine,
                                               schema=args.schema)
                mm.add_counts_matrix(name=matrix_name, counts_matrix=counts)
                print(mm.get_norm_matrix(name=matrix_name))
                results = ge.pca_json(mm.get_norm_matrix(name=matrix_name))
        return results.to_dict(orient='records')

api.add_resource(pca_points, '/data')
