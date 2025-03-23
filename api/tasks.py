import os
import string

import Levenshtein
import whisper
from opencc.opencc import OpenCC
from simhash import Simhash
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from celery_app import app
from models import Question, Recording

engine = create_engine("sqlite:///./dbs/ai_teacher.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 加载Whisper模型（只需加载一次）
model = whisper.load_model("base")
# 初始化 OpenCC 转换器
converter = OpenCC('t2s')  # 't2s' 表示从繁体到简体的转换


def clean_text(text):
    """去除文本中的空格和标点符号"""
    # 创建中英文标点符号表
    punctuation = string.punctuation + "，。！？、；：""''（）《》【】"
    # 创建转换表，将所有标点和空格映射为空字符串
    trans_table = str.maketrans("", "", punctuation + " ")
    # 应用转换表并返回结果
    return text.translate(trans_table)


def similarity_score(similarity):
    if similarity > 0 and similarity < 0.1:
        score = 10
    elif similarity >= 0.1 and similarity < 0.2:
        score = 20
    elif similarity >= 0.2 and similarity < 0.3:
        score = 30
    elif similarity >= 0.3 and similarity < 0.4:
        score = 40
    elif similarity >= 0.4 and similarity < 0.5:
        score = 50
    elif similarity >= 0.5 and similarity < 0.6:
        score = 60
    elif similarity >= 0.6 and similarity < 0.7:
        score = 70
    elif similarity >= 0.7 and similarity < 0.8:
        score = 80
    elif similarity >= 0.8 and similarity < 0.9:
        score = 90
    else:
        score = 100
    return score


def compute_similarity_simhash(str1, str2):
    hash1 = Simhash(str1)
    hash2 = Simhash(str2)
    # Simhash之间的距离
    distance = hash1.distance(hash2)
    # 转化为相似度（这里假设最大距离为64位）
    similarity = 1 - distance / 64
    print(f"Simhash similarity: {similarity}")
    similarity = similarity * 1.2  # 乘以拉伸系数
    print(f"Simhash similarity after stretch: {similarity}")
    score = similarity_score(similarity)
    print(f"score: {score}")
    return similarity


def compute_similarity_levenshtein(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    similarity = 1 - distance / max(len(str1), len(str2))
    print(f"Levenshtein similarity: {similarity}")
    score = similarity_score(similarity)
    print(f"score: {score}")
    return score


def compute_similarity_dynamic(str1, str2, threshold=100):
    """
    1. **文本长度较短时使用Levenshtein距离**：
        - Levenshtein距离适合短文本，因为它能够精确地计算编辑距离，适用于需要高精度的场景。
        - 对于长度在几十个字符以内的文本，Levenshtein距离通常能够提供更准确的相似度测量。

    2. **文本长度较长时使用SimHash**：
        - SimHash适合处理较长文本和大规模数据，因为它能够快速计算并比较文本的指纹。
        - 当文本长度超过几百个字符时，SimHash的效率和处理能力更为突出，尤其是在需要处理大量文本时。
    """

    if len(str1) < threshold and len(str2) < threshold:
        # 使用Levenshtein距离
        return compute_similarity_levenshtein(str1, str2)
    else:
        return compute_similarity_simhash(str1, str2)


@app.task
def check_audio_file(recording_id: int):
    # 获取数据库会话
    db = SessionLocal()
    try:
        # 获取录音记录
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording:
            return {"error": "Recording not found"}

        question = db.execute(
            select(Question.id, Question.title, Question.content)
            .where(Question.id == recording.question_id)
        )
        question_result = question.first()
        if not question_result:
            return {"error": "Question not found"}

        question_content = clean_text(question_result.content)
        print(f"question_content: {question_content}")

        # 构建音频文件路径
        audio_path = os.path.join("uploads", recording.filename)
        if not os.path.exists(audio_path):
            return {"error": "Audio file not found"}
        
        try:
            # 使用Whisper进行语音转文本
            result = model.transcribe(audio_path, fp16=False, language="Chinese")
            transcribed_text = result["text"]
            transcribed_text = clean_text(transcribed_text)
            # 转换为简体中文
            transcribed_text = converter.convert(transcribed_text)
            print(f"transcribed_text: {transcribed_text}")

            score = compute_similarity_dynamic(transcribed_text, question_content)

            # 更新数据库
            recording.check_result = "checked"
            recording.score = score
            db.commit()

            # 删除音频文件
            try:
                os.remove(audio_path)
            finally:
                pass

            return {
                "status": "success",
                "recording_id": recording_id,
                "score": score
            }
        except Exception as e:
            recording.check_result = f"Transcription failed: {str(e)}"
            recording.score = 0
            db.commit()
            return {"error": f"Transcription failed: {str(e)}"}

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
