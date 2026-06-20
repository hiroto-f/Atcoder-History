# ダイクストラ法

## 概要

ダイクストラ法は、重み付きグラフにおいて、ある始点から各頂点への最短距離を求めるアルゴリズムです。

すべての辺のコストが `0` 以上のときに使えます。

基本的な考え方は次の通りです。

1. 各頂点への最短距離候補を `dist` に持つ
2. まだ処理していない中で、距離が一番小さい頂点を選ぶ
3. その頂点から行ける先の距離を更新する
4. これを繰り返す

## イメージ

始点の距離を `0` とします。

最初は、他の頂点への距離はまだ分からないので `INF` にします。

```text
始点: 0
その他: INF
```

ダイクストラ法では、始点に近い頂点から順番に最短距離を確定していきます。

```text
確定済みの範囲       次に一番近い頂点       未確定の範囲
[ 最短距離が確定 ] -> [ これを選ぶ ]   ->   [ 後で更新される ]
```

優先度付きキューから取り出した頂点が、その時点で最も距離が小さい頂点です。

辺のコストがすべて非負なので、あとから遠い頂点を経由しても、すでに一番近い頂点の距離がさらに短くなることはありません。

そのため、一番小さい距離で取り出された頂点の距離は確定できます。

## 緩和

次のような辺があるとします。

```text
current -> next_node のコストが cost
```

もし、

```text
dist[current] + cost < dist[next_node]
```

なら、`next_node` へより短く行ける経路が見つかったということです。

そのため、次のように更新します。

```text
dist[next_node] = dist[current] + cost
```

この更新処理を「緩和」と呼びます。

## Python の典型コード

```python
import heapq

INF = 10**30

dist = [INF] * n
dist[start] = 0

heap = [(0, start)]

while heap:
    current_dist, current = heapq.heappop(heap)

    if dist[current] != current_dist:
        continue

    for next_node, cost in graph[current]:
        next_dist = current_dist + cost

        if next_dist < dist[next_node]:
            dist[next_node] = next_dist
            heapq.heappush(heap, (next_dist, next_node))
```

## グラフの持ち方

隣接リストで持つことが多いです。

```python
graph = [[] for _ in range(n)]
graph[u].append((v, cost))
```

無向辺の場合は、両方向に追加します。

```python
graph[u].append((v, cost))
graph[v].append((u, cost))
```

## 計算量

優先度付きキューを使うと、計算量は次のようになります。

```text
O((N + M) log N)
```

ここで、

- `N` は頂点数
- `M` は辺数
