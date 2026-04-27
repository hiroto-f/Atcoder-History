use std::cmp::Ordering;
use std::collections::BinaryHeap;
use std::io::{self, BufRead, BufReader, Write};
use std::time::{Duration, Instant};

// ==================== 設定 ====================
const SA_TIME_MS: u64 = 1995;     // ★ 焼きなまし実行時間（固定）


// ==================== 速いスキャナ ====================
struct Scanner<R> {
    reader: R,
    buf: Vec<u8>,
    pos: usize,
}
impl<R: BufRead> Scanner<R> {
    fn new(reader: R) -> Self {
        Self { reader, buf: Vec::with_capacity(1 << 16), pos: 0 }
    }
    fn refill(&mut self) -> bool {
        self.buf.clear();
        self.pos = 0;
        let mut s = String::new();
        match self.reader.read_line(&mut s) {
            Ok(0) => false,
            Ok(_) => {
                self.buf.extend_from_slice(s.as_bytes());
                true
            }
            Err(_) => false,
        }
    }
    fn next_token(&mut self) -> Option<String> {
        loop {
            while self.pos < self.buf.len() && self.buf[self.pos].is_ascii_whitespace() {
                self.pos += 1;
            }
            if self.pos < self.buf.len() {
                let start = self.pos;
                while self.pos < self.buf.len() && !self.buf[self.pos].is_ascii_whitespace() {
                    self.pos += 1;
                }
                return Some(std::str::from_utf8(&self.buf[start..self.pos]).ok()?.to_string());
            }
            if !self.refill() {
                return None;
            }
        }
    }
    fn next_usize(&mut self) -> usize { self.next_token().unwrap().parse().unwrap() }
    fn next_i64(&mut self) -> i64 { self.next_token().unwrap().parse().unwrap() }
}

// ==================== 簡易 RNG (xorshift64) ====================
struct XorShift64 { state: u64 }
impl XorShift64 {
    fn new(mut seed: u64) -> Self {
        if seed == 0 { seed = 0x9E37_79B9_7F4A_7C15; }
        Self { state: seed }
    }
    #[inline] fn next_u64(&mut self) -> u64 {
        let mut x = self.state;
        x ^= x << 7;
        x ^= x >> 9;
        x ^= x << 8;
        self.state = x;
        x
    }
    #[inline] fn gen_usize(&mut self, bound: usize) -> usize { (self.next_u64() as usize) % bound }
    #[inline] fn gen_f64(&mut self) -> f64 { ((self.next_u64() >> 11) as f64) * (1.0 / ((1u64 << 53) as f64)) }
    #[inline] fn gen_range_usize(&mut self, lo: usize, hi: usize) -> usize { lo + self.gen_usize(hi - lo) }
}

