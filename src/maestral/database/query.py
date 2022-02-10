"""
SQL query definitions that facilitate writing object-oriented code to generate SQL
queries.
"""

import os
from typing import Tuple, Sequence, Iterator, List, TYPE_CHECKING

from .types import SqlPath, ColumnValueType

if TYPE_CHECKING:
    from .orm import Column


class Query:
    """Base type for query"""

    def clause(self) -> Tuple[str, Sequence[ColumnValueType]]:
        """
        Generate the corresponding SQL clause.

        :returns: SQL clause and arguments to substitute.
        """
        raise NotImplementedError()


class PathTreeQuery(Query):
    """
    Query for an entire subtree at the given path.

    :param column: Column to match.
    :param path: Root path for the subtree.
    """

    def __init__(self, column: "Column", path: str):

        if not isinstance(column.type, SqlPath):
            raise ValueError("Only accepts columns with type SqlPath")

        self.column = column
        self.file_blob = os.fsencode(path)
        self.dir_blob = os.path.join(self.file_blob, b"")

    def clause(self):
        query_part = f"({self.column.name} = ? OR substr({self.column.name}, 1, ?) = ?)"
        args = (self.file_blob, len(self.dir_blob), self.dir_blob)

        return query_part, args


class MatchQuery(Query):
    """
    Query to match an exact value.

    :param column: Column to match.
    :param value: Value to match.
    """

    def __init__(self, column: "Column", value: ColumnValueType):
        self.column = column
        self.value = value

    def clause(self):
        args = (self.column.py_to_sql(self.value),)
        return f"{self.column.name} = ?", args


class AllQuery(Query):
    """
    Query to match everything.
    """

    def clause(self):
        return "TRUE", ()


class CollectionQuery(Query):
    """An abstract query class that aggregates other queries. Can be
    indexed like a list to access the sub-queries.

    :param subqueries: Subqueries to aggregate.
    """

    def __init__(self, *subqueries: Query):
        self.subqueries = subqueries

    # Act like a sequence.

    def __len__(self) -> int:
        return len(self.subqueries)

    def __getitem__(self, key: int) -> Query:
        return self.subqueries[key]

    def __iter__(self) -> Iterator[Query]:
        return iter(self.subqueries)

    def __contains__(self, item: Query) -> bool:
        return item in self.subqueries

    def clause_with_joiner(self, joiner: str) -> Tuple[str, Sequence[ColumnValueType]]:
        """Return a clause created by joining together the clauses of
        all subqueries with the string joiner (padded by spaces).
        """
        clause_parts = []
        subvals: List[ColumnValueType] = []

        for subq in self.subqueries:
            subq_clause, subq_subvals = subq.clause()
            clause_parts.append("(" + subq_clause + ")")
            subvals += subq_subvals

        clause = (" " + joiner + " ").join(clause_parts)
        return clause, subvals

    def clause(self):
        raise NotImplementedError()


class AndQuery(CollectionQuery):
    """A conjunction of a list of other queries."""

    def clause(self):
        return self.clause_with_joiner("AND")


class OrQuery(CollectionQuery):
    """A conjunction of a list of other queries."""

    def clause(self):
        return self.clause_with_joiner("OR")


class NotQuery(Query):
    """A query that matches the negation of its `subquery`, as a shorcut for
    performing `not(subquery)` without using regular expressions.

    :param subquery: Query to negate.
    """

    def __init__(self, subquery: Query):
        self.subquery = subquery

    def clause(self):
        clause, subvals = self.subquery.clause()
        if clause:
            return f"not ({clause})", subvals
        else:
            # If there is no clause, there is nothing to negate. All the logic
            # is handled by match() for slow queries.
            return clause, subvals
