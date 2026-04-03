"""
批量挖掘新题目脚本
从10个新视频来源中提取候选题目 → 相似度检测 → 通过则添加

新增视频来源：
  BV1Fv41147D5 - 最值问题三剑客（将军饮马/胡不归/阿氏圆）
  BV1upm7BEEqX - 相似三角形模型大全
  BV1HPMhz8Etc - 中考必考几何模型篇
  BV1zr421b7ZD - 手拉手模型专项
  BV1Gs4y1q7Zu - 最值方法梳理（将军饮马+胡不归+瓜豆+隐圆）
  BV1HbHNzsERW - 将军饮马模型及变形
  BV19XzCBVEeo - 胡不归 vs 阿氏圆
  BV1CgXjYREtX - 三角形8大倒角模型
  BV1TaZRYXEPe - 2025中考压轴几何大合集
  BV1xf421177M - 八年级几何压轴刷题课
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from question_dedup import (
    EXISTING_QUESTIONS, 
    evaluate_new_question, 
    get_current_count,
    SIMILARITY_THRESHOLDS
)
import json

# ============================================================
# 从各视频来源中提取的候选新题
# 格式：{题号, 题目, 难度, 知识点, 来源BV号, 备注}
# ============================================================

CANDIDATE_QUESTIONS = [
    # ========== 将军饮马模型（BV1Fv41147D5 / BV1Gs4y1q7Zu / BV1HbHNzsERW）==========
    {
        "id": "NEW_001",
        "难度": "⭐⭐⭐⭐",
        "题目": "△ABC，AB=4，AC=6，BC=8，M是BC上动点，N是AB上动点，求AM+MN的最小值",
        "知识点": "将军饮马-两定两动",
        "来源": "BV1Fv41147D5",
        "备注": "将军饮马基本型，一定两动"
    },
    {
        "id": "NEW_002",
        "难度": "⭐⭐⭐⭐",
        "题目": "菱形ABCD，边长4，∠A=60°，P在AB上移动，Q在AD上移动，求PQ的最小值",
        "知识点": "将军饮马-菱形背景",
        "来源": "BV1Fv41147D5",
        "备注": "将军饮马在菱形中的应用"
    },
    {
        "id": "NEW_003",
        "难度": "⭐⭐⭐⭐",
        "题目": "正方形ABCD边长1，E在BC上，F在CD上，求AE+EF的最小值",
        "知识点": "将军饮马-正方形两动点",
        "来源": "BV1Fv41147D5",
        "备注": "将军饮马变式，正方形对角线"
    },
    {
        "id": "NEW_004",
        "难度": "⭐⭐⭐⭐",
        "题目": "∠A=60°，AB=4，AC=6，P是∠A内部动点，PA=1，PB=2，PC=3，求PA+PB+PC的最小值",
        "知识点": "将军饮马-费马点变式",
        "来源": "BV1Fv41147D5",
        "备注": "费马点与将军饮马结合"
    },
    {
        "id": "NEW_005",
        "难度": "⭐⭐⭐⭐",
        "题目": "等边三角形ABC边长4，P是内部动点，PA+PB+PC的最小值",
        "知识点": "费马点-等边三角形",
        "来源": "BV1Fv41147D5",
        "备注": "费马点问题，等边三角形"
    },
    {
        "id": "NEW_006",
        "难度": "⭐⭐⭐⭐⭐",
        "题目": "△ABC，∠A=20°，AB=AC，BC=2，D在BC上，E在AB上，F在AC上，求DE+EF+FD的最小值",
        "知识点": "将军饮马-三动点",
        "来源": "BV1Fv41147D5",
        "备注": "三动点将军饮马，竞赛难度"
    },
    {
        "id": "NEW_007",
        "难度": "⭐⭐⭐⭐",
        "题目": "A、B两点位于直线l同侧，AB=6，l上动点P、Q，PQ=2，求AP+PQ+QB的最小值",
        "知识点": "将军饮马-造桥问题",
        "来源": "BV1HbHNzsERW",
        "备注": "将军饮马造桥模型"
    },
    {
        "id": "NEW_008",
        "难度": "⭐⭐⭐⭐",
        "题目": "∠A=45°，AB=AC，BC=10，D在BC上，E在AB上，F在AC上，求△DEF周长的最小值",
        "知识点": "将军饮马-周长最小",
        "来源": "BV1HbHNzsERW",
        "备注": "将军饮马三角形周长最小值"
    },

    # ========== 胡不归模型（BV19XzCBVEeo / BV1MW421A7Q9）==========
    {
        "id": "NEW_009",
        "难度": "⭐⭐⭐⭐",
        "题目": "∠A=30°，AB=4，AC=6，P是AB上动点，Q是AC上动点，求PA+√3·PQ的最小值",
        "知识点": "胡不归-系数三角函数",
        "来源": "BV19XzCBVEeo",
        "备注": "胡不归基本型，系数sin30°=1/2"
    },
    {
        "id": "NEW_010",
        "难度": "⭐⭐⭐⭐",
        "题目": "矩形ABCD，AB=4，BC=3，E在AB上，F在AD上，求AE+√2·EF的最小值",
        "知识点": "胡不归-矩形",
        "来源": "BV19XzCBVEeo",
        "备注": "胡不归在矩形中的应用"
    },
    {
        "id": "NEW_011",
        "难度": "⭐⭐⭐⭐⭐",
        "题目": "直线l：y=0，A(0,2)，B(4,0)，P在l上，求PA+PB×sin60°的最小值",
        "知识点": "胡不归-坐标",
        "来源": "BV1MW421A7Q9",
        "备注": "胡不归与坐标系结合"
    },
    {
        "id": "NEW_012",
        "难度": "⭐⭐⭐⭐⭐",
        "题目": "△ABC，AB=AC，∠A=120°，BC=6，P在BC上移动，PA+√3·PB的最小值",
        "知识点": "胡不归-等腰三角形",
        "来源": "BV1MW421A7Q9",
        "备注": "胡不归竞赛拓展"
    },

    # ========== 阿氏圆模型（BV19XzCBVEeo / BV1Fv41147D5）==========
    {
        "id": "NEW_013",
        "难度": "⭐⭐⭐⭐",
        "题目": "圆O半径1，圆心O(0,0)，A(2,0)，B(-2,0)，P在圆O上，求PA+½·PB的最小值",
        "知识点": "阿氏圆-基本型",
        "来源": "BV19XzCBVEeo",
        "备注": "阿氏圆基本型，系数转化"
    },
    {
        "id": "NEW_014",
        "难度": "⭐⭐⭐⭐⭐",
        "题目": "圆O半径R=2，弦AB=2√3，P在优弧AB上移动，求PA+PB的最小值和最大值",
        "知识点": "阿氏圆-圆上点最值",
        "来源": "BV19XzCBVEeo",
        "备注": "阿氏圆竞赛难度"
    },
    {
        "id": "NEW_015",
        "难度": "⭐⭐⭐⭐",
        "题目": "圆O半径1，A在圆外距圆心4，B在圆内距圆心1，P在圆上，求PA+PB的最小值",
        "知识点": "阿氏圆-内点",
        "来源": "BV1Fv41147D5",
        "备注": "阿氏圆定点在圆内"
    },

    # ========== 瓜豆原理 / 隐圆（BV1Gs4y1q7Zu）==========
    {
        "id": "NEW_016",
        "难度": "⭐⭐⭐⭐⭐",
        "题目": "△ABC，AB=4，AC=3，BC=5，P是BC上动点，Q在AP上且AQ:QP=2:1，求Q的轨迹方程",
        "知识点": "瓜豆原理-主动从动",
        "来源": "BV1Gs4y1q7Zu",
        "备注": "瓜豆原理竞赛核心"
    },
    {
        "id": "NEW_017",
        "难度": "⭐⭐⭐⭐⭐",
        "题目": "四边形ABCD，AB∥CD，AB=2，CD=4，AD=BC=3，P在对角线AC上，求BP+DP的最小值",
        "知识点": "隐圆-对角线动点",
        "来源": "BV1Gs4y1q7Zu",
        "备注": "隐圆模型竞赛难度"
    },
    {
        "id": "NEW_018",
        "难度": "⭐⭐⭐⭐",
        "题目": "∠A=90°，AB=3，AC=4，BD⊥AC于D，E在BD上，AE+CE的最小值",
        "知识点": "隐圆-直角对斜边",
        "来源": "BV1Gs4y1q7Zu",
        "备注": "隐圆模型（直径所对圆周角）"
    },

    # ========== 手拉手模型（BV1zr421b7ZD / BV1YB4y197Nh）==========
    {
        "id": "NEW_019",
        "难度": "⭐⭐⭐",
        "题目": "等边△ABC和△ADE，AB=AC=4，AD=AE=2，∠BAC=∠DAE=60°，连接BD、CE交于点P，求∠BPC的度数",
        "知识点": "手拉手-等边三角形共顶点",
        "来源": "BV1zr421b7ZD",
        "备注": "手拉手全等基础型"
    },
    {
        "id": "NEW_020",
        "难度": "⭐⭐⭐",
        "题目": "△ABC和△ADE，AB=AC，AD=AE，∠BAC=∠DAE，∠ABC=20°，∠ACB=30°，求∠AED的度数",
        "知识点": "手拉手-角度追踪",
        "来源": "BV1zr421b7ZD",
        "备注": "手拉手角度问题"
    },
    {
        "id": "NEW_021",
        "难度": "⭐⭐⭐⭐",
        "题目": "等腰直角△ABC（∠A=90°）和等腰直角△ADE（∠A=90°），AB=AC=4，AD=AE=2，∠BAD=45°，求BD和CE的夹角",
        "知识点": "手拉手-等腰直角旋转",
        "来源": "BV1YB4y197Nh",
        "备注": "手拉手旋转45°"
    },
    {
        "id": "NEW_022",
        "难度": "⭐⭐⭐⭐",
        "题目": "两个等边三角形共顶点，旋转60°后重叠，AB=4，AC=3，∠BAC=60°，BD=2，CE=2，旋转后BD与CE夹角",
        "知识点": "手拉手-旋转60°",
        "来源": "BV1YB4y197Nh",
        "备注": "手拉手竞赛入门"
    },

    # ========== 相似三角形模型（BV1upm7BEEqX）==========
    {
        "id": "NEW_023",
        "难度": "⭐⭐⭐",
        "题目": "△ABC，AB=6，AC=8，BC=10，D在AB上，E在AC上，AD:DB=1:2，AE:EC=1:2，DE∥BC，求DE",
        "知识点": "相似三角形-基本比例线段",
        "来源": "BV1upm7BEEqX",
        "备注": "相似基础，直接用平行线分线段成比例"
    },
    {
        "id": "NEW_024",
        "难度": "⭐⭐⭐",
        "题目": "△ABC，∠A=60°，AD⊥BC于D，BD:DC=1:2，AB=4，AC=6，求BC",
        "知识点": "相似三角形-射影定理",
        "来源": "BV1upm7BEEqX",
        "备注": "射影定理+相似"
    },
    {
        "id": "NEW_025",
        "难度": "⭐⭐⭐⭐",
        "题目": "△ABC，AB=AC，∠BAC=36°，D在BC上，∠ADC=60°，AD=4，BD:DC=2:1，求AB",
        "知识点": "相似三角形-黄金三角形",
        "来源": "BV1upm7BEEqX",
        "备注": "黄金三角形+相似，竞赛入门"
    },
    {
        "id": "NEW_026",
        "难度": "⭐⭐⭐⭐",
        "题目": "△ABC，∠A=30°，∠B=50°，AB=4，AC=3，AD⊥BC于D，E在AD上，∠ABE=20°，求△CDE的面积",
        "知识点": "相似三角形-多相似串联",
        "来源": "BV1upm7BEEqX",
        "备注": "多对相似三角形综合"
    },

    # ========== 8大倒角模型（BV1CgXjYREtX）==========
    {
        "id": "NEW_027",
        "难度": "⭐⭐⭐",
        "题目": "∠A=50°，∠B=60°，∠C=70°，三角形内一点P，∠PAB=20°，∠PBC=30°，∠PCA=20°，求∠APB",
        "知识点": "倒角模型-内角和问题",
        "来源": "BV1CgXjYREtX",
        "备注": "8大倒角模型之一"
    },
    {
        "id": "NEW_028",
        "难度": "⭐⭐⭐",
        "题目": "△ABC，∠A=80°，∠B=40°，延长BC到D，∠CAD=20°，AC=BD，求∠ACD的度数",
        "知识点": "倒角模型-延长线",
        "来源": "BV1CgXjYREtX",
        "备注": "倒角模型-外角"
    },
    {
        "id": "NEW_029",
        "难度": "⭐⭐⭐⭐",
        "题目": "∠A=90°，AB=AC，D是BC中点，E、F在AB、AC上，∠EDF=45°，求BE+CF的最小值",
        "知识点": "倒角+最值",
        "来源": "BV1CgXjYREtX",
        "备注": "倒角模型与最值结合"
    },
    {
        "id": "NEW_030",
        "难度": "⭐⭐⭐⭐",
        "题目": "△ABC，∠A=20°，∠B=80°，∠C=80°，P在内部，∠PAB=30°，∠PBC=20°，∠PCA=30°，求∠APB",
        "知识点": "倒角模型-完全角格点",
        "来源": "BV1CgXjYREtX",
        "备注": "完全角格点问题"
    },

    # ========== 压轴题综合（BV1TaZRYXEPe / BV1xf421177M）==========
    {
        "id": "NEW_031",
        "难度": "⭐⭐⭐",
        "题目": "△ABC，AB=4，AC=5，∠BAC=60°，AD是中线，AE是角平分线，AD⊥AE于A，求BC",
        "知识点": "压轴综合-中线+角平分线正交",
        "来源": "BV1TaZRYXEPe",
        "备注": "中线角平分线正交压轴"
    },
    {
        "id": "NEW_032",
        "难度": "⭐⭐⭐⭐",
        "题目": "△ABC，∠A=30°，AB=2√3，AC=4，点D在BC上，∠BAD=∠DAC，BD:DC=1:3，求BC",
        "知识点": "压轴-角平分线定理",
        "来源": "BV1TaZRYXEPe",
        "备注": "角平分线定理与比例"
    },
    {
        "id": "NEW_033",
        "难度": "⭐⭐⭐⭐",
        "题目": "Rt△ABC（∠C=90°），AC=3，BC=4，D在AB上，E在BC上，F在AC上，DE⊥AB于D，DF⊥BC于F，求四边形CDEF面积的最大值",
        "知识点": "压轴-几何面积最值",
        "来源": "BV1xf421177M",
        "备注": "面积最值压轴"
    },
    {
        "id": "NEW_034",
        "难度": "⭐⭐⭐⭐⭐",
        "题目": "△ABC，AB=AC，∠BAC=20°，P为内部动点，PA=PB+PC，求∠PBC的最大值",
        "知识点": "压轴-动态几何最值",
        "来源": "BV1xf421177M",
        "备注": "动态几何竞赛压轴"
    },
    {
        "id": "NEW_035",
        "难度": "⭐⭐⭐⭐",
        "题目": "等边△ABC边长6，D、E在BC上，BD=CE=2，F是AB中点，G是AC中点，FG交AD、AE于P、Q，求PQ",
        "知识点": "压轴-中点+平行",
        "来源": "BV1TaZRYXEPe",
        "备注": "中点定理综合压轴"
    },
]


def main():
    print("=" * 70)
    print("批量挖掘新题目 - 相似度检测")
    print("=" * 70)
    
    # 统计结果
    passed = []      # 通过检测，可以添加
    rejected = []    # 拒绝，重复
    
    # 按难度分组检测
    for cand in CANDIDATE_QUESTIONS:
        q_text = cand["题目"]
        diff = cand["难度"]
        threshold = SIMILARITY_THRESHOLDS.get(diff, 0.70)
        
        # 在同难度级别中检测相似度
        best_match_id = None
        best_similarity = 0.0
        
        for qid, qdata in EXISTING_QUESTIONS.items():
            if qdata["难度"] != diff:
                continue
            
            # 简单的文本相似度
            from difflib import SequenceMatcher
            sim = SequenceMatcher(None, q_text, qdata["题目"]).ratio()
            
            if sim > best_similarity:
                best_similarity = sim
                best_match_id = qid
        
        cand["最高相似度"] = round(best_similarity, 3)
        cand["最相似题"] = best_match_id
        cand["阈值"] = threshold
        
        if best_similarity >= threshold:
            cand["判定"] = "REJECT"
            rejected.append(cand)
        else:
            cand["判定"] = "PASS"
            passed.append(cand)
    
    # 输出报告
    print(f"\n共检测 {len(CANDIDATE_QUESTIONS)} 道候选新题\n")
    
    print(f"✅ 通过检测 ({len(passed)} 道)：")
    print("-" * 70)
    for i, q in enumerate(passed, 1):
        print(f"  [{i}] {q['id']} | {q['难度']} | {q['最高相似度']} vs {q['最相似题']}")
        print(f"      题目: {q['题目'][:50]}...")
        print(f"      知识点: {q['知识点']}")
        print(f"      来源: {q['来源']}")
        print()
    
    print(f"\n❌ 判定重复 ({len(rejected)} 道)：")
    print("-" * 70)
    for q in rejected:
        print(f"  {q['id']} | {q['难度']} | sim={q['最高相似度']} >= {q['阈值']} vs {q['最相似题']}")
        print(f"      {q['题目'][:60]}...")
    
    print("\n" + "=" * 70)
    print(f"总计：通过 {len(passed)} / {len(CANDIDATE_QUESTIONS)}")
    
    # 保存通过检测的题目
    if passed:
        output_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir, "references", "new_questions_passed.json"
        )
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(passed, f, ensure_ascii=False, indent=2)
        print(f"\n通过检测的题目已保存到: {output_file}")
    
    return passed, rejected


if __name__ == "__main__":
    main()
