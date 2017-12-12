TESTS = add1 overlay simple general reload

all:
	cd ..; make
	for name in ${TESTS}; \
	do \
	   cd $${name}; make; cd .. ;\
        done

clean:
	for name in ${TESTS}; \
	do \
	   cd $${name}; make clean; cd ..;\
	done
