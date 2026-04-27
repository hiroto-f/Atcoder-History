#include <bits/stdc++.h>
using namespace std;

struct Move {
    int type, i, j, k;
};

struct Cand {
    Move m;
    int score;
};

struct Solver {
    static constexpr int R = 10;

    vector<vector<int>> init_dep;
    vector<vector<int>> dep, sid;
    vector<int> fixed_len;

    vector<vector<Move>> turns;

    int policy = 0;
    mt19937 rng;

    Solver(const vector<vector<int>>& init, int pol)
        : init_dep(init), policy(pol), rng(1234567 + pol * 1009) {}

    void apply_move(const Move& m) {
        if (m.type == 0) {
            auto &a = dep[m.i];
            auto &b = sid[m.j];

            vector<int> block(a.end() - m.k, a.end());
            a.erase(a.end() - m.k, a.end());
            b.insert(b.begin(), block.begin(), block.end());
        } else {
            auto &a = sid[m.j];
            auto &b = dep[m.i];

            vector<int> block(a.begin(), a.begin() + m.k);
            a.erase(a.begin(), a.begin() + m.k);
            b.insert(b.end(), block.begin(), block.end());
        }
    }

    bool valid_move(const Move& m) const {
        if (m.type == 0) {
            if (m.i < 0 || m.i >= R || m.j < 0 || m.j >= R) return false;
            if (m.k <= 0) return false;
            if ((int)dep[m.i].size() - fixed_len[m.i] < m.k) return false;
            if ((int)sid[m.j].size() + m.k > 20) return false;
        } else {
            if (m.i < 0 || m.i >= R || m.j < 0 || m.j >= R) return false;
            if (m.k <= 0) return false;
            if ((int)sid[m.j].size() < m.k) return false;
            if ((int)dep[m.i].size() + m.k > 15) return false;
        }
        return true;
    }

    void normalize_fixed() {
        bool changed = true;

        while (changed) {
            changed = false;

            for (int i = 0; i < R; i++) {
                while (fixed_len[i] < 10 &&
                       (int)dep[i].size() > fixed_len[i] &&
                       dep[i][fixed_len[i]] == 10 * i + fixed_len[i]) {
                    fixed_len[i]++;
                    changed = true;
                }
            }
        }
    }

    bool done() const {
        for (int i = 0; i < R; i++) {
            if (fixed_len[i] != 10) return false;
            if ((int)dep[i].size() != 10) return false;

            for (int c = 0; c < 10; c++) {
                if (dep[i][c] != 10 * i + c) return false;
            }
        }
        return true;
    }

    tuple<int,int,int> find_car(int x) const {
        for (int i = 0; i < R; i++) {
            for (int p = fixed_len[i]; p < (int)dep[i].size(); p++) {
                if (dep[i][p] == x) return {0, i, p};
            }
        }

        for (int j = 0; j < R; j++) {
            for (int p = 0; p < (int)sid[j].size(); p++) {
                if (sid[j][p] == x) return {1, j, p};
            }
        }

        return {-1, -1, -1};
    }

    int target_of(int x) const {
        return x / 10;
    }

    int choose_siding_for_block(const vector<int>& block) const {
        int best_j = -1;
        int best_score = -1e9;

        int tg = target_of(block.back());
        bool same_group = true;
        for (int x : block) {
            if (target_of(x) != tg) same_group = false;
        }

        for (int j = 0; j < R; j++) {
            int free_space = 20 - (int)sid[j].size();
            if (free_space < (int)block.size()) continue;

            int score = free_space * 10;

            if (same_group && j == tg) score += 500;
            if (!sid[j].empty()) {
                int front = sid[j][0];
                if (target_of(front) == tg) score += 100;
            }

            if (policy == 1) score -= abs(j - tg) * 5;
            if (policy == 2) score += (j == tg ? 300 : 0);
            if (policy == 3) score += uniform_int_distribution<int>(0, 50)(const_cast<mt19937&>(rng));

            if (score > best_score) {
                best_score = score;
                best_j = j;
            }
        }

        return best_j;
    }

