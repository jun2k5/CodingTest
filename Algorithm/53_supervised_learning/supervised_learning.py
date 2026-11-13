"""지도 학습 기초: 결정 트리(엔트로피·정보 이득, ID3), k-최근접 이웃, 퍼셉트론, 다층 퍼셉트론과 역전파. 표준 라이브러리만 사용."""
import math, random
from collections import Counter


# ---------- 결정 트리 ----------

def entropy(labels):
    n = len(labels)
    return -sum(c / n * math.log2(c / n) for c in Counter(labels).values()) if n else 0.0


def gini(labels):
    n = len(labels)
    return 1 - sum((c / n) ** 2 for c in Counter(labels).values()) if n else 0.0


def info_gain(rows, labels, attr, impurity=entropy):
    """부모 불순도 - Σ (자식 크기 비율 × 자식 불순도)."""
    groups = {}
    for r, y in zip(rows, labels): groups.setdefault(r[attr], []).append(y)
    n = len(labels)
    return impurity(labels) - sum(len(g) / n * impurity(g) for g in groups.values())


def build_tree(rows, labels, attrs, impurity=entropy):
    """ID3: 정보 이득이 가장 큰 속성으로 나누기를 반복. 모두 같은 클래스이거나 속성이 없으면 잎(다수결)."""
    if len(set(labels)) == 1: return labels[0]
    if not attrs: return Counter(labels).most_common(1)[0][0]
    best = max(attrs, key=lambda a: info_gain(rows, labels, a, impurity))
    node = {"attr": best, "children": {}, "default": Counter(labels).most_common(1)[0][0]}
    for v in sorted({r[best] for r in rows}):
        idx = [i for i, r in enumerate(rows) if r[best] == v]
        node["children"][v] = build_tree([rows[i] for i in idx], [labels[i] for i in idx],
                                         [a for a in attrs if a != best], impurity)
    return node


def predict_tree(node, row):
    while isinstance(node, dict):
        node = node["children"].get(row[node["attr"]], node["default"])
    return node


def show_tree(node, names, indent=""):
    if not isinstance(node, dict): return [indent + f"→ {node}"]
    out = []
    for v, child in node["children"].items():
        out.append(indent + f"{names[node['attr']]} = {v}")
        out += show_tree(child, names, indent + "    ")
    return out


# ---------- k-최근접 이웃 ----------

def knn_predict(train_x, train_y, x, k):
    d = sorted((math.dist(p, x), y) for p, y in zip(train_x, train_y))[:k]
    votes = Counter(y for _, y in d)
    top = max(votes.values())
    return min(y for y, c in votes.items() if c == top)      # 동표면 작은 라벨


# ---------- 퍼셉트론 ----------

def perceptron(xs, ys, epochs=100, lr=1.0):
    """y ∈ {-1, +1}. 틀린 점마다 w += lr·y·x. 선형 분리 가능하면 유한 번 안에 수렴한다."""
    w, b = [0.0] * len(xs[0]), 0.0
    for ep in range(epochs):
        errors = 0
        for x, y in zip(xs, ys):
            if y * (sum(wi * xi for wi, xi in zip(w, x)) + b) <= 0:
                w = [wi + lr * y * xi for wi, xi in zip(w, x)]; b += lr * y; errors += 1
        if errors == 0: return w, b, ep + 1
    return w, b, None


# ---------- 다층 퍼셉트론 (은닉층 1개) ----------

def sigmoid(z):
    return 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))


