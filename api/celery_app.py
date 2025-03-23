from datetime import datetime

from celery import Celery
from sqlalchemy import Column, DateTime, Integer, PickleType, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base

# 使用SQLite作为broker和backend
BROKER_URL = 'sqla+sqlite:///dbs/celery_broker.db'
BACKEND_URL = 'db+sqlite:///dbs/celery_backend.db'

app = Celery(
    'audio_check',
    broker=BROKER_URL,
    backend=BACKEND_URL
)

# 创建必要的数据库表
engine = create_engine(BROKER_URL.replace('sqla+', ''))
Base = declarative_base()


class CeleryTaskMeta(Base):
    __tablename__ = 'celery_taskmeta'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(155), unique=True)
    status = Column(String(50))
    result = Column(PickleType, nullable=True)
    date_done = Column(DateTime, default=datetime.utcnow)
    traceback = Column(Text, nullable=True)


class CeleryTaskSetMeta(Base):
    __tablename__ = 'celery_tasksetmeta'

    id = Column(Integer, primary_key=True)
    taskset_id = Column(String(155), unique=True)
    result = Column(PickleType, nullable=True)
    date_done = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)

# 任务配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    broker_transport_options={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.5,
    },
    task_time_limit=1200,  # 20分钟超时
    task_soft_time_limit=1080,  # 18分钟软超时
)
