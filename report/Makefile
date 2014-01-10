# Makefile for latex paper (conference)

all: report.pdf

report.pdf: report.tex authblk.sty usenix.sty
	pdflatex report.tex
	pdflatex report.tex
	pdflatex report.tex

clean:
	rm -rf report.aux report.bbl report.blg report.log report.pdf

