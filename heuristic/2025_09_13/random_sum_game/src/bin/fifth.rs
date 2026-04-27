use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};
use std::io::{self, BufRead, BufReader, Write};
use std::time::{Duration, Instant};

// ==================== 設定 ====================
const PRINT_TIME: bool = false; // 提出時は false（stderr 出力抑止）
const SA_TIME_MS: u64 = 1990;   // 焼きなまし実行時間（固定 1.99s）
const PHASE1_MS: u64 = 1000;    // フェーズ1（単一移動のみ）
const PHASE2_MS: u64 = SA_TIME_MS - PHASE1_MS; // フェーズ2（スワップのみ）

// ==================== 速いスキャナ ====================
struct Scanner<R> { reader: R, buf: Vec<u8>, pos: usize }
impl<R: BufRead> Scanner<R> {
    fn new(reader: R) -> Self { Self { reader, buf: Vec::with_capacity(1 << 16), pos: 0 } }
    fn refill(&mut self) -> bool {
        self.buf.clear(); self.pos = 0;
        let mut s = String::new();
        match self.reader.read_line(&mut s) {
            Ok(0) => false, Ok(_) => { self.buf.extend_from_slice(s.as_bytes()); true }, Err(_) => false,
        }
    }
    fn next_token(&mut self) -> Option<String> {
        loop {
            while self.pos < self.buf.len() && self.buf[self.pos].is_ascii_whitespace() { self.pos += 1; }
            if self.pos < self.buf.len() {
                let st = self.pos;
                while self.pos < self.buf.len() && !self.buf[self.pos].is_ascii_whitespace() { self.pos += 1; }
                return Some(std::str::from_utf8(&self.buf[st..self.pos]).ok()?.to_string());
            }
            if !self.refill() { return None; }
        }
    }
    fn next_usize(&mut self) -> usize { self.next_token().unwrap().parse().unwrap() }
    fn next_i64(&mut self) -> i64 { self.next_token().unwrap().parse().unwrap() }
}

// ==================== 簡易 RNG (xorshift64) ====================
struct XorShift64 { state: u64 }
impl XorShift64 {
    fn new(mut seed: u64) -> Self { if seed == 0 { seed = 0x9E37_79B9_7F4A_7C15; } Self { state: seed } }
    #[inline] fn next_u64(&mut self) -> u64 { let mut x=self.state; x^=x<<7; x^=x>>9; x^=x<<8; self.state=x; x }
    #[inline] fn gen_usize(&mut self, bound: usize) -> usize { (self.next_u64() as usize) % bound }
    #[inline] fn gen_f64(&mut self) -> f64 { ((self.next_u64() >> 11) as f64) * (1.0 / ((1u64 << 53) as f64)) }
    #[inline] fn gen_range_usize(&mut self, lo: usize, hi: usize) -> usize { lo + self.gen_usize(hi - lo) }
}