class MLP:
    """입력 → 은닉(tanh) → 출력(sigmoid), 손실은 이진 교차 엔트로피."""

    def __init__(self, n_in, n_hidden, rng):
        s = 1 / math.sqrt(n_in)
        self.W1 = [[rng.uniform(-s, s) for _ in range(n_in)] for _ in range(n_hidden)]
        self.b1 = [0.0] * n_hidden
        self.W2 = [rng.uniform(-1, 1) / math.sqrt(n_hidden) for _ in range(n_hidden)]
        self.b2 = 0.0

    def forward(self, x):
        h = [math.tanh(sum(w * xi for w, xi in zip(row, x)) + b) for row, b in zip(self.W1, self.b1)]
        out = sigmoid(sum(w * hi for w, hi in zip(self.W2, h)) + self.b2)
        return h, out

    def loss(self, xs, ys):
        eps = 1e-12
        return -sum(y * math.log(self.forward(x)[1] + eps) + (1 - y) * math.log(1 - self.forward(x)[1] + eps)
                    for x, y in zip(xs, ys)) / len(xs)

    def gradients(self, x, y):
        """역전파: 출력층 오차 δ2 = ŷ - y (sigmoid + 교차 엔트로피), 은닉층 δ1 = δ2·W2·(1 - h²)."""
        h, out = self.forward(x)
        d2 = out - y
        gW2 = [d2 * hi for hi in h]
        gb2 = d2
        d1 = [d2 * w2 * (1 - hi * hi) for w2, hi in zip(self.W2, h)]
        gW1 = [[d * xi for xi in x] for d in d1]
        gb1 = d1
        return gW1, gb1, gW2, gb2

    def train(self, xs, ys, epochs, lr, rng):
        idx = list(range(len(xs)))
        for _ in range(epochs):
            rng.shuffle(idx)
            for i in idx:
                gW1, gb1, gW2, gb2 = self.gradients(xs[i], ys[i])
                for j in range(len(self.W1)):
                    self.W1[j] = [w - lr * g for w, g in zip(self.W1[j], gW1[j])]
                    self.b1[j] -= lr * gb1[j]
                self.W2 = [w - lr * g for w, g in zip(self.W2, gW2)]
                self.b2 -= lr * gb2

    def predict(self, x):
        return int(self.forward(x)[1] >= 0.5)


def numeric_grad_check(model, x, y, h=1e-6):
    """수치 미분 (L(w+h) - L(w-h)) / 2h 과 역전파 기울기의 최대 차이."""
    gW1, gb1, gW2, gb2 = model.gradients(x, y)
    def L(): return model.loss([x], [y])
    worst = 0.0
    for j in range(len(model.W1)):
        for k in range(len(model.W1[j])):
            old = model.W1[j][k]
            model.W1[j][k] = old + h; lp = L()
            model.W1[j][k] = old - h; lm = L()
            model.W1[j][k] = old
            worst = max(worst, abs((lp - lm) / (2 * h) - gW1[j][k]))
    for j in range(len(model.W2)):
        old = model.W2[j]
        model.W2[j] = old + h; lp = L()
        model.W2[j] = old - h; lm = L()
        model.W2[j] = old
        worst = max(worst, abs((lp - lm) / (2 * h) - gW2[j]))
    return worst


def make_circles(rng, n):
    """안쪽 원(라벨 1)과 바깥 고리(라벨 0). 반지름 1.0~1.4 구간은 두 클래스가 겹친다. 직선 하나로는 나눌 수 없다."""
    xs, ys = [], []
    for _ in range(n):
        if rng.random() < 0.5:
            r, y = rng.uniform(0, 1.4), 1
        else:
            r, y = rng.uniform(1.0, 2.2), 0
        t = rng.uniform(0, 2 * math.pi)
        xs.append((r * math.cos(t), r * math.sin(t))); ys.append(y)
    return xs, ys


