"""
从视频中截取题目帧和解答帧的脚本
用法：
  python screenshot_from_video.py <bvid> <question_id> <time_question> [time_answer1] [time_answer2] ...
  
示例：
  python screenshot_from_video.py BV16VVnz3EsU q091 00:12:34 00:15:20
  python screenshot_from_video.py BV16VVnz3EsU q091 00:12:34 00:15:20 00:16:45
"""

import subprocess
import os
import sys
import json
import hashlib

# 视频缓存目录（从B站下载的视频会存这里）
VIDEO_CACHE_DIR = r"C:\Users\123\Videos\bilibili"
# 截图输出根目录
OUTPUT_ROOT = r"C:\Users\123\.openclaw\workspace\skills\triangle-tutor\questions"

def get_video_path(bvid: str) -> str:
    """根据BV号查找本地缓存的视频文件"""
    # 支持多种常见格式
    for ext in [".mp4", ".flv", ".mkv", ".avi"]:
        path = os.path.join(VIDEO_CACHE_DIR, f"{bvid}{ext}")
        if os.path.exists(path):
            return path
        # 也可能以 BV号 的一部分命名
        for f in os.listdir(VIDEO_CACHE_DIR):
            if bvid.lower() in f.lower() and f.endswith(ext):
                return os.path.join(VIDEO_CACHE_DIR, f)
    return None


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def extract_frame(video_path: str, timestamp: str, output_path: str, quality: int = 2) -> bool:
    """
    从视频中截取单帧图片
    
    参数：
        video_path: 视频文件路径
        timestamp: 时间戳（格式：HH:MM:SS 或 SS.frac）
        output_path: 输出图片路径
        quality: 质量等级（1=最高质量，2=高质量，3=普通）
    
    返回：是否成功
    """
    if not os.path.exists(video_path):
        print(f"[ERROR] Video not found: {video_path}")
        return False
    
    cmd = [
        "ffmpeg",
        "-ss", timestamp,
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", str(quality),
        "-y",  # 覆盖已存在的文件
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0 and os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"[OK] {output_path} ({size/1024:.1f}KB)")
            return True
        else:
            print(f"[ERROR] ffmpeg failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def generate_meta(question_id: str, bvid: str, timestamps: dict, output_dir: str) -> dict:
    """生成元数据JSON"""
    meta = {
        "question_id": question_id.upper(),
        "source": {
            "type": "video",
            "bv_id": bvid,
            "video_path": get_video_path(bvid),
            "timestamps": timestamps
        },
        "screenshots": {},
        "status": "collected"
    }
    
    # 记录截图文件
    q_file = f"{question_id.lower()}_question.png"
    if os.path.exists(os.path.join(output_dir, q_file)):
        meta["screenshots"]["question"] = q_file
    
    for i, ts in enumerate(timestamps.get("answers", []), 1):
        a_file = f"{question_id.lower()}_answer_{i}.png"
        if os.path.exists(os.path.join(output_dir, a_file)):
            meta["screenshots"]["answers"] = meta["screenshots"].get("answers", [])
            meta["screenshots"]["answers"].append(a_file)
    
    return meta


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    
    bvid = sys.argv[1]
    question_id = sys.argv[2]  # e.g., "q091" or "Q091"
    time_question = sys.argv[3]  # e.g., "00:12:34"
    time_answers = sys.argv[4:] if len(sys.argv) > 4 else []  # 可多个解答帧
    
    # 归一化 question_id
    qid_normalized = question_id.lower().replace("q", "q")  # 保持小写 q 前缀
    
    # 查找视频
    video_path = get_video_path(bvid)
    if not video_path:
        print(f"[ERROR] Video not found for BV: {bvid}")
        print(f"[HINT] Please download the video first or check VIDEO_CACHE_DIR")
        sys.exit(1)
    
    print(f"[INFO] Found video: {video_path}")
    
    # 创建题目文件夹
    # 从 q091 这种格式提取难度目录
    q_num = int(''.join(filter(str.isdigit, question_id)))
    if q_num <= 17:
        diff_folder = "q001-q017"
    elif q_num <= 56:
        diff_folder = "q018-q056"
    elif q_num <= 90:
        diff_folder = "q057-q090"
    elif q_num <= 117:
        diff_folder = "q091-q117"
    else:
        diff_folder = "q118-q150"
    
    output_dir = os.path.join(OUTPUT_ROOT, diff_folder, qid_normalized)
    ensure_dir(output_dir)
    
    print(f"[INFO] Output directory: {output_dir}")
    
    # 截取题目帧
    print(f"\n[Step 1] Capturing question frame at {time_question}...")
    q_output = os.path.join(output_dir, f"{qid_normalized}_question.png")
    q_ok = extract_frame(video_path, time_question, q_output)
    
    # 截取解答帧（可能有多个）
    answer_files = []
    for i, ts in enumerate(time_answers, 1):
        print(f"\n[Step {i+1}] Capturing answer frame {i} at {ts}...")
        a_output = os.path.join(output_dir, f"{qid_normalized}_answer_{i}.png")
        if extract_frame(video_path, ts, a_output):
            answer_files.append(f"{qid_normalized}_answer_{i}.png")
    
    # 生成元数据
    timestamps = {
        "question": time_question,
        "answers": time_answers
    }
    meta = generate_meta(question_id, bvid, timestamps, output_dir)
    
    meta_path = os.path.join(output_dir, f"{qid_normalized}_meta.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"\n[INFO] Meta data saved: {meta_path}")
    
    # 打印摘要
    print("\n" + "=" * 50)
    print(f"Question ID: {question_id.upper()}")
    print(f"Video: {bvid}")
    print(f"Timestamps: {timestamps}")
    print(f"Question frame: {'OK' if q_ok else 'FAILED'}")
    print(f"Answer frames: {len(answer_files)}/{len(time_answers)}")
    print(f"Output: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
