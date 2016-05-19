from rnavis import app
from flask_restful import Resource, Api, reqparse
import pandas
import rnavis.gene_expression as ge
import rnavis.combat as combat
import sqlalchemy as sql
import rnavis.config as config
import psycopg2


api = Api(app)

get_parser = reqparse.RequestParser()
get_parser.add_argument('matrix', dest='matrix', required=True,
                        location='headers',
                        help='Get the original matrix, must be posted first')
get_parser.add_argument('matrix_norm', dest='matrix_norm', required=True,
                        location='headers',
                        help='Get the normalized matrix')
get_parser.add_argument('matrix_batch', dest='matrix_batch', required=True,
                        location='headers',
                        help='Get normalized and batch corrected matrix')

engine = sql.create_engine(config.psql)


class pca_points(Resource):

    def __init__(self):
        self.org_mat = None
        self.norm_mat = None
        self.batch_mat = None

    def get(self):
        args = get_parser.parse_args()
        if sum([args.matrix, args.matrix_norm, args.matrix_batch]) > 1:
            return {'status': 501, 'message': 'can only return one matrix'}
        if sum([args.matrix, args.matrix_norm, args.matrix_batch]) == 0:
            return self.org_mat or {'status': 400,
                                    'message': 'Need to post matrix first'}
        if args.matrix:
            return self.org_mat
        if args.norm_mat:
            return self.norm_mat or ge.norm_gene_matrix(self.org_mat)
        if args.matrix_batch:
            return (self.batch_mat or
                    combat.combat(self.norm_mat, batch=list(args.batch)) or
                    combat.combat(ge.norm_gene_matrix(self.org_mat),
                                  batch=list(args.batch)))
        return {'status': 400, 'message': 'something was wrong with request'}

    def post(self):


api.add_resource(pca_points, '/data')