// ==================== A 構築：案C（上位4層を削って s/2 と s/4 を追加） ====================
fn build_cards(
    n: usize, m: usize, l: i128, u: i128
) -> (Vec<i128>, Vec<(i128, usize, usize)>, usize, i128) {
    let base_count = m;
    let remaining = n.saturating_sub(base_count);
    let max_layers = remaining / m;
    let r = u - l;

    let (layers, s) = if r <= 0 || max_layers == 0 {
        (0usize, 0i128)
    } else {
        let layers = max_layers;
        let denom_u = (1u128 << layers) - 1;
        let r_u = r as u128;
        let s_u = (r_u + denom_u - 1) / denom_u; // ceil
        (layers, s_u as i128)
    };

    let mut pairs: Vec<(i128, usize)> = Vec::new();
    if layers > 0 && s > 0 {
        for k in 0..layers {
            let v = ((1u128 << k) * (s as u128)) as i128;
            pairs.push((v, m));
        }
        // 案C：上位4層を 0.48, 0.56, 0.64, 0.52 に削減 → 浮き ≈ 1.8M を s/2 と s/4 に
        if layers >= 4 {
            let idx_top = layers - 1;
            let idx2    = layers - 2;
            let idx3    = layers - 3;
            let idx4    = layers - 4;

            let keep_top = ((m as f64) * 0.48).ceil() as usize;
            let keep_2nd = ((m as f64) * 0.56).ceil() as usize;
            let keep_3rd = ((m as f64) * 0.64).ceil() as usize;
            let keep_4th = ((m as f64) * 0.52).ceil() as usize;

            let mut freed: usize = 0;
            let new_top = keep_top.min(m);
            let new_2nd = keep_2nd.min(m);
            let new_3rd = keep_3rd.min(m);
            let new_4th = keep_4th.min(m);

            freed += pairs[idx_top].1.saturating_sub(new_top);
            freed += pairs[idx2].1.saturating_sub(new_2nd);
            freed += pairs[idx3].1.saturating_sub(new_3rd);
            freed += pairs[idx4].1.saturating_sub(new_4th);

            pairs[idx_top].1 = new_top;
            pairs[idx2].1    = new_2nd;
            pairs[idx3].1    = new_3rd;
            pairs[idx4].1    = new_4th;

            // s/2: M 枚を上限に投入、残りは s/4
            let half  = std::cmp::max(1i128, s / 2);
            let quart = std::cmp::max(1i128, s / 4);
            if freed > 0 {
                let add_half = freed.min(m);
                pairs.push((half, add_half));
                let rem = freed - add_half;
                if rem > 0 { pairs.push((quart, rem)); }
            }
        }
    }

    // 額面降順
    pairs.sort_by(|a, b| b.0.cmp(&a.0));

    // A 配列（先頭に L×M）
    let mut a: Vec<i128> = Vec::with_capacity(n);
    for _ in 0..m { a.push(l); }

    // groups: (value, start_index, count)
    let mut groups: Vec<(i128, usize, usize)> = Vec::new();
    let mut cur = a.len();
    for (v, cnt) in pairs.iter() {
        if *cnt == 0 { continue; }
        let start = cur;
        for _ in 0..*cnt { a.push(*v); }
        groups.push((*v, start, *cnt));
        cur = a.len();
    }

    // N を満たす（余りは 1 を詰める）
    while a.len() < n { a.push(1); }
    if a.len() > n {
        let overflow = a.len() - n;
        if let Some(last) = groups.last_mut() {
            let (val, start, cnt) = *last;
            let new_cnt = cnt.saturating_sub(overflow);
            a.truncate(n);
            *last = (val, start, new_cnt);
        } else {
            a.truncate(n);
        }
    }

    (a, groups, layers, s)
}

// ==================== 初期割当（額面降順 × Δ降順） ====================
fn greedy_assign(
    a: &[i128], m: usize, l: i128, b: &[i128],
    groups: &[(i128, usize, usize)]
) -> (Vec<usize>, Vec<i128>, i128) {
    let n = a.len();
    let mut x = vec![0usize; n];

    // Base L を 1..M に
    let mut ssum = vec![0i128; m];
    for j in 0..m { x[j] = j + 1; ssum[j] += l; }

    // Δ = B - L
    let mut delta: Vec<i128> = b.iter().map(|&bj| bj - l).collect();

    #[derive(Clone, Copy, Eq)]
    struct Item(i128, usize);
    impl Ord for Item {
        fn cmp(&self, other: &Self) -> Ordering {
            match self.0.cmp(&other.0) { Ordering::Equal => self.1.cmp(&other.1), o => o }
        }
    }
    impl PartialOrd for Item { fn partial_cmp(&self, other: &Self) -> Option<Ordering> { Some(self.cmp(other)) } }
    impl PartialEq for Item { fn eq(&self, other: &Self) -> bool { self.0 == other.0 && self.1 == other.1 } }

    let mut heap = BinaryHeap::with_capacity(m);
    for j in 0..m { heap.push(Item(delta[j], j)); }

    for &(value, start, count) in groups.iter() {
        let mut assigned_any = false;
        for idx in start..start + count {
            loop {
                if let Some(Item(d, j)) = heap.pop() {
                    if d != delta[j] { continue; } // stale
                    if d < value {
                        heap.push(Item(d, j)); // これ以上この額面は無理
                        break;
                    }
                    x[idx] = j + 1;
                    ssum[j] += value;
                    delta[j] -= value;
                    heap.push(Item(delta[j], j));
                    assigned_any = true;
                    break;
                } else { break; }
            }
            if !assigned_any { break; }
        }
    }

    // 誤差
    let mut e: i128 = 0;
    for j in 0..m { e += (ssum[j] - b[j]).abs(); }
    (x, ssum, e)
}