    vector<Cand> generate_candidates() {
        vector<Cand> cs;

        normalize_fixed();

        // 1. 待避線先頭に次に必要な車両があるなら、直接入れる
        for (int i = 0; i < R; i++) {
            if (fixed_len[i] >= 10) continue;
            if ((int)dep[i].size() != fixed_len[i]) continue;

            int need = 10 * i + fixed_len[i];

            for (int j = 0; j < R; j++) {
                if (!sid[j].empty() && sid[j][0] == need) {
                    int sc = 100000;

                    if (i == j) sc += 1000;
                    if (policy == 1) sc -= abs(i - j) * 10;
                    if (policy == 3) sc += uniform_int_distribution<int>(0, 200)(rng);

                    cs.push_back({{1, i, j, 1}, sc});
                }
            }
        }

        // 2. 出発線の固定済みprefixより後ろにある邪魔な suffix を待避線へ送る
        for (int i = 0; i < R; i++) {
            int temp = (int)dep[i].size() - fixed_len[i];
            if (temp <= 0) continue;

            int max_k = min(temp, 10);

            for (int k = max_k; k >= 1; k--) {
                vector<int> block(dep[i].end() - k, dep[i].end());
                int j = choose_siding_for_block(block);

                if (j == -1) continue;

                int same = 1;
                for (int x : block) {
                    if (target_of(x) != target_of(block[0])) same = 0;
                }

                int sc = 2000 + 80 * k;
                if (same) sc += 300;
                if (j == target_of(block.back())) sc += 300;
                if (policy == 2) sc += k * k * 10;
                if (policy == 3) sc += uniform_int_distribution<int>(0, 100)(rng);

                cs.push_back({{0, i, j, k}, sc});
                break;
            }
        }

        // 3. 待避線内にある次の必要車両を露出させるため、前方blockを出発線へ逃がす
        for (int goal = 0; goal < R; goal++) {
            if (fixed_len[goal] >= 10) continue;
            if ((int)dep[goal].size() != fixed_len[goal]) continue;

            int need = 10 * goal + fixed_len[goal];
            auto [kind, line, pos] = find_car(need);

            if (kind != 1 || pos <= 0) continue;

            int s = line;

            for (int d = 0; d < R; d++) {
                if (d == goal && fixed_len[d] < 10) continue;

                int free_space = 15 - (int)dep[d].size();
                if (free_space <= 0) continue;

                int k = min(pos, free_space);
                if (k <= 0) continue;

                int sc = 1000 + 70 * k;
                sc += max(0, 10 - abs(d - s)) * 5;

                if (policy == 1) sc -= abs(d - s) * 5;
                if (policy == 2) sc += free_space * 10;
                if (policy == 3) sc += uniform_int_distribution<int>(0, 100)(rng);

                cs.push_back({{1, d, s, k}, sc});
            }
        }

        // 4. 次に必要な車両が出発線の一時領域にある場合、上の邪魔を除去する
        for (int goal = 0; goal < R; goal++) {
            if (fixed_len[goal] >= 10) continue;

            int need = 10 * goal + fixed_len[goal];
            auto [kind, d, pos] = find_car(need);

            if (kind != 0) continue;

            int above = (int)dep[d].size() - pos - 1;

            if (above > 0) {
                int max_k = min(above, 10);

                for (int k = max_k; k >= 1; k--) {
                    vector<int> block(dep[d].end() - k, dep[d].end());
                    int j = choose_siding_for_block(block);

                    if (j == -1) continue;

                    int sc = 3000 + 100 * k;
                    if (policy == 3) sc += uniform_int_distribution<int>(0, 100)(rng);

                    cs.push_back({{0, d, j, k}, sc});
                    break;
                }
            } else {
                // need 自身が tail にあるが、正しい出発線ではない場合はいったん待避線へ送る
                if (!(d == goal && pos == fixed_len[goal])) {
                    vector<int> block = {need};

                    for (int j = 0; j < R; j++) {
                        if ((int)sid[j].size() >= 20) continue;

                        int sc = 5000;
                        if (j == goal) sc += 1000;
                        if (policy == 1) sc -= abs(j - goal) * 10;
                        if (policy == 3) sc += uniform_int_distribution<int>(0, 100)(rng);

                        cs.push_back({{0, d, j, 1}, sc});
                    }
                }
            }
        }

        vector<Cand> filtered;
        for (auto &c : cs) {
            if (valid_move(c.m)) filtered.push_back(c);
        }

        return filtered;
    }

