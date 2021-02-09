from typing import Type

from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.sqltypes import String, DateTime, NullType

PY3 = str is not bytes
text = str if PY3 else unicode
int_type = int if PY3 else (int, long)
str_type = str if PY3 else (str, unicode)


class StringLiteral(String):
    '''Teach SA how to literalize various things.'''

    def literal_processor(self, dialect):
        super_processor = super(StringLiteral, self).literal_processor(dialect)

        def process(value):
            if isinstance(value, int_type):
                return text(value)
            if not isinstance(value, str_type):
                value = text(value)
            result = super_processor(value)
            if isinstance(result, bytes):
                result = result.decode(dialect.encoding)
            return result

        return process


class LiteralDialect(DefaultDialect):
    colspecs = {
        # prevent various encoding explosions
        String: StringLiteral,
        # teach SA about how to literalize a datetime
        DateTime: StringLiteral,
        # don't format py2 long integers to NULL
        NullType: StringLiteral,
    }

    @classmethod
    def get_sql_with_var(cls, orm_query: Type[Select]) -> str:
        ''' Функция принимает на вход запрос на ORM
            SQLAlchemy и возврощает сгенерированный чистый SQL.
        '''
        orm_sql = orm_query.compile(
            dialect=cls(),
            compile_kwargs={'literal_binds': True},
        ).string

        result = orm_sql.replace('\n', '')
        return result
