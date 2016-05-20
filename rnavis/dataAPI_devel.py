from rnavis import app
from flask_restful import Resource, Api, reqparse
import pandas
import rnavis.gene_expression as ge
import rnavis.combat as combat


api = Api(app)

get_parser = reqparse.RequestParser()
get_parser.add_argument('org_matrix', dest='org_matrix', required=False,
                        location='headers',
                        help='Get the original matrix, must be posted first')
get_parser.add_argument('norm_matrix', dest='norm_matrix', required=False,
                        location='headers',
                        help='Get the normalized matrix')
get_parser.add_argument('batch_matrix', dest='batch_matrix', required=False,
                        location='headers',
                        help='Get normalized and batch corrected matrix')

post_parser = reqparse.RequestParser()
post_parser.add_argument('org_matrix_name', dest='org_matrix_name',
                         required=False, location='json',
                         help='Name of the original matrix')
post_parser.add_argument('norm_matrix_name', dest='norm_matrix_name',
                         required=False, location='json',
                         help='Name of the normalized matrix')
post_parser.add_argument('batch_matrix_name', dest='batch_matrix_name',
                         required=False, location='json',
                         help='name of the batch correct matrix')
post_parser.add_argument('matrix', dest='matrix', required=False,
                         location='json', help='matrix or dataframe in json')

put_parser = reqparse.RequestParser()
put_parser.add_argument('batch_list', dest='batch_list', required=True,
                        location='json',
                        help='Post list of ints specifying batch')
put_parser.add_argument('matrix_to_correct', dest='matrix_to_correct',
                        required=False, location='json',
                        help='matrix that needs to be batch corrected')
put_parser.add_argument('name_matrix_to_correct',
                        dest='name_matrix_to_correct', required=False,
                        location='json',
                        help='name of matrix that is stored to be corrected')


class pca_points(Resource):

    def __init__(self):
        self.org_dict = {}
        self.norm_dict = {}
        self.batch_dict = {}

    def get(self):
        args = get_parser.parse_args()
        if sum([args.org_matrix, args.norm_matrix, args.batch_matrix]) > 1:
            return {'status': 501, 'message': 'can only return one matrix'}
        if sum([args.org_matrix, args.norm_matrix, args.batch_matrix]) == 0:
            return {'status': 400, 'message': 'need to specify matrix'}
        if args.org_matrix:
            return self.org_dict[args.org_matrix]
        if args.norm_matrix:
            try:
                return self.norm_dict[args.norm_matrix]
            except KeyError:
                try:
                    return ge.norm_gene_matrix(self.org_dict[args.norm_matrix])
                except KeyError:
                    return {'status': 404,
                            'message': 'need to post matrix first'}
        if args.batch_matrix:
            try:
                return self.batch_dict[args.batch_matrix]
            except KeyError:
                return {'status': 404,
                        'message': 'matrix needs to be batch corrected first'}
        return {'status': 400, 'message': 'something was wrong with request'}

    def post(self):
        args = post_parser.parse_args()
        if not args.matrix:
            return {'status': 400, 'message': 'need to attach matrix'}
        if sum([args.org_matrix_name, args.norm_matrix_name,
                args.batch_matrix_name]) > 1:
            return {'status': 501,
                    'message': 'can add one type of matrix per time'}
        if args.batch_matrix_name:
            self.batch_dict[args.batch_matrix_name] = pandas.read_json(
                                                    args.matrix, numpy=True
                                                                    )
            return self.batch_dict[args.batch_matrix_name]
        if args.norm_matrix_name:
            self.norm_dict[args.norm_matrix_name] = pandas.read_json(
                                                    args.matrix, numpy=True
                                                                    )
            return self.norm_dict[args.norm_matrix_name]
        if args.org_matrix_name:
            self.org_dict[args.org_matrix_name] = pandas.read_json(
                                                    args.matrix, numpy=True
                                                                    )
            return self.norm_dict[args.org_matrix_name]
        return {'status': 400, 'message': 'something was wrong with request'}

    def put(self):
        args = put_parser.parse_args()
        if not args.batch_list:
            return {'status': 400,
                    'message': 'need to specify the batch for samples'}
        if args.matrix_to_correct and args.name_matrix_to_correct:
            return {'status': 400,
                    'message': 'cant batch correct two matrices at once'}
        try:
            matrix_to_correct = self.norm_dict[args.name_matrix_to_correct]
            self.batch_dict[args.name_matrix_to_correct] = combat.combat(
                                matrix_to_correct, batch=list(args.batch_list))
            return self.batch_dict[args.name_matrix_to_correct]
        except KeyError:
            matrix_to_correct = pandas.read_json(args.matrix_to_correct)
            return combat.combat(matrix_to_correct,
                                 batch=list(args.batch_list))
        return {'status': 400, 'message': 'something was wrong with request'}

api.add_resource(pca_points, '/data')
