use std::io::{self, BufRead, BufReader, Write};
use std::time::{Duration, Instant};

// ==================== 設定 ====================
const SA_TIME_MS: u64 = 1990;     // ★ 焼きなまし実行時間を固定（1.7s）

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

// ==================== A（カード）構築：L + 二進層 ====================
fn build_cards(n: usize, m: usize, l: i128, u: i128) -> (Vec<i128>, usize, i128, Vec<i128>) {
    let base_count = m;
    let remaining = n.saturating_sub(base_count);
    let max_layers = remaining / m;
    let r = u - l;

    let (layers, s) = if r <= 0 || max_layers == 0 {
        (0usize, 0i128)
    } else {
        let layers = max_layers;                    // 使えるだけ使って s を最小化
        let denom_u = (1u128 << layers) - 1;
        let r_u = r as u128;
        let s_u = (r_u + denom_u - 1) / denom_u;   // ceil
        (layers, s_u as i128)
    };

    let mut a = Vec::with_capacity(n);
    for _ in 0..m { a.push(l); }                   // 各山の土台 L

    let mut layer_values = Vec::with_capacity(layers);
    for k in 0..layers {
        let dv = ((1u128 << k) * (s as u128)) as i128;
        layer_values.push(dv);
        for _ in 0..m { a.push(dv); }              // 各層は M 枚
    }
    while a.len() < n { a.push(1); }               // 余りは 1（基本捨て札）

    (a, layers, s, layer_values)
}

// ==================== 初期割当（貪欲） ====================
fn greedy_assign(
    a: &[i128], m: usize, l: i128, b: &[i128],
    layers: usize, layer_values: &[i128],
) -> (Vec<usize>, Vec<i128>, i128) {
    let n = a.len();
    let mut x = vec![0usize; n];

    // Base L を山 1..M に一枚ずつ
    for j in 0..m { x[j] = j + 1; }

    // delta = B - L
    let mut delta: Vec<i128> = b.iter().map(|&bj| bj - l).collect();

    // 上位層から貪欲
    for kk in (0..layers).rev() {
        let dv = layer_values[kk];
        let base_idx = m + kk * m;
        for j in 0..m {
            let idx = base_idx + j;
            if delta[j] >= dv {
                x[idx] = j + 1;
                delta[j] -= dv;
            } else {
                x[idx] = 0;
            }
        }
    }

    // S と E
    let mut ssum = vec![0i128; m];
    for (i, &pile) in x.iter().enumerate() {
        if pile > 0 { ssum[pile - 1] += a[i]; }
    }
    let mut e: i128 = 0;
    for j in 0..m { e += (ssum[j] - b[j]).abs(); }
    (x, ssum, e)
}

// ==================== 焼きなまし（単一移動） ====================
fn anneal(
    a: &[i128], m: usize, b: &[i128],
    x: &mut [usize], ssum: &mut [i128], e: &mut i128,
    time_limit: Duration, seed: u64,
) {
    let n = a.len();
    let start = Instant::now();
    let mut rng = XorShift64::new(seed);

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

        // ランダムに 1 枚選び、別の行き先へ
        let i = rng.gen_usize(n);
        let v = a[i];
        let p = x[i];
        let mut q = p;
        for _ in 0..3 {
            let cand = rng.gen_range_usize(0, m + 1); // 0=捨て, 1..M
            if cand != p { q = cand; break; }
        }
        if q == p { continue; }

        // ΔE を高速評価（最大2山）
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

        // 受理判定
        let accept = if d_e <= 0 {
            true
        } else {
            let prob = (-(d_e as f64) / t).exp();
            rng.gen_f64() < prob
        };
        if accept {
            if p != 0 { d[p - 1] -= v; ssum[p - 1] -= v; }
            if q != 0 { d[q - 1] += v; ssum[q - 1] += v; }
            x[i] = q;
            *e += d_e;
        }
    }
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

    // 2) A を構築して 1 行出力
    let (a, layers, _s, layer_values) = build_cards(n, m, l, u);
    for i in 0..n {
        if i > 0 { write!(out, " ").unwrap(); }
        write!(out, "{}", a[i]).unwrap();
    }
    writeln!(out).unwrap();
    out.flush().unwrap(); // B を受け取るため flush

    // 3) B（M 個）を空白区切りで読み取り
    let mut b = vec![0i128; m];
    for j in 0..m { b[j] = sc.next_i64() as i128; }

    // 4) 初期解（貪欲）
    let (mut x, mut ssum, mut e) = greedy_assign(&a, m, l, &b, layers, &layer_values);

    // 5) 焼きなまし：固定 1.6 秒
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