if __name__ == "__main__":
    rng = random.Random(53)
    # 테니스 예제 (Quinlan의 ID3 교재 데이터)
    names = ["날씨", "기온", "습도", "바람"]
    data = [("맑음", "더움", "높음", "약함", "아니오"), ("맑음", "더움", "높음", "강함", "아니오"), ("흐림", "더움", "높음", "약함", "예"),
            ("비", "보통", "높음", "약함", "예"), ("비", "추움", "보통", "약함", "예"), ("비", "추움", "보통", "강함", "아니오"),
            ("흐림", "추움", "보통", "강함", "예"), ("맑음", "보통", "높음", "약함", "아니오"), ("맑음", "추움", "보통", "약함", "예"),
            ("비", "보통", "보통", "약함", "예"), ("맑음", "보통", "보통", "강함", "예"), ("흐림", "보통", "높음", "강함", "예"),
            ("흐림", "더움", "보통", "약함", "예"), ("비", "보통", "높음", "강함", "아니오")]
    rows, labels = [d[:4] for d in data], [d[4] for d in data]
    print(f"전체 엔트로피 (예 9, 아니오 5): {entropy(labels):.3f}")
    for a in range(4):
        print(f"  {names[a]} 정보 이득 {info_gain(rows, labels, a):.3f}  (지니 감소 {info_gain(rows, labels, a, gini):.3f})")
    tree = build_tree(rows, labels, [0, 1, 2, 3])
    print("\n".join(show_tree(tree, names)))
    assert all(predict_tree(tree, r) == y for r, y in zip(rows, labels))
    print("학습 데이터 14개 모두 맞게 분류")

    # 결정 트리 검증: 라벨이 속성들의 결정적 함수면 학습 데이터 정확도 100%
    for _ in range(200):
        n_attr = rng.randint(1, 4)
        rule = {}
        rs = [tuple(rng.randint(0, 2) for _ in range(n_attr)) for _ in range(rng.randint(1, 40))]
        ls = [rule.setdefault(r, rng.choice("AB")) for r in rs]
        t = build_tree(rs, ls, list(range(n_attr)))
        assert all(predict_tree(t, r) == y for r, y in zip(rs, ls))
    print("결정 트리: 200개 무작위 데이터(라벨이 속성으로 결정됨)에서 학습 데이터 정확도 100%")

    # k-NN
    xs, ys = make_circles(rng, 400)
    tx, ty = make_circles(rng, 200)
    for k in (1, 5, 15, 51):
        acc = sum(knn_predict(xs, ys, x, k) == y for x, y in zip(tx, ty)) / len(tx)
        print(f"k-NN 원 데이터 (학습 400, 테스트 200), k = {k:2d}: 정확도 {acc:.3f}")

    # 퍼셉트론: 선형 분리 가능 vs XOR
    w_true = (2.0, -3.0); b_true = 0.5
    pts = [(rng.uniform(-5, 5), rng.uniform(-5, 5)) for _ in range(200)]
    pts = [p for p in pts if abs(w_true[0] * p[0] + w_true[1] * p[1] + b_true) > 0.5]   # 경계 근처는 뺌(여백)
    lab = [1 if w_true[0] * x + w_true[1] * y + b_true > 0 else -1 for x, y in pts]
    w, b, ep = perceptron(pts, lab)
    print(f"퍼셉트론 (선형 분리 가능한 점 {len(pts)}개): {ep}번째 에포크에 수렴, w = ({w[0]:.1f}, {w[1]:.1f}), b = {b:.1f}")
    xor_x, xor_y = [(0, 0), (0, 1), (1, 0), (1, 1)], [-1, 1, 1, -1]
    w, b, ep = perceptron(xor_x, xor_y, epochs=1000)
    print("퍼셉트론 XOR:", "1000 에포크 안에 수렴하지 않음 (직선 하나로 나눌 수 없다)" if ep is None else ep)

    # MLP: 기울기 검사, XOR, 원 데이터
    m = MLP(2, 4, rng)
    worst = max(numeric_grad_check(m, (rng.uniform(-2, 2), rng.uniform(-2, 2)), rng.randint(0, 1)) for _ in range(50))
    print(f"역전파 기울기 vs 수치 미분: 50개 입력에서 최대 차이 {worst:.2e}")
    m = MLP(2, 4, rng)
    xy = [0, 1, 1, 0]
    before = m.loss(xor_x, xy)
    m.train(xor_x, xy, 3000, 0.1, rng)
    print(f"MLP(은닉 4) XOR: 손실 {before:.3f} → {m.loss(xor_x, xy):.3f}, 예측 {[m.predict(x) for x in xor_x]} (정답 [0, 1, 1, 0])")
    m = MLP(2, 8, rng)
    m.train(xs, ys, 200, 0.05, rng)
    acc = sum(m.predict(x) == y for x, y in zip(tx, ty)) / len(tx)
    lin_w, lin_b, _ = perceptron(xs, [1 if y else -1 for y in ys], epochs=50)
    lin_acc = sum((1 if sum(a * b for a, b in zip(lin_w, x)) + lin_b > 0 else 0) == y for x, y in zip(tx, ty)) / len(tx)
    print(f"원 데이터 테스트 정확도: MLP(은닉 8) {acc:.3f}, 퍼셉트론(직선) {lin_acc:.3f}")