// ==================== SA 用バケツ構造 ====================
struct Buckets {
    // buckets[pile][val_idx] = indices  (pile: 0..=M, 0=捨て山)
    buckets: Vec<Vec<Vec<usize>>>,
    // index -> (pile, val_idx, pos_in_vec)
    idx_pile: Vec<usize>,
    idx_vali: Vec<usize>,
    idx_pos: Vec<usize>,
    movable: Vec<bool>,
}
impl Buckets {
    fn new(m: usize, distinct_vals: usize, n: usize, x: &[usize], idx_vali: &[usize], movable: &[bool]) -> Self {
        let mut buckets = vec![vec![Vec::<usize>::new(); distinct_vals]; m + 1];
        let mut idx_pile = vec![0usize; n];
        let mut idx_pos  = vec![0usize; n];
        let idx_vali_owned = idx_vali.to_vec();
        for i in 0..n {
            if !movable[i] { continue; }
            let p = x[i]; // 0..M（Xそのもの）
            let vi = idx_vali[i];
            buckets[p][vi].push(i);
            idx_pile[i] = p;
            idx_pos[i]  = buckets[p][vi].len() - 1;
        }
        Self { buckets, idx_pile, idx_vali: idx_vali_owned, idx_pos, movable: movable.to_vec() }
    }
    #[inline] fn remove(&mut self, i: usize) {
        if !self.movable[i] { return; }
        let p  = self.idx_pile[i];
        let vi = self.idx_vali[i];
        let v = &mut self.buckets[p][vi];
        if v.is_empty() { return; } // 予防ガード
        let pos = self.idx_pos[i];
        let last = v.len() - 1;
        v.swap(pos, last);
        let j = v[last];
        self.idx_pos[j] = pos;
        v.pop();
    }
    #[inline] fn add(&mut self, i: usize, new_p: usize) {
        if !self.movable[i] { return; }
        let vi = self.idx_vali[i];
        self.idx_pile[i] = new_p;
        self.idx_pos[i]  = self.buckets[new_p][vi].len();
        self.buckets[new_p][vi].push(i);
    }
    // pile p に value <= target で最も近い val_idx（values は降順）
    fn pick_idx_leq(&self, p: usize, values: &[i128], target: i128) -> Option<usize> {
        let mut best_vi: Option<usize> = None;
        for (vi, &v) in values.iter().enumerate() {
            if self.buckets[p][vi].is_empty() { continue; }
            if v <= target {
                return Some(vi);
            } else {
                best_vi = Some(vi); // 大きすぎるが何かはある
            }
        }
        // すべて target より大きい → 一番小さい額面の非空を返す
        for (vi, _) in values.iter().enumerate().rev() {
            if !self.buckets[p][vi].is_empty() { return Some(vi); }
        }
        best_vi
    }
    // バケツから 1 枚取り出す（末尾）
    #[inline] fn pop_from(&mut self, p: usize, vi: usize) -> Option<usize> {
        if self.buckets[p][vi].is_empty() { return None; }
        let i = self.buckets[p][vi].pop().unwrap();
        self.idx_pile[i] = p;
        Some(i)
    }
    // 任意のバケツで 1 枚（あるもの）を取る
    fn any_index_in_pile(&self, p: usize) -> Option<usize> {
        for vi in 0..self.buckets[p].len() {
            if let Some(&i) = self.buckets[p][vi].last() { return Some(i); }
        }
        None
    }
}

// ========== 小ヘルパ ==========
#[inline]
fn abs_update(absd: &mut [i128], d: &[i128], idx: usize, sum_abs: &mut i128) {
    let old = absd[idx];
    let new = d[idx].abs();
    if new != old {
        *sum_abs += new - old;
        absd[idx] = new;
    }
}

#[inline]
fn pick_pile_weighted(d: &[i128], absd: &[i128], sign: i8, rng: &mut XorShift64) -> usize {
    let mut total: i128 = 0;
    for j in 0..absd.len() {
        if sign == 1 && d[j] <= 0 { continue; }
        if sign == -1 && d[j] >= 0 { continue; }
        total += absd[j];
    }
    if total <= 0 {
        let mut mj = 0usize; let mut best = -1i128;
        for j in 0..absd.len() { let v = absd[j]; if v > best { best = v; mj = j; } }
        return mj;
    }
    let mut r = (rng.gen_f64() * (total as f64)) as i128;
    for j in 0..absd.len() {
        if sign == 1 && d[j] <= 0 { continue; }
        if sign == -1 && d[j] >= 0 { continue; }
        if r < absd[j] { return j; }
        r -= absd[j];
    }
    0
}

