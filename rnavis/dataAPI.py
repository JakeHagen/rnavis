from rnavis import app
from flask_restful import Resource, Api, reqparse
import pandas
import rnavis.ge as ge
import rnavis.combat as combat
import sqlalchemy as sql
import rnavis.config as config


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

engine = sql.create_engine(config.psql)


class pca_points(Resource):
    def post(self):
        args = post_parser.parse_args()
        print(args)
        if args.batch:
            try:
                rna_exp = ge.gene_expression(
                    pandas.read_sql_table(args.table + "_voom",
                                          index_col='Gene',
                                          con=engine,
                                          schema=args.schema))
                rna_exp_batch = ge.gene_expression(
                    combat.combat(rna_exp.df, batch=list(args.batch)))
                results = ge.pca_json(rna_exp_batch, voom=False)
            except:   # Need to catch error psycopg2.ProgrammingError
                print("need voom normalized matrix before batch correcting")
        else:
            try:
                rna_exp = ge.gene_expression(
                    pandas.read_sql_table(args.table + "_voom",
                                          index_col='Gene',
                                          con=engine,
                                          schema=args.schema))
                results = ge.pca_json(rna_exp, voom=False)
            except:
                rna_exp = ge.gene_expression(
                    pandas.read_sql_table(args.table,
                                          index_col='Gene',
                                          con=engine,
                                          schema=args.schema))
                voom_df = ge.voom_out(rna_exp)
                voom_df.to_sql(args.table + "_voom",
                               con=engine, schema=args.schema)
                results = ge.pca_json(rna_exp, voom=True)
        return results

api.add_resource(pca_points, '/data')