import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from .base import Base

__all__ = ("rulebooks", "rulesets", "rules", "Rule", "RuleSet", "RuleBook")

from .mixins import IntIdMixin


class RuleBook(IntIdMixin, Base):
    __tablename__ = "rulebook"

    name = sa.Column(sa.String)
    rulesets = sa.Column(sa.String)
    project_id = sa.Column(
        sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=True
    )


class RuleSet(IntIdMixin, Base):
    __tablename__ = "ruleset"

    rulebook_id = sa.Column(
        sa.ForeignKey("rulebook.id", ondelete="CASCADE"), nullable=False
    )
    name = sa.Column(sa.String)


class Rule(IntIdMixin, Base):
    __tablename__ = "rule"

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
