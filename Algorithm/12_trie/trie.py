"""트라이: 삽입, 검색, 접두사 검색, 접두사로 시작하는 단어 수, 삭제."""
import random


class TrieNode:
    __slots__ = ("children", "end", "count")

    def __init__(self):
        self.children = {}
        self.end = False        # 여기서 끝나는 단어가 있는가
        self.count = 0          # 이 노드를 지나는 단어 수(접두사 개수)


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        if self.search(word):
            return
        node = self.root
        node.count += 1
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
            node.count += 1
        node.end = True

    def _walk(self, s):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):
        n = self._walk(word)
        return n is not None and n.end

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

    def count_prefix(self, prefix):
        n = self._walk(prefix)
        return n.count if n else 0

    def words_with_prefix(self, prefix):
        n, out = self._walk(prefix), []
        def dfs(node, path):
            if node.end: out.append(path)
            for ch in sorted(node.children):
                dfs(node.children[ch], path + ch)
        if n: dfs(n, prefix)
        return out

    def delete(self, word):
        if not self.search(word):
            return False
        node = self.root
        node.count -= 1
        for ch in word:
            nxt = node.children[ch]
            nxt.count -= 1
            if nxt.count == 0:          # 이 단어만 지나던 가지는 통째로 떼어 낸다
                del node.children[ch]
                return True
            node = nxt
        node.end = False
        return True


if __name__ == "__main__":
    rng = random.Random(31)
    for _ in range(300):
        t, ref = Trie(), set()
        for _ in range(rng.randint(1, 80)):
            w = "".join(rng.choice("abc") for _ in range(rng.randint(0, 5)))
            if rng.random() < 0.7:
                t.insert(w); ref.add(w)
            else:
                assert t.delete(w) == (w in ref); ref.discard(w)
            p = "".join(rng.choice("abc") for _ in range(rng.randint(0, 3)))
            assert t.search(w) == (w in ref)
            assert t.count_prefix(p) == sum(1 for x in ref if x.startswith(p))
            assert t.words_with_prefix(p) == sorted(x for x in ref if x.startswith(p))
    print("Trie: set과 300개 무작위 시나리오 일치 (검색·접두사 개수·목록·삭제)")
    t = Trie()
    for w in ["tea", "ten", "to", "inn", "in", "team"]:
        t.insert(w)
    print("te로 시작:", t.words_with_prefix("te"), " 개수:", t.count_prefix("te"))
    print("search('te') =", t.search("te"), " starts_with('te') =", t.starts_with("te"))