#[inline]
fn delta_e_move(d: &[i128], p: usize, q: usize, v: i128) -> i128 {
    let mut old: i128 = 0; let mut newv: i128 = 0;
    if p != 0 { let dp = d[p-1]; old += dp.abs(); newv += (dp - v).abs(); }
    if q != 0 { let dq = d[q-1]; old += dq.abs(); newv += (dq + v).abs(); }
    newv - old
}

// ==================== 焼きなまし（1000ms:単一移動のみ → 990ms:スワップのみ） ====================
fn anneal_two_phase(
    a: &[i128], m: usize, b: &[i128],
    x: &mut [usize], ssum: &mut [i128], e: &mut i128,
    values: &[i128], val_index: &HashMap<i128, usize>,
    movable: &[bool],
    time_limit: Duration, seed: u64,
) {
    let mut roopcount = 0;
    let n = a.len();
    let start = Instant::now();
    let phase1_end = start + Duration::from_millis(PHASE1_MS);

    let mut rng = XorShift64::new(seed);

    // D = S - B
    let mut d: Vec<i128> = (0..m).map(|j| ssum[j] - b[j]).collect();

    // 値インデックス（降順 values）
    let idx_vali: Vec<usize> =
        (0..n).map(|i| if movable[i] { *val_index.get(&a[i]).unwrap() } else { 0usize }).collect();
    let mut buckets = Buckets::new(m, values.len(), n, x, &idx_vali, movable);

    // 温度（256反復ごとに更新）
    let mut e_f = (*e) as f64; if e_f < 1.0 { e_f = 1.0; }
    let t0 = e_f / (m as f64);
    let tend = 1.0f64;
    let inv_limit = 1.0 / time_limit.as_secs_f64();
    let mut t = t0;

    // |D| と合計（差分更新用）
    let mut absd: Vec<i128> = vec![0; m];
    let mut sum_abs: i128 = 0;
    for j in 0..m { absd[j] = d[j].abs(); sum_abs += absd[j]; }
    if sum_abs == 0 { sum_abs = 1; }

    let mut iter: u32 = 0;
    while start.elapsed() < time_limit {
        // 温度の間引き更新
        if (iter & 0xFF) == 0 {
            let progress = (start.elapsed().as_secs_f64() * inv_limit).min(1.0);
            t = t0 * (tend / t0).powf(progress);
            if t < 1e-12 { t = 1e-12; }
        }
        iter = iter.wrapping_add(1);

        // フェーズ判定
        let in_phase1 = Instant::now() < phase1_end;

        if in_phase1 {
            // ==================== フェーズ1：単一移動のみ ====================
            // surplus → deficit を優先。なければフォールバック（全体から選ぶ）
            let mut src = pick_pile_weighted(&d, &absd, 1, &mut rng);
            let mut dst = pick_pile_weighted(&d, &absd, -1, &mut rng);
            if d[src] <= 0 || d[dst] >= 0 {
                src = pick_pile_weighted(&d, &absd, 0, &mut rng);
                dst = pick_pile_weighted(&d, &absd, 0, &mut rng);
                if src == dst { dst = (dst + 1) % m; }
            }
            let p = src + 1;
            let q_dst = dst + 1;

            let target = if d[src] > 0 && d[dst] < 0 { d[src].min(-d[dst]) } else { d[src].abs() };

            if let Some(vi) = buckets.pick_idx_leq(p, values, target) {
                if let Some(i) = buckets.pop_from(p, vi) {
                    if movable[i] {
                        let v = a[i];
                        let q = if d[src] > 0 && d[dst] < 0 { q_dst } else { 0 }; // surplus→deficit or surplus→trash
                        let de = delta_e_move(&d, p, q, v);
                        let accept = if de <= 0 { true } else { (-(de as f64)/t).exp() > rng.gen_f64() };
                        if accept {
                            // 差分更新（O(1)）
                            if p != 0 { d[p-1] -= v; ssum[p-1] -= v; abs_update(&mut absd, &d, p-1, &mut sum_abs); }
                            if q != 0 { d[q-1] += v; ssum[q-1] += v; abs_update(&mut absd, &d, q-1, &mut sum_abs); }
                            x[i] = q;
                            buckets.add(i, q);
                            *e += de;
                        } else {
                            buckets.add(i, p);
                        }
                    } else {
                        buckets.add(i, p);
                    }
                }
            }
            continue;
        }

        // ==================== フェーズ2：スワップのみ ====================
        // surplus / deficit から重み付きに選ぶ
        let src = pick_pile_weighted(&d, &absd, 1, &mut rng);
        let dst = pick_pile_weighted(&d, &absd, -1, &mut rng);
        if d[src] <= 0 || d[dst] >= 0 {
            // スワップできない状況 → 何もしない（単一移動は禁止）
            continue;
        }
        let p = src + 1;
        let q = dst + 1;
        let tp = d[src];
        let tq = -d[dst];

        if let Some(vip) = buckets.pick_idx_leq(p, values, tp) {
            if let Some(i) = buckets.pop_from(p, vip) {
                if let Some(viq) = buckets.pick_idx_leq(q, values, tq) {
                    if let Some(j) = buckets.pop_from(q, viq) {
                        if movable[i] && movable[j] {
                            let v = a[i];
                            let w = a[j];

                            let old = d[src].abs() + d[dst].abs();
                            let newp = (d[src] - v + w).abs();
                            let newq = (d[dst] + v - w).abs();
                            let de = newp + newq - old;

                            let accept = if de <= 0 { true } else { (-(de as f64)/t).exp() > rng.gen_f64() };
                            if accept {
                                // 差分更新
                                d[src] -= v; ssum[src] -= v; abs_update(&mut absd, &d, src, &mut sum_abs);
                                d[dst] += v; ssum[dst] += v; abs_update(&mut absd, &d, dst, &mut sum_abs);

                                d[dst] -= w; ssum[dst] -= w; abs_update(&mut absd, &d, dst, &mut sum_abs);
                                d[src] += w; ssum[src] += w; abs_update(&mut absd, &d, src, &mut sum_abs);

                                x[i] = q; buckets.add(i, q);
                                x[j] = p; buckets.add(j, p);

                                *e += de;
                            } else {
                                buckets.add(i, p);
                                buckets.add(j, q);
                            }
                        } else {
                            if movable[i] { buckets.add(i, p); }
                            if movable[j] { buckets.add(j, q); }
                        }
                    } else {
                        buckets.add(i, p);
                    }
                } else {
                    buckets.add(i, p);
                }
            }
        }
        roopcount += 1;
    }
    println!("合計 {} 回ループしました", roopcount);
}

