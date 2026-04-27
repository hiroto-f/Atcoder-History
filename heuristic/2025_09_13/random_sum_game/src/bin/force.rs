use std::cmp::Ordering;
use std::collections::BinaryHeap;
use std::io::{self, BufRead, BufReader, Write};
use std::time::{Duration, Instant};

// =============== 設定 ===============
const SA_TIME_MS: u64 = 1995;     // ★ 焼きなまし 1.99s 固定

// =============== 速いスキャナ ===============
struct Scanner<R> {
    reader: R,
    buf: Vec<u8>,
    pos: usize,
}
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
                let start = self.pos;
                while self.pos < self.buf.len() && !self.buf[self.pos].is_ascii_whitespace() { self.pos += 1; }
                return Some(std::str::from_utf8(&self.buf[start..self.pos]).ok()?.to_string());
            }
            if !self.refill() { return None; }
        }
    }
    fn next_usize(&mut self) -> usize { self.next_token().unwrap().parse().unwrap() }
    fn next_i64(&mut self) -> i64 { self.next_token().unwrap().parse().unwrap() }
}

// =============== 簡易 RNG (xorshift64) ===============
struct XorShift64 { state: u64 }
impl XorShift64 {
    fn new(mut seed: u64) -> Self { if seed == 0 { seed = 0x9E37_79B9_7F4A_7C15; } Self { state: seed } }
    #[inline] fn next_u64(&mut self) -> u64 { let mut x=self.state; x^=x<<7; x^=x>>9; x^=x<<8; self.state=x; x }
    #[inline] fn gen_usize(&mut self, bound: usize) -> usize { (self.next_u64() as usize) % bound }
    #[inline] fn gen_f64(&mut self) -> f64 { ((self.next_u64() >> 11) as f64) * (1.0 / ((1u64 << 53) as f64)) }
    #[inline] fn gen_range_usize(&mut self, lo: usize, hi: usize) -> usize { lo + self.gen_usize(hi - lo) }
}

