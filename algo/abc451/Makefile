CONTEST=abc451
PROBLEMS=a b c d e f

setup:
	mkdir -p $(PROBLEMS)
	for p in $(PROBLEMS); do \
		cd $$p; \
		oj d https://atcoder.jp/contests/$(CONTEST)/tasks/$(CONTEST)_$$p; \
		cd ..; \
	done

test:
	oj t -c "python3 main.py"