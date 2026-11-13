"""아호-코라식: 트라이 + 실패 링크로 여러 패턴을 텍스트 한 번 훑으며 모두 찾는다."""
import random
from collections import deque


class AhoCorasick:
    def __init__(self, patterns):
        self.goto = [{}]                          # 노드별 자식 {문자: 노드}
        self.fail = [0]
        self.out = [[]]                           # 이 노드에서 끝나는 패턴 번호 (실패 링크로 이어진 것 포함)
        self.patterns = patterns
        for idx, p in enumerate(patterns):
            v = 0
            for c in p:
                if c not in self.goto[v]:
                    self.goto[v][c] = len(self.goto)
                    self.goto.append({}); self.fail.append(0); self.out.append([])
                v = self.goto[v][c]
            self.out[v].append(idx)
        q = deque(self.goto[0].values())          # 깊이 1 노드의 실패 링크는 루트
        while q:                                   # BFS: 부모의 실패 링크가 먼저 계산되어 있어야 한다
            v = q.popleft()
            for c, u in self.goto[v].items():
                f = self.fail[v]
                while f and c not in self.goto[f]:
                    f = self.fail[f]
                self.fail[u] = self.goto[f][c] if c in self.goto[f] and self.goto[f][c] != u else 0
                self.out[u] += self.out[self.fail[u]]   # 실패 링크 쪽에서 끝나는 패턴도 여기서 끝난다
                q.append(u)

    def search(self, t):
        """반환: (시작 위치, 패턴 번호) 목록."""
        res, v = [], 0
        for i, c in enumerate(t):
            while v and c not in self.goto[v]:
                v = self.fail[v]
            v = self.goto[v].get(c, 0)
            for idx in self.out[v]:
                res.append((i - len(self.patterns[idx]) + 1, idx))
        return res


def brute(t, patterns):
    res = []
    for idx, p in enumerate(patterns):
        i = t.find(p)
        while i != -1:
            res.append((i, idx)); i = t.find(p, i + 1)
    return res


if __name__ == "__main__":
    rng = random.Random(37)
    for _ in range(2000):
        pats = list({"".join(rng.choice("abc") for _ in range(rng.randint(1, 5))) for _ in range(rng.randint(1, 8))})
        t = "".join(rng.choice("abc") for _ in range(rng.randint(0, 60)))
        assert sorted(AhoCorasick(pats).search(t)) == sorted(brute(t, pats))
    print("아호-코라식: 2000개 입력(패턴 최대 8개)에서 패턴별 str.find 결과와 일치")

    pats = ["he", "she", "his", "hers"]
    ac = AhoCorasick(pats)
    print("패턴", pats, "텍스트 'ushers':", [(pos, pats[i]) for pos, i in sorted(ac.search("ushers"))])
    print("노드 수", len(ac.goto), "실패 링크", ac.fail)

    # 패턴 수가 많을 때: 패턴마다 따로 검색 vs 아호-코라식
    import time
    alpha = "abcdefghij"
    t = "".join(rng.choice(alpha) for _ in range(200000))
    for k in (10, 1000):
        pats = list({"".join(rng.choice(alpha) for _ in range(6)) for _ in range(k)})
        t0 = time.perf_counter(); a = AhoCorasick(pats).search(t); t1 = time.perf_counter()
        b = brute(t, pats); t2 = time.perf_counter()
        assert sorted(a) == sorted(b)
        print(f"텍스트 200,000자, 길이 6 패턴 {len(pats)}개: 일치 {len(a)}번, 아호-코라식 {1000 * (t1 - t0):.0f}ms, "
              f"패턴마다 str.find {1000 * (t2 - t1):.0f}ms")