// ==================== main ====================
fn main() {
    let stdin = io::stdin();
    let mut sc = Scanner::new(BufReader::new(stdin.lock()));
    let mut out = io::BufWriter::new(io::stdout());

    // 入力: N M L U
    let n = sc.next_usize();
    let m = sc.next_usize();
    let l = sc.next_i64() as i128;
    let u = sc.next_i64() as i128;

    // A 構築（案C）→ 出力
    let (a, groups, _layers, _s) = build_cards(n, m, l, u);
    for i in 0..n { if i > 0 { write!(out, " ").unwrap(); } write!(out, "{}", a[i]).unwrap(); }
    writeln!(out).unwrap();
    out.flush().unwrap(); // B を受け取るため flush

    // B 読取
    let mut b = vec![0i128; m];
    for j in 0..m { b[j] = sc.next_i64() as i128; }

    // 初期割当（額面降順 × Δ降順）
    let (mut x, mut ssum, mut e) = greedy_assign(&a, m, l, &b, &groups);

    // SA 用の値集合と val_index（降順）
    let mut values: Vec<i128> = groups.iter().map(|g| g.0).collect();
    values.sort_by(|a, b| b.cmp(a)); values.dedup();

    let mut val_index: HashMap<i128, usize> = HashMap::new();
    for (i, &v) in values.iter().enumerate() { val_index.insert(v, i); }

    // L のカードは固定（movable=false）
    let mut movable = vec![true; n];
    for i in 0..m { movable[i] = false; } // 先頭 M 枚（L）
    for i in 0..n { if a[i] == l { movable[i] = false; } }

    // 焼きなまし（前半=単一移動のみ、後半=スワップのみ）
    let time_limit = Duration::from_millis(SA_TIME_MS);
    anneal_two_phase(&a, m, &b, &mut x, &mut ssum, &mut e, &values, &val_index, &movable, time_limit, 0x1234_5678_9ABC_DEF0);

    // X 出力（1 行）
    for i in 0..n { if i > 0 { write!(out, " ").unwrap(); } write!(out, "{}", x[i]).unwrap(); }
    writeln!(out).unwrap();
    out.flush().unwrap();

    if PRINT_TIME {
        eprintln!("[time] SA fixed={}ms (phase1={}ms, phase2={}ms)", SA_TIME_MS, PHASE1_MS, PHASE2_MS);
    }
}
