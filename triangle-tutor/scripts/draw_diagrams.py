"""
生成三角形几何题图
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR = r"C:\Users\123\.openclaw\workspace\skills\triangle-tutor\questions\images"
os.makedirs(OUT_DIR, exist_ok=True)

# 尝试加载中文字体
def get_font(size=20):
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",     # 黑体
        "C:/Windows/Fonts/simsun.ttc",     # 宋体
    ]
    for p in font_paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

FONT = get_font(18)
FONT_SM = get_font(14)
FONT_LG = get_font(24)

WHITE = "white"
BLACK = "black"
GRAY = "gray"
RED = "red"
BLUE = "blue"
GREEN = "green"
ORANGE = "orange"

def new_img(w=800, h=600, bg=WHITE):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)

def draw_point(draw, x, y, r=5, color=BLACK):
    draw.ellipse([x-r, y-r, x+r, y+r], fill=color, outline=color)

def draw_line(draw, x1, y1, x2, y2, color=BLACK, width=2):
    draw.line([x1, y1, x2, y2], fill=color, width=width)

def draw_text(draw, text, x, y, font=None, color=BLACK, anchor="mm"):
    if font is None:
        font = FONT
    draw.text((x, y), text, fill=color, font=font, anchor=anchor)

def draw_triangle(draw, pts, labels=None, side_labels=None, color=BLACK, width=2):
    """pts: [(x,y), (x,y), (x,y)] 逆时针/顺时针"""
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i+1)%n]
        draw_line(draw, x1, y1, x2, y2, color=color, width=width)
    # 顶点
    for x, y in pts:
        draw_point(draw, x, y, r=5, color=color)
    # 标签
    if labels:
        for i, (x, y) in enumerate(pts):
            offset = 20
            # 根据位置调整偏移
            angle = (i * 120 - 90) % 360
            dx = offset * (1 if angle < 180 else -1) * 0.3
            dy = offset * (0.5 if angle < 180 else -0.5)
            if len(labels[i]) > 1:
                dy -= 10
            draw_text(draw, labels[i], x + (25 if x > 400 else -25), y + (20 if y < 300 else -30), FONT_LG, color)
    # 边标签
    if side_labels:
        for i in range(3):
            x1, y1 = pts[i]
            x2, y2 = pts[(i+1)%3]
            mx, my = (x1+x2)//2, (y1+y2)//2
            offset_dir = [(0,-15), (15,5), (-20,5)][i]
            draw_text(draw, side_labels[i], mx+offset_dir[0], my+offset_dir[1], FONT_SM, BLUE)


# ============================================================
# 图001: 一般三角形（含中线）
# ============================================================
def make_img001():
    img, draw = new_img(700, 500)
    # A顶，B左下，C右下
    pts = [(350, 80), (100, 400), (600, 400)]
    labels = ["A", "B", "C"]
    side_labels = ["c", "a", "b"]
    draw_triangle(draw, pts, labels, side_labels)
    # D是BC中点
    D = ((pts[1][0]+pts[2][0])//2, (pts[1][1]+pts[2][1])//2)
    draw_point(draw, D[0], D[1], r=5, color=RED)
    draw_line(draw, pts[0][0], pts[0][1], D[0], D[1], color=RED, width=2)
    draw_text(draw, "D", D[0]+20, D[1]-15, FONT_LG, RED)
    # 标注BC的中点关系
    draw_text(draw, "BD = DC", 350, 450, FONT_SM, GRAY)
    # 标题
    draw_text(draw, "图001：三角形ABC，AD为BC上的中线", 350, 30, FONT_LG, BLACK)
    img.save(os.path.join(OUT_DIR, "img001.png"))

# ============================================================
# 图002: 等腰三角形 ABC, AB=AC
# ============================================================
def make_img002():
    img, draw = new_img(700, 500)
    # A顶，B左，C右，AB=AC
    pts = [(350, 80), (120, 380), (580, 380)]
    labels = ["A", "B", "C"]
    side_labels = ["", "", ""]
    draw_triangle(draw, pts, labels, side_labels)
    # 标注等边
    draw_text(draw, "AB = AC", 200, 230, FONT_SM, BLUE)
    # E在AB上，F在AC上
    E = (pts[0][0] + (pts[1][0]-pts[0][0])*0.4, pts[0][1] + (pts[1][1]-pts[0][1])*0.4)
    F = (pts[0][0] + (pts[2][0]-pts[0][0])*0.4, pts[0][1] + (pts[2][1]-pts[0][1])*0.4)
    draw_point(draw, E[0], E[1], r=4, color=GREEN)
    draw_point(draw, F[0], F[1], r=4, color=GREEN)
    draw_text(draw, "E", E[0]-20, E[1]-10, FONT_SM, GREEN)
    draw_text(draw, "F", F[0]+15, F[1]-10, FONT_SM, GREEN)
    draw_text(draw, "AE = AF", 200, 320, FONT_SM, GREEN)
    # 虚线EF（平行于BC）
    draw_line(draw, E[0], E[1], F[0], F[1], color=ORANGE, width=2)
    draw_text(draw, "EF ∥ BC", 280, 310, FONT_SM, ORANGE)
    draw_text(draw, "图002：等腰△ABC，E、F为AB、AC上点，AE=AF", 350, 30, FONT_LG, BLACK)
    img.save(os.path.join(OUT_DIR, "img002.png"))

# ============================================================
# 图003: 直角三角形 + 勾股定理
# ============================================================
def make_img003():
    img, draw = new_img(800, 450)
    # 直角在A，左下角
    pts = [(100, 350), (650, 350), (100, 100)]
    labels = ["A", "B", "C"]
    # 画直角符号
    draw_line(draw, pts[0][0], pts[0][1], pts[0][0]+40, pts[0][1], color=BLACK, width=2)
    draw_line(draw, pts[0][0], pts[0][1], pts[0][0], pts[0][1]-40, color=BLACK, width=2)
    # 画三角形（直角在左下）
    draw_line(draw, pts[0][0], pts[0][1], pts[1][0], pts[1][1], color=BLACK, width=2)  # AB
    draw_line(draw, pts[0][0], pts[0][1], pts[2][0], pts[2][1], color=BLACK, width=2)  # AC
    draw_line(draw, pts[1][0], pts[1][1], pts[2][0], pts[2][1], color=BLACK, width=2)  # BC
    # 顶点
    for x, y in pts:
        draw_point(draw, x, y, r=5, color=BLACK)
    # 标签
    draw_text(draw, "A", pts[0][0]-25, pts[0][1]+10, FONT_LG, BLACK)
    draw_text(draw, "B", pts[1][0]+10, pts[1][1]+10, FONT_LG, BLACK)
    draw_text(draw, "C", pts[2][0]-25, pts[2][1]-10, FONT_LG, BLACK)
    # 边标签
    draw_text(draw, "a", (pts[0][0]+pts[1][0])//2+10, pts[0][1]+20, FONT_LG, BLUE)  # AB = a
    draw_text(draw, "b", pts[0][0]-30, (pts[0][1]+pts[2][1])//2, FONT_LG, BLUE)   # AC = b
    draw_text(draw, "c", (pts[1][0]+pts[2][0])//2+10, (pts[1][1]+pts[2][1])//2+10, FONT_LG, BLUE)  # BC = c
    # 勾股定理公式
    draw.rectangle([550, 60, 780, 120], outline=GRAY, width=1)
    draw_text(draw, "勾股定理：a² + b² = c²", 665, 90, FONT_SM, BLACK)
    draw_text(draw, "图003：直角三角形ABC，∠A = 90°", 400, 25, FONT_LG, BLACK)
    img.save(os.path.join(OUT_DIR, "img003.png"))

# ============================================================
# 图004: 全等三角形 SSS
# ============================================================
def make_img004():
    img, draw = new_img(900, 400)
    # △ABC
    pts1 = [(150, 80), (50, 320), (280, 320)]
    # △DEF（对齐放置）
    pts2 = [(550, 80), (450, 320), (680, 320)]
    # 画第一个三角形
    for i in range(3):
        x1, y1 = pts1[i]; x2, y2 = pts1[(i+1)%3]
        draw_line(draw, x1, y1, x2, y2, color=BLACK, width=2)
    for x, y in pts1:
        draw_point(draw, x, y, r=5, color=BLACK)
    labels1 = ["A", "B", "C"]
    offsets1 = [(10, -25), (-25, 10), (10, 10)]
    for i, (x, y) in enumerate(pts1):
        draw_text(draw, labels1[i], x+offsets1[i][0], y+offsets1[i][1], FONT_LG, BLACK)
    # 边标签
    mid1 = [(pts1[0][0]+pts1[1][0])//2+5, (pts1[0][1]+pts1[1][1])//2]
    mid2 = [(pts1[1][0]+pts1[2][0])//2, (pts1[1][1]+pts1[2][1])//2+10]
    mid3 = [(pts1[2][0]+pts1[0][0])//2+5, (pts1[2][1]+pts1[0][1])//2+5]
    draw_text(draw, "c", mid1[0], mid1[1], FONT_SM, BLUE)
    draw_text(draw, "a", mid2[0], mid2[1], FONT_SM, BLUE)
    draw_text(draw, "b", mid3[0], mid3[1], FONT_SM, BLUE)
    # 画第二个三角形
    for i in range(3):
        x1, y1 = pts2[i]; x2, y2 = pts2[(i+1)%3]
        draw_line(draw, x1, y1, x2, y2, color=BLACK, width=2)
    for x, y in pts2:
        draw_point(draw, x, y, r=5, color=BLACK)
    labels2 = ["D", "E", "F"]
    offsets2 = [(10, -25), (-25, 10), (10, 10)]
    for i, (x, y) in enumerate(pts2):
        draw_text(draw, labels2[i], x+offsets2[i][0], y+offsets2[i][1], FONT_LG, BLACK)
    # 边标签
    mid1b = [(pts2[0][0]+pts2[1][0])//2+5, (pts2[0][1]+pts2[1][1])//2]
    mid2b = [(pts2[1][0]+pts2[2][0])//2, (pts2[1][1]+pts2[2][1])//2+10]
    mid3b = [(pts2[2][0]+pts2[0][0])//2+5, (pts2[2][1]+pts2[0][1])//2+5]
    draw_text(draw, "c", mid1b[0], mid1b[1], FONT_SM, BLUE)
    draw_text(draw, "a", mid2b[0], mid2b[1], FONT_SM, BLUE)
    draw_text(draw, "b", mid3b[0], mid3b[1], FONT_SM, BLUE)
    # 大括号标注对应边
    bx = 310; by1 = 80; by2 = 320
    draw_line(draw, bx, by1, bx, by2, color=RED, width=2)
    for yy in range(by1, by2, 10):
        draw_line(draw, bx, yy, bx+5 if (yy-by1)//10%2==0 else bx, yy, color=RED, width=1)
    draw_text(draw, "SSS", 320, 200, FONT_LG, RED)
    draw_text(draw, "△ABC ≅ △DEF", 450, 370, FONT_LG, BLACK)
    draw_text(draw, "图004：SSS全等三角形", 450, 25, FONT_LG, BLACK)
    img.save(os.path.join(OUT_DIR, "img004.png"))

# ============================================================
# 图005: 等边三角形
# ============================================================
def make_img005():
    img, draw = new_img(700, 500)
    # 等边三角形，顶点在正上方
    h = 350 * 0.866  # √3/2
    pts = [(350, 80), (350-h, 350+80-h+50), (350+h, 350+80-h+50)]
    labels = ["A", "B", "C"]
    draw_triangle(draw, pts, labels)
    # 各边等长标注
    draw_text(draw, "AB = BC = CA", 350, 430, FONT_SM, BLUE)
    draw_text(draw, "各内角 = 60°", 350, 455, FONT_SM, BLUE)
    # 角的弧线
    cx, cy, r = 350, 80, 30
    draw.arc([cx-r, cy-r, cx+r, cy+r], 30, 90, fill=BLACK, width=2)
    draw_text(draw, "60°", cx+15, cy-25, FONT_SM, BLACK)
    draw_text(draw, "图005：等边三角形ABC", 350, 30, FONT_LG, BLACK)
    img.save(os.path.join(OUT_DIR, "img005.png"))

# ============================================================
# 图006: 角平分线
# ============================================================
def make_img006():
    img, draw = new_img(700, 500)
    # 角BAC，顶点在左上方
    A = (150, 100)
    B = (600, 400)
    C = (150, 400)
    # 画角的两边
    draw_line(draw, A[0], A[1], B[0], B[1], color=BLACK, width=2)
    draw_line(draw, A[0], A[1], C[0], C[1], color=BLACK, width=2)
    draw_point(draw, A[0], A[1], r=5, color=BLACK)
    draw_text(draw, "A", A[0]-25, A[1]-15, FONT_LG, BLACK)
    draw_text(draw, "B", B[0]+10, B[1], FONT_LG, BLACK)
    draw_text(draw, "C", C[0]-25, C[1], FONT_LG, BLACK)
    # 角平分线AD
    D = (375, 400)
    draw_line(draw, A[0], A[1], D[0], D[1], color=RED, width=2)
    draw_point(draw, D[0], D[1], r=5, color=RED)
    draw_text(draw, "D", D[0]+10, D[1]-10, FONT_LG, RED)
    # 角的弧
    draw.arc([A[0]-30, A[1], A[0]+30, A[1]+60], -90, 0, fill=GRAY, width=1)
    draw_text(draw, "AD是∠BAC的平分线", 350, 460, FONT_SM, RED)
    draw_text(draw, "图006：三角形ABC，AD为∠BAC的角平分线", 350, 30, FONT_LG, BLACK)
    img.save(os.path.join(OUT_DIR, "img006.png"))

# ============================================================
# 图007: 直角三角形 30°角定理
# ============================================================
def make_img007():
    img, draw = new_img(800, 500)
    # 直角在A，30°角在B
    A = (120, 380)
    B = (680, 380)
    C = (120, 100)
    # 画直角
    draw_line(draw, A[0], A[1], A[0]+40, A[1], color=BLACK, width=2)
    draw_line(draw, A[0], A[1], A[0], A[1]-40, color=BLACK, width=2)
    # 三角形
    draw_line(draw, A[0], A[1], B[0], B[1], color=BLACK, width=2)
    draw_line(draw, A[0], A[1], C[0], C[1], color=BLACK, width=2)
    draw_line(draw, B[0], B[1], C[0], C[1], color=BLACK, width=2)
    for x, y in [A, B, C]:
        draw_point(draw, x, y, r=5, color=BLACK)
    draw_text(draw, "A", A[0]-25, A[1]+10, FONT_LG, BLACK)
    draw_text(draw, "B", B[0]+10, B[1]+10, FONT_LG, BLACK)
    draw_text(draw, "C", C[0]-25, C[1]-10, FONT_LG, BLACK)
    # 标注
    draw_text(draw, "∠C = 30°", (A[0]+C[0])//2-60, (A[1]+C[1])//2-30, FONT_SM, BLACK)
    draw_text(draw, "BC是斜边", (B[0]+C[0])//2+10, (B[1]+C[1])//2+10, FONT_SM, BLUE)
    draw_text(draw, "AB(对边) = BC/2", (A[0]+B[0])//2-60, A[1]+20, FONT_SM, BLUE)
    draw.rectangle([500, 60, 790, 120], outline=GRAY, width=1)
    draw_text(draw, "30°定理：30°所对直角边 = 斜边的一半", 645, 90, FONT_SM, BLACK)
    draw_text(draw, "图007：直角三角形，∠C=30°", 400, 25, FONT_LG, BLACK)
    img.save(os.path.join(OUT_DIR, "img007.png"))

# ============================================================
# 图008: 等腰三角形 + 三线合一
# ============================================================
def make_img008():
    img, draw = new_img(700, 550)
    # 顶角A在顶部，AB=AC
    A = (350, 80)
    B = (120, 420)
    C = (580, 420)
    # 三角形
    draw_line(draw, A[0], A[1], B[0], B[1], color=BLACK, width=2)
    draw_line(draw, A[0], A[1], C[0], C[1], color=BLACK, width=2)
    draw_line(draw, B[0], B[1], C[0], C[1], color=BLACK, width=2)
    for x, y in [A, B, C]:
        draw_point(draw, x, y, r=5, color=BLACK)
    draw_text(draw, "A", A[0]-10, A[1]-25, FONT_LG, BLACK)
    draw_text(draw, "B", B[0]-25, B[1]+5, FONT_LG, BLACK)
    draw_text(draw, "C", C[0]+10, C[1]+5, FONT_LG, BLACK)
    # AB=AC标注
    draw_text(draw, "AB = AC", 200, 250, FONT_SM, BLUE)
    # D是BC中点，顶角平分线+高+中线三线合一
    D = ((B[0]+C[0])//2, (B[1]+C[1])//2)
    draw_line(draw, A[0], A[1], D[0], D[1], color=RED, width=2)
    draw_point(draw, D[0], D[1], r=5, color=RED)
    draw_text(draw, "D", D[0]+10, D[1]-10, FONT_LG, RED)
    # 直角符号（在D处的高）
    draw_line(draw, D[0], D[1], D[0], D[1]+40, color=RED, width=1)
    draw_line(draw, D[0], D[1]+40, D[0]+15, D[1]+40, color=RED, width=1)
    draw_text(draw, "AD = 顶角平分线 = 底边中线 = 底边高（三线合一）", 350, 500, FONT_SM, RED)
    draw_text(draw, "图008：等腰△ABC，AB=AC，AD为三线合一", 350, 30, FONT_LG, BLACK)
    img.save(os.path.join(OUT_DIR, "img008.png"))

# ============================================================
# 生成所有图片
# ============================================================
if __name__ == "__main__":
    print("正在生成图片...")
    make_img001()
    print("img001.png OK")
    make_img002()
    print("img002.png OK")
    make_img003()
    print("img003.png OK")
    make_img004()
    print("img004.png OK")
    make_img005()
    print("img005.png OK")
    make_img006()
    print("img006.png OK")
    make_img007()
    print("img007.png OK")
    make_img008()
    print("img008.png OK")
    print(f"全部生成完毕，保存到：{OUT_DIR}")
