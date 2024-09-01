"""Module with DB tweets' models."""

from typing import Dict, List, Optional

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from database import Base
from likes.models import likes


class Tweet(Base):
    """DB tweet's model."""

    __tablename__ = 'tweets'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime)

    user = relationship('User', back_populates='tweets')
    liked_users = relationship('User', secondary=likes, back_populates='liked_tweets')
    attachments = relationship(
        'Media',
        back_populates='tweet',
        cascade='all, delete-orphan',
    )

    def to_json(self) -> Dict[str, str]:
        """Function of convertation objs to JSON."""
        attachments: List[str] = [''.join(['/static/images/', i_attach.name])
                                  for i_attach in self.attachments
                                  ]
        author: Dict[str, str] = {'id': self.user.id, 'name': self.user.name}
        likes: Optional[List[dict]] = [
            {'user_id': i_user.id, 'name': i_user.name}
            for i_user in self.liked_users
        ]

        return {
            'id': self.id,
            'content': self.content,
            'attachments': attachments,
            'author': author,
            'likes': likes,
        }

    def __repr__(self):
        return f'<Tweet {self.content}>'

    @classmethod
    async def get_tweet_by_id(
        cls,
        session: AsyncSession,
        tweet_id: str,
    ) -> Optional['Tweet']:
        """Function of getting the tweet by id."""
        res = await session.execute(select(Tweet).filter_by(id=tweet_id))
        return res.unique().scalars().one_or_none()