// =============== A 構築：案C+（上位4層をさらに攻め、s/2,s/4,s/8を投入） ===============
fn build_cards(
    n: usize, m: usize, l: i128, u: i128
) -> (Vec<i128>, Vec<(i128, usize, usize)>, usize, i128) {
    let base_count = m;
    let remaining = n.saturating_sub(base_count);
    let max_layers = remaining / m;  // 通常 N=500,M=50→9
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

    // (額面, 枚数)
    let mut pairs: Vec<(i128, usize)> = Vec::new();
    if layers > 0 && s > 0 {
        // 二進層（各 M 枚）
        for k in 0..layers {
            let v = ((1u128 << k) * (s as u128)) as i128;
            pairs.push((v, m));
        }

        // ---- 案C+：上位4層を 0.44/0.52/0.64/0.72 に削減、s/2 と s/4 と s/8 を追加 ----
        if layers >= 4 {
            let idx_top = layers - 1;
            let idx2    = layers - 2;
            let idx3    = layers - 3;
            let idx4    = layers - 4;

            let keep_top = ((m as f64) * 0.44).ceil() as usize; // 例:22/50
            let keep_2nd = ((m as f64) * 0.52).ceil() as usize; // 26/50
            let keep_3rd = ((m as f64) * 0.64).ceil() as usize; // 32/50
            let keep_4th = ((m as f64) * 0.72).ceil() as usize; // 36/50

            let new_top = keep_top.min(m);
            let new_2nd = keep_2nd.min(m);
            let new_3rd = keep_3rd.min(m);
            let new_4th = keep_4th.min(m);

            let mut freed: usize = 0;
            freed += pairs[idx_top].1.saturating_sub(new_top);
            freed += pairs[idx2].1.saturating_sub(new_2nd);
            freed += pairs[idx3].1.saturating_sub(new_3rd);
            freed += pairs[idx4].1.saturating_sub(new_4th);

            pairs[idx_top].1 = new_top;
            pairs[idx2].1    = new_2nd;
            pairs[idx3].1    = new_3rd;
            pairs[idx4].1    = new_4th;

            // 追加：s/2 を M 枚、s/8 を round(0.12*M) 枚、残りは s/4
            let half  = std::cmp::max(1i128, s / 2);
            let quart = std::cmp::max(1i128, s / 4);
            let eighth= std::cmp::max(1i128, s / 8);

            if freed > 0 {
                let add_half = freed.min(m);
                let mut rest = freed - add_half;

                let add_eighth = ((m as f64) * 0.12).round() as usize; // 例: 6/50
                let add_eighth = add_eighth.min(rest);
                rest -= add_eighth;

                let add_quart = rest;
                if add_half > 0   { pairs.push((half,   add_half)); }
                if add_quart > 0  { pairs.push((quart,  add_quart)); }
                if add_eighth > 0 { pairs.push((eighth, add_eighth)); }
            }
        } else {
            // 層が少ない場合も、上位から順に 0.6..0.8 程度を残して freed を作り、
            // s/2 と s/4（余力あれば s/8）を投入（簡易フォールバック）
            let mut freed: usize = 0;
            let reduce_ratio = [0.6, 0.7, 0.8]; // 層数に応じて
            let cap = layers.min(reduce_ratio.len());
            for t in 0..cap {
                let idx = layers - 1 - t;
                let keep = ((m as f64) * reduce_ratio[t]).ceil() as usize;
                let keep = keep.min(m);
                freed += pairs[idx].1.saturating_sub(keep);
                pairs[idx].1 = keep;
            }
            if freed > 0 {
                let half  = std::cmp::max(1i128, s / 2);
                let quart = std::cmp::max(1i128, s / 4);
                let eighth= std::cmp::max(1i128, s / 8);
                let add_half = freed.min(m);
                let mut rest = freed - add_half;
                let add_eighth = ((m as f64) * 0.12).round() as usize;
                let add_eighth = add_eighth.min(rest);
                rest -= add_eighth;
                let add_quart = rest;
                if add_half > 0   { pairs.push((half,   add_half)); }
                if add_quart > 0  { pairs.push((quart,  add_quart)); }
                if add_eighth > 0 { pairs.push((eighth, add_eighth)); }
            }
        }
    }

    // 額面降順
    pairs.sort_by(|a, b| b.0.cmp(&a.0));

    // A 構築：先頭に L×M、その後 groups（value, start, count）
    let mut a: Vec<i128> = Vec::with_capacity(n);
    for _ in 0..m { a.push(l); }

    let mut groups: Vec<(i128, usize, usize)> = Vec::new();
    let mut cur = a.len();
    for (v, cnt) in pairs.iter() {
        if *cnt == 0 { continue; }
        let start = cur;
        for _ in 0..*cnt { a.push(*v); }
        groups.push((*v, start, *cnt));
        cur = a.len();
    }

    // N 充足（余りは 1）
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

// =============== 初期割当（額面降順 × Δ降順） ===============
fn greedy_assign(
    a: &[i128], m: usize, l: i128, b: &[i128],
    groups: &[(i128, usize, usize)],
) -> (Vec<usize>, Vec<i128>, i128) {
    let n = a.len();
    let mut x = vec![0usize; n];

    // Base L を各山へ
    let mut ssum = vec![0i128; m];
    for j in 0..m { x[j] = j + 1; ssum[j] += l; }

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
                    if d != delta[j] { continue; }     // stale
                    if d < value {
                        heap.push(Item(d, j));         // 戻す
                        break;                          // これ以上この額面は配れない
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

    let mut e: i128 = 0;
    for j in 0..m { e += (ssum[j] - b[j]).abs(); }
    (x, ssum, e)
}

// =============== 焼きなまし（単一移動, 1990ms） ===============
fn anneal(
    a: &[i128], m: usize, b: &[i128],
    x: &mut [usize], ssum: &mut [i128], e: &mut i128,
    time_limit: Duration, seed: u64,
) {
    let mut roopcount = 0;
    let n = a.len();
    let start = Instant::now();
    let mut rng = XorShift64::new(seed);

    let mut d: Vec<i128> = (0..m).map(|j| ssum[j] - b[j]).collect();

    let mut e_f = (*e) as f64;
    if e_f < 1.0 { e_f = 1.0; }
    let t0 = e_f / (m as f64);
    let tend = 1.0f64;

    while start.elapsed() < time_limit {
        let progress = (start.elapsed().as_secs_f64() / time_limit.as_secs_f64()).min(1.0);
        let mut t = t0 * (tend / t0).powf(progress);
        if t < 1e-12 { t = 1e-12; }

        let i = rng.gen_usize(n);
        let v = a[i];
        let p = x[i];
        let mut q = p;
        for _ in 0..3 {
            let cand = rng.gen_range_usize(0, m + 1);
            if cand != p { q = cand; break; }
        }
        if q == p { continue; }

        let mut old_part: i128 = 0;
        let mut new_part: i128 = 0;
        if p != 0 { let dp = d[p - 1]; old_part += dp.abs(); new_part += (dp - v).abs(); }
        if q != 0 { let dq = d[q - 1]; old_part += dq.abs(); new_part += (dq + v).abs(); }
        let d_e = new_part - old_part;

        let accept = if d_e <= 0 { true } else { (-(d_e as f64) / t).exp() > rng.gen_f64() };
        if accept {
            if p != 0 { d[p - 1] -= v; ssum[p - 1] -= v; }
            if q != 0 { d[q - 1] += v; ssum[q - 1] += v; }
            x[i] = q;
            *e += d_e;
        }
    }
}

// =============== main ===============
fn main() {
    let global_start = Instant::now();

    let stdin = io::stdin();
    let mut sc = Scanner::new(BufReader::new(stdin.lock()));
    let mut out = io::BufWriter::new(io::stdout());

    // 入力: N M L U
    let n = sc.next_usize();
    let m = sc.next_usize();
    let l = sc.next_i64() as i128;
    let u = sc.next_i64() as i128;

    // A 構築（案C+）→ 出力
    let (a, groups, _layers, _s) = build_cards(n, m, l, u);
    for i in 0..n { if i > 0 { write!(out, " ").unwrap(); } write!(out, "{}", a[i]).unwrap(); }
    writeln!(out).unwrap();
    out.flush().unwrap();

    // B 読取
    let mut b = vec![0i128; m];
    for j in 0..m { b[j] = sc.next_i64() as i128; }

    // 初期割当（額面降順 × Δ降順）
    let (mut x, mut ssum, mut e) = greedy_assign(&a, m, l, &b, &groups);

    // SA（1990ms）
    let time_limit = Duration::from_millis(SA_TIME_MS);
    anneal(&a, m, &b, &mut x, &mut ssum, &mut e, time_limit, 0x1234_5678_9ABC_DEF0);

    // X 出力
    for i in 0..n { if i > 0 { write!(out, " ").unwrap(); } write!(out, "{}", x[i]).unwrap(); }
    writeln!(out).unwrap();
    out.flush().unwrap();
}