    vector<Move> select_non_crossing_dp(const vector<Cand>& cs) {
        vector<int> by_i[R];
        for (int idx = 0; idx < (int)cs.size(); idx++) {
            by_i[cs[idx].m.i].push_back(idx);
        }

        const int NEG = -1e9;

        int dp[11][11];
        int par_last[11][11];
        int par_cand[11][11];

        for (int i = 0; i <= R; i++) {
            for (int j = 0; j <= R; j++) {
                dp[i][j] = NEG;
                par_last[i][j] = -1;
                par_cand[i][j] = -2;
            }
        }

        dp[0][0] = 0; // last_j = -1 を index 0 とする

        for (int i = 0; i < R; i++) {
            for (int last_idx = 0; last_idx <= R; last_idx++) {
                if (dp[i][last_idx] <= NEG / 2) continue;

                // skip
                if (dp[i][last_idx] > dp[i + 1][last_idx]) {
                    dp[i + 1][last_idx] = dp[i][last_idx];
                    par_last[i + 1][last_idx] = last_idx;
                    par_cand[i + 1][last_idx] = -1;
                }

                int last_j = last_idx - 1;

                for (int idx : by_i[i]) {
                    int j = cs[idx].m.j;
                    if (j <= last_j) continue;

                    int nj = j + 1;
                    int val = dp[i][last_idx] + cs[idx].score;

                    if (val > dp[i + 1][nj]) {
                        dp[i + 1][nj] = val;
                        par_last[i + 1][nj] = last_idx;
                        par_cand[i + 1][nj] = idx;
                    }
                }
            }
        }

        int best_last = 0;
        for (int j = 1; j <= R; j++) {
            if (dp[R][j] > dp[R][best_last]) best_last = j;
        }

        vector<Move> res;

        int cur_last = best_last;
        for (int i = R; i >= 1; i--) {
            int idx = par_cand[i][cur_last];
            int prev = par_last[i][cur_last];

            if (idx >= 0) {
                res.push_back(cs[idx].m);
            }

            cur_last = prev;
        }

        reverse(res.begin(), res.end());
        return res;
    }

    bool fallback_one_move() {
        normalize_fixed();

        for (int i = 0; i < R; i++) {
            if (fixed_len[i] >= 10) continue;

            int need = 10 * i + fixed_len[i];

            if ((int)dep[i].size() > fixed_len[i]) {
                int k = (int)dep[i].size() - fixed_len[i];
                vector<int> block(dep[i].end() - k, dep[i].end());
                int j = choose_siding_for_block(block);

                if (j != -1) {
                    Move m{0, i, j, min(k, 20 - (int)sid[j].size())};
                    if (valid_move(m)) {
                        turns.push_back({m});
                        apply_move(m);
                        return true;
                    }
                }
            }

            auto [kind, line, pos] = find_car(need);

            if (kind == 1) {
                if (pos == 0 && (int)dep[i].size() == fixed_len[i]) {
                    Move m{1, i, line, 1};
                    if (valid_move(m)) {
                        turns.push_back({m});
                        apply_move(m);
                        return true;
                    }
                }

                for (int d = 0; d < R; d++) {
                    if (d == i) continue;

                    int free_space = 15 - (int)dep[d].size();
                    if (free_space <= 0) continue;

                    Move m{1, d, line, min(pos, free_space)};
                    if (valid_move(m)) {
                        turns.push_back({m});
                        apply_move(m);
                        return true;
                    }
                }
            }

            if (kind == 0) {
                int above = (int)dep[line].size() - pos - 1;

                if (above > 0) {
                    for (int j = 0; j < R; j++) {
                        int free_space = 20 - (int)sid[j].size();
                        if (free_space <= 0) continue;

                        Move m{0, line, j, min(above, free_space)};
                        if (valid_move(m)) {
                            turns.push_back({m});
                            apply_move(m);
                            return true;
                        }
                    }
                } else {
                    for (int j = 0; j < R; j++) {
                        if ((int)sid[j].size() >= 20) continue;

                        Move m{0, line, j, 1};
                        if (valid_move(m)) {
                            turns.push_back({m});
                            apply_move(m);
                            return true;
                        }
                    }
                }
            }
        }

        return false;
    }

