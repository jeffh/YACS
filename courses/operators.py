# from http://djangosnippets.org/snippets/2008/
from copy import deepcopy

from django.db import models
from django.db.models.sql.expressions import SQLEvaluator
from django.utils import tree


class FExpression(object):
    '''
    FExpression is the simplest way to reach the code path we need
    and should not inherit from tree.Node or any subclass thereof.

    FExpression currently only supports the integer comparison.
    Partial string comparison and such do not work because of the
    way these are defined in connection.operators. For those you
    should use the regular filter methods django provides.
    '''
    def __init__(self, left_expression, lookup_type, right_expression):
        self.left_expression = left_expression
        self.lookup_type = lookup_type
        self.right_expression = right_expression

    def as_sql(self, qn, connection):
        cast_sql = connection.ops.lookup_cast(self.lookup_type)
        field = models.Field()
        # expression is either a smart expression or a user parameter
        if hasattr(self.left_expression, 'as_sql'):
            left_sql, left_params = self.left_expression.as_sql(qn, connection)
            left_sql = cast_sql % left_sql
        else:
            left_sql, left_params = cast_sql, field.get_db_prep_lookup(self.lookup_type, self.left_expression, connection=connection)
        # right hand side is cast by the operator sql
        if hasattr(self.right_expression, 'as_sql'):
            right_sql, right_params = self.right_expression.as_sql(qn, connection)
        else:
            right_sql, right_params = '%s', field.get_db_prep_lookup(self.lookup_type, self.right_expression, connection=connection)

        format = '%%s %s' % connection.operators[self.lookup_type]
        return format % (left_sql, right_sql), list(left_params) + list(right_params)


class FNode(tree.Node):
    '''
    FNode inherits tree.Node to pass tests for the code path we need
    This allows FNode to work without using complex_filter
    '''
    def __init__(self, left_expression, lookup_type, right_expression):
        if lookup_type not in ('exact', 'gt', 'gte', 'lt', 'lte'):
            raise ValueError(
                'Invalid operator, operator %r is not supported.' % lookup_type)
        super(FNode, self).__init__()
        self.left_expression = left_expression
        self.lookup_type = lookup_type
        self.right_expression = right_expression

    def __deepcopy__(self, memodict):
        obj = super(FNode, self).__deepcopy__(memodict)
        obj.left_expression = deepcopy(self.left_expression, memodict)
        obj.right_expression = deepcopy(self.right_expression, memodict)
        obj.lookup_type = self.lookup_type
        return obj

    def add_to_query(self, query, aliases):
        # evaluate if it is a query expression
        if hasattr(self.left_expression, 'evaluate'):
            self.left_expression = SQLEvaluator(self.left_expression, query)
        if hasattr(self.right_expression, 'evaluate'):
            self.right_expression = SQLEvaluator(self.right_expression, query)
        query.where.add(FExpression(self.left_expression, self.lookup_type, self.right_expression), self.connector)


def FQ(*args, **kwargs):
    '''
    Wrap FNode in a Q object for it's logical operators
    '''
    return models.Q(FNode(*args, **kwargs))