// ==================== A（カード）構築：L + 二進層（案Bを実装） ====================
// 返り値：A（値配列）、groups（= 調整カード群の連続ブロック情報 [降順]）、layers, s
// groups は (value, start_index, count)。base(L) は groups に含めない（先頭で M 枚固定）。
fn build_cards(
    n: usize, m: usize, l: i128, u: i128
) -> (Vec<i128>, Vec<(i128, usize, usize)>, usize, i128) {
    let base_count = m;
    let remaining = n.saturating_sub(base_count);
    let max_layers = remaining / m; // 通常 N=500,M=50→9
    let r = u - l;

    let (layers, s) = if r <= 0 || max_layers == 0 {
        (0usize, 0i128)
    } else {
        let layers = max_layers;                      // s 最小化のため最大層
        let denom_u = (1u128 << layers) - 1;
        let r_u = r as u128;
        let s_u = (r_u + denom_u - 1) / denom_u;     // ceil
        (layers, s_u as i128)
    };

    // （額面, 枚数）の在庫を構築
    // 基本は各層 M 枚（k=0..layers-1, value=2^k·s）。
    // 案B：上位2層だけ M/2 枚に削減し、浮いた 2*(M - M/2) = M 枚を s/2 として追加。
    let mut pairs: Vec<(i128, usize)> = Vec::new();
    if layers > 0 && s > 0 {
        // 先に通常の層
        for k in 0..layers {
            let v = ((1u128 << k) * (s as u128)) as i128;
            pairs.push((v, m));
        }
        // 上位2層を削減（layers>=2 のとき）
        if layers >= 2 {
            let reduce_to = m / 2;        // M=50→25
            // 最大額面 = k=layers-1、次点 = k=layers-2
            let top_idx = layers - 1;
            let sec_idx = layers - 2;
            // pairs は昇順(k小→大)で入っているので index で参照可
            let freed_top  = pairs[top_idx].1.saturating_sub(reduce_to);
            let freed_sec  = pairs[sec_idx].1.saturating_sub(reduce_to);
            pairs[top_idx].1 = reduce_to;
            pairs[sec_idx].1 = reduce_to;

            // s/2 を追加（合計 freed_top+freed_sec 枚）
            let half = std::cmp::max(1i128, s / 2);
            let extra = freed_top + freed_sec;       // 通常は M 枚
            if extra > 0 {
                pairs.push((half, extra));
            }
        }
    }

    // pairs を額面降順に（高額面から割り当てやすく）
    pairs.sort_by(|a, b| b.0.cmp(&a.0));

    // A を構築：先頭に base L を M 枚、その後 groups を順に並べる
    let mut a: Vec<i128> = Vec::with_capacity(n);
    for _ in 0..m { a.push(l); }

    let mut groups: Vec<(i128, usize, usize)> = Vec::new(); // (value, start, count)
    let mut cur = a.len();
    for (v, cnt) in pairs.iter() {
        if *cnt == 0 { continue; }
        let start = cur;
        for _ in 0..*cnt {
            a.push(*v);
        }
        groups.push((*v, start, *cnt));
        cur = a.len();
    }

    // N を満たすための埋め草（1）— これらは groups に含めない（= 初期貪欲の対象外）
    while a.len() < n { a.push(1); }
    if a.len() > n {
        // 万一オーバーしたら、最後の groups から削る（通常は起きない）
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
    groups: &[(i128, usize, usize)], // 調整カード群（降順）
) -> (Vec<usize>, Vec<i128>, i128) {
    let n = a.len();
    let mut x = vec![0usize; n];

    // Base L を山 1..M に一枚ずつ
    let mut ssum = vec![0i128; m];
    for j in 0..m {
        x[j] = j + 1;
        ssum[j] += l;
    }

    // Δ = B - L
    let mut delta: Vec<i128> = b.iter().map(|&bj| bj - l).collect();

    // 最大Δの山を選ぶヒープ（Δが同じなら index 小さい方を先）
    #[derive(Clone, Copy, Eq)]
    struct Item(i128, usize);
    impl Ord for Item {
        fn cmp(&self, other: &Self) -> Ordering {
            // i128 は Ord を持つ。最大ヒープにしたいのでそのまま。
            match self.0.cmp(&other.0) {
                Ordering::Equal => self.1.cmp(&other.1),
                o => o,
            }
        }
    }
    impl PartialOrd for Item {
        fn partial_cmp(&self, other: &Self) -> Option<Ordering> { Some(self.cmp(other)) }
    }
    impl PartialEq for Item {
        fn eq(&self, other: &Self) -> bool { self.0 == other.0 && self.1 == other.1 }
    }

    let mut heap = BinaryHeap::with_capacity(m);
    for j in 0..m { heap.push(Item(delta[j], j)); }

    // 額面降順の各グループについて、Δが額面以上の山に配る
    for &(value, start, count) in groups.iter() {
        let mut assigned = 0usize;
        for idx in start..start + count {
            // Δが value 未満の山しか残っていないなら、この額面はもう配れない
            loop {
                if let Some(Item(d, j)) = heap.pop() {
                    if d != delta[j] {
                        // ステール→無視
                        continue;
                    }
                    if d < value {
                        // これ以上は配れない（最大Δが不足）
                        heap.push(Item(d, j)); // 戻す
                        break;
                    }
                    // 配る
                    x[idx] = j + 1;
                    ssum[j] += value;
                    delta[j] -= value;
                    heap.push(Item(delta[j], j));
                    assigned += 1;
                    break;
                } else {
                    // 山が空（理論上起きない）
                    break;
                }
            }
            // もし配れなかったら（break で出てきたら）、残りは捨て
            if assigned == 0 {
                // この額面は誰にも配れない状況→以降の同額面も配れない
                break;
            }
        }
    }

    // 誤差
    let mut e: i128 = 0;
    for j in 0..m { e += (ssum[j] - b[j]).abs(); }
    (x, ssum, e)
}

// ==================== 焼きなまし（単一移動・固定） ====================
fn anneal(
    a: &[i128], m: usize, b: &[i128],
    x: &mut [usize], ssum: &mut [i128], e: &mut i128,
    time_limit: Duration, seed: u64,
) {
    let n = a.len();
    let start = Instant::now();
    let mut rng = XorShift64::new(seed);
    let mut roopcount = 0;

    // D = S - B
    let mut d: Vec<i128> = (0..m).map(|j| ssum[j] - b[j]).collect();

    // 温度（1山あたり誤差ベース）
    let mut e_f = (*e) as f64;
    if e_f < 1.0 { e_f = 1.0; }
    let t0 = e_f / (m as f64);
    let tend = 1.0f64;

    while start.elapsed() < time_limit {
        let progress = (start.elapsed().as_secs_f64() / time_limit.as_secs_f64()).min(1.0);
        let mut t = t0 * (tend / t0).powf(progress);
        if t < 1e-12 { t = 1e-12; }

        // ランダムに 1 枚を別の行き先へ
        let i = rng.gen_usize(n);
        let v = a[i];
        let p = x[i];
        let mut q = p;
        for _ in 0..3 {
            let cand = rng.gen_range_usize(0, m + 1); // 0=捨て, 1..M
            if cand != p { q = cand; break; }
        }
        if q == p { continue; }

        // ΔE を O(1) で評価（最大2山）
        let mut old_part: i128 = 0;
        let mut new_part: i128 = 0;
        if p != 0 {
            let dp = d[p - 1];
            old_part += dp.abs();
            new_part += (dp - v).abs();
        }
        if q != 0 {
            let dq = d[q - 1];
            old_part += dq.abs();
            new_part += (dq + v).abs();
        }
        let d_e = new_part - old_part;

        // 受理
        let accept = if d_e <= 0 { true } else { (-(d_e as f64) / t).exp() > rng.gen_f64() };
        if accept {
            if p != 0 { d[p - 1] -= v; ssum[p - 1] -= v; }
            if q != 0 { d[q - 1] += v; ssum[q - 1] += v; }
            x[i] = q;
            *e += d_e;
        }
        roopcount += 1;
    }
    println!("合計 {} 回ループしました", roopcount);
}

// ==================== main ====================
fn main() {
    let global_start = Instant::now();

    let stdin = io::stdin();
    let mut sc = Scanner::new(BufReader::new(stdin.lock()));
    let mut out = io::BufWriter::new(io::stdout());

    // 1) N M L U
    let n = sc.next_usize();
    let m = sc.next_usize();
    let l = sc.next_i64() as i128;
    let u = sc.next_i64() as i128;

    // 2) カード A（案B）を構築して 1 行出力
    let (a, groups, _layers, _s) = build_cards(n, m, l, u);
    for i in 0..n {
        if i > 0 { write!(out, " ").unwrap(); }
        write!(out, "{}", a[i]).unwrap();
    }
    writeln!(out).unwrap();
    out.flush().unwrap(); // B を受け取るため flush

    // 3) B（M 個）を空白区切りで読み取り
    let mut b = vec![0i128; m];
    for j in 0..m { b[j] = sc.next_i64() as i128; }

    // 4) 初期解（額面降順 × Δ降順の貪欲）
    let (mut x, mut ssum, mut e) = greedy_assign(&a, m, l, &b, &groups);

    // 5) 焼きなまし：固定時間
    let time_limit = Duration::from_millis(SA_TIME_MS);
    anneal(&a, m, &b, &mut x, &mut ssum, &mut e, time_limit, 0x1234_5678_9ABC_DEF0);

    // 6) X を 1 行出力（0=捨て, 1..M=山）
    for i in 0..n {
        if i > 0 { write!(out, " ").unwrap(); }
        write!(out, "{}", x[i]).unwrap();
    }
    writeln!(out).unwrap();
    out.flush().unwrap();

}
