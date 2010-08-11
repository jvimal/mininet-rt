
FILES=cpu-stress
FILES+=gettimeofday

all: $(FILES)
	@echo done

cpu-stress: cpu-stress.c
gettimeofday: gettimeofday.c

%.c:
	$(CC) $(CFLAGS) $< -o $@

.PHONY: clean
clean:
	rm $(FILES)

