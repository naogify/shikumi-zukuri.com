"""
ヒーロー用の等高線 SVG パスを生成するスクリプト。

名刺の make_card.py と同じ考え方（斜めの傾斜面＋山頂のガウス山＋うねり）で
スカラー場をつくり、その等値線を matplotlib で求めて SVG の path に変換する。
出力は public/index.html のヒーローにインラインで貼り付けて使う（実行時の JS 不要）。

使い方:
    python gen_contours.py > contours.txt  # 出力を index.html の <g mask=...> 内に貼り替える
"""

import math

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# ---- 描画範囲（SVG の viewBox 単位） ----
W, H = 1000.0, 640.0
# 山頂（緑の点）の位置
PEAK = (760.0, 170.0)


def rdp(points, eps):
    """Ramer–Douglas–Peucker 法で折れ線の点数を減らす。

    Args:
        points: (N, 2) の座標配列
        eps: 許容誤差（この距離以内の点は省略する）
    Returns:
        間引いた (M, 2) 配列
    """
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    d = end - start
    n = math.hypot(*d)
    # 始点と終点を結ぶ直線から各点までの距離を求める
    if n == 0:
        dist = np.hypot(*(points - start).T)
    else:
        dist = np.abs(d[0] * (points[:, 1] - start[1]) - d[1] * (points[:, 0] - start[0])) / n
    i = int(np.argmax(dist))
    # 最も遠い点が許容誤差を超えていれば、そこで分割して再帰する
    if dist[i] > eps:
        left = rdp(points[: i + 1], eps)
        right = rdp(points[i:], eps)
        return np.vstack([left[:-1], right])
    return np.array([start, end])


def field():
    """等高線の元になるスカラー場を返す。

    Returns:
        (xs, ys, f) のタプル。f は ys×xs の 2 次元配列
    """
    xs = np.linspace(-10, W + 10, 420)
    ys = np.linspace(-10, H + 10, 280)
    gx, gy = np.meshgrid(xs, ys)

    def gauss(px, py, sx, sy, amp, rot=0.0):
        """回転付き楕円ガウス関数（山ひとつ分）を返す。"""
        cr, sr = math.cos(rot), math.sin(rot)
        dx, dy = gx - px, gy - py
        u = cr * dx + sr * dy
        v = -sr * dx + cr * dy
        return amp * np.exp(-(u * u / (2 * sx * sx) + v * v / (2 * sy * sy)))

    # 左下→右上へ上っていく斜めの傾斜面（基準線からの符号付き距離）
    lx0, ly0, lx1, ly1 = 260.0, 0.0, 1000.0, 470.0
    ln = math.hypot(lx1 - lx0, ly1 - ly0)
    nx, ny = (ly1 - ly0) / ln, -(lx1 - lx0) / ln
    ramp = (gx - lx0) * nx + (gy - ly0) * ny

    # 傾斜面＋山頂の山＋サブの尾根＋地形らしいうねり
    f = (
        ramp / 300.0
        + gauss(PEAK[0], PEAK[1], 70, 48, 0.34, rot=-0.45)
        + gauss(520, 40, 120, 40, 0.10, rot=0.4)
        + 0.045 * np.sin(gx * 0.030 + gy * 0.047)
        + 0.030 * np.sin(gx * 0.012 - gy * 0.065 + 1.3)
        + 0.020 * np.sin(gx * 0.065 + gy * 0.011 + 0.4)
    )
    return xs, ys, f


def main():
    """等値線を求め、SVG の <path> 要素として標準出力に書き出す。"""
    xs, ys, f = field()
    levels = np.arange(0.03, 1.4, 0.075)
    cs = plt.contour(xs, ys, f, levels=levels)
    out = []
    for seg_list in cs.allsegs:
        for seg in seg_list:
            # 小さな島（ノイズ由来の閉曲線）は除外する
            if len(seg) < 3 or np.ptp(seg, axis=0).max() < 40:
                continue
            pts = rdp(np.asarray(seg), 0.9)
            d = "M" + " ".join(f"{x:.0f} {y:.0f}" for x, y in pts)
            out.append(f'<path d="{d}"/>')
    print("\n".join(out))


if __name__ == "__main__":
    main()
