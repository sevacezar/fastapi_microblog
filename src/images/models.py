"""Module with DB medias' models."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Media(Base):
    """DB media's model."""

    __tablename__ = 'medias'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tweet_id = Column(Integer, ForeignKey('tweets.id'), nullable=True)
    tweet = relationship('Tweet', back_populates='attachments')

    def __repr__(self):
        return f'{self.id}, {self.name}'