    vector<vector<Move>> run() {
        dep = init_dep;
        sid.assign(R, {});
        fixed_len.assign(R, 0);
        turns.clear();

        normalize_fixed();

        // 初期状態で使える正しいprefixは残し、それ以外を一斉に待避線へ逃がす
        vector<Move> first;

        for (int i = 0; i < R; i++) {
            int k = (int)dep[i].size() - fixed_len[i];
            if (k > 0) {
                Move m{0, i, i, k};
                first.push_back(m);
            }
        }

        if (!first.empty()) {
            turns.push_back(first);
            for (auto &m : first) apply_move(m);
        }

        normalize_fixed();

        int safety = 0;

        while (!done() && (int)turns.size() < 4000 && safety < 10000) {
            safety++;

            normalize_fixed();

            auto cs = generate_candidates();
            auto selected = select_non_crossing_dp(cs);

            if (selected.empty()) {
                bool ok = fallback_one_move();
                if (!ok) break;
                continue;
            }

            turns.push_back(selected);

            for (auto &m : selected) {
                if (!valid_move(m)) {
                    return {};
                }
            }

            for (auto &m : selected) {
                apply_move(m);
            }

            normalize_fixed();
        }

        normalize_fixed();

        if (!done()) return {};
        if ((int)turns.size() > 4000) return {};

        return turns;
    }
};

bool check_answer(
    const vector<vector<int>>& init,
    const vector<vector<Move>>& turns
) {
    const int R = 10;

    vector<vector<int>> dep = init;
    vector<vector<int>> sid(R);

    if ((int)turns.size() > 4000) return false;

    for (auto &turn : turns) {
        if (turn.empty() || (int)turn.size() > R) return false;

        vector<int> used_i(R, 0), used_j(R, 0);

        for (auto &m : turn) {
            if (m.type < 0 || m.type > 1) return false;
            if (m.i < 0 || m.i >= R || m.j < 0 || m.j >= R) return false;
            if (m.k <= 0) return false;

            if (used_i[m.i] || used_j[m.j]) return false;
            used_i[m.i] = used_j[m.j] = 1;
        }

        for (int a = 0; a < (int)turn.size(); a++) {
            for (int b = a + 1; b < (int)turn.size(); b++) {
                int i1 = turn[a].i, j1 = turn[a].j;
                int i2 = turn[b].i, j2 = turn[b].j;

                if (i1 < i2 && !(j1 < j2)) return false;
                if (i2 < i1 && !(j2 < j1)) return false;
            }
        }

        for (auto &m : turn) {
            if (m.type == 0) {
                if ((int)dep[m.i].size() < m.k) return false;
                if ((int)sid[m.j].size() + m.k > 20) return false;
            } else {
                if ((int)sid[m.j].size() < m.k) return false;
                if ((int)dep[m.i].size() + m.k > 15) return false;
            }
        }

        for (auto &m : turn) {
            if (m.type == 0) {
                vector<int> block(dep[m.i].end() - m.k, dep[m.i].end());
                dep[m.i].erase(dep[m.i].end() - m.k, dep[m.i].end());
                sid[m.j].insert(sid[m.j].begin(), block.begin(), block.end());
            } else {
                vector<int> block(sid[m.j].begin(), sid[m.j].begin() + m.k);
                sid[m.j].erase(sid[m.j].begin(), sid[m.j].begin() + m.k);
                dep[m.i].insert(dep[m.i].end(), block.begin(), block.end());
            }
        }
    }

    for (int i = 0; i < R; i++) {
        if ((int)dep[i].size() != 10) return false;

        for (int c = 0; c < 10; c++) {
            if (dep[i][c] != 10 * i + c) return false;
        }
    }

    return true;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int R_input;
    cin >> R_input;

    vector<vector<int>> init(10, vector<int>(10));

    for (int r = 0; r < 10; r++) {
        for (int c = 0; c < 10; c++) {
            cin >> init[r][c];
        }
    }

    vector<vector<Move>> best;
    int best_T = INT_MAX;

    auto start = chrono::steady_clock::now();

    int policy = 0;

    while (true) {
        auto now = chrono::steady_clock::now();
        double elapsed = chrono::duration<double>(now - start).count();

        if (elapsed > 1.85) break;

        Solver solver(init, policy);
        auto res = solver.run();

        if (!res.empty() && check_answer(init, res)) {
            int T = (int)res.size();

            if (T < best_T) {
                best_T = T;
                best = res;
            }
        }

        policy++;
    }

    cout << best.size() << '\n';

    for (auto &turn : best) {
        cout << turn.size() << '\n';

        for (auto &m : turn) {
            cout << m.type << ' ' << m.i << ' ' << m.j << ' ' << m.k << '\n';
        }
    }

    return 0;
}