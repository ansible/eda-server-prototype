import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from .base import Base

__all__ = ("rulebooks", "rulesets", "rules", "Rule", "RuleSet", "RuleBook")


class RuleBook(Base):
    __tablename__ = "rulebook"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    name = sa.Column(sa.String)
    rulesets = sa.Column(sa.String)
    project_id = sa.Column(
        sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=True
    )


class RuleSet(Base):
    __tablename__ = "ruleset"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    rulebook_id = sa.Column(
        sa.ForeignKey("rulebook.id", ondelete="CASCADE"), nullable=False
    )
    name = sa.Column(sa.String)


class Rule(Base):
    __tablename__ = "rule"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    ruleset_id = sa.Column(
        sa.ForeignKey("ruleset.id", ondelete="CASCADE"), nullable=False
    )
    name = sa.Column(sa.String)
    action = sa.Column(postgresql.JSONB(none_as_null=True), nullable=False)


# TODO(cutwater): These tables are for compatibility with existing queries
#  only. They must be removed after queries are updated by using
#  declarative models.
rulebooks = RuleBook.__table__
rulesets = RuleSet.__table__
rules = Rule.__table__
