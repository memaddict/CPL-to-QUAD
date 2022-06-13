# CPL to QUAD Compilator [OUI - 2021]

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django) ![SLY](https://img.shields.io/badge/-SLY-green)

## Python CPQ



- :bar_chart: Uses [SLY](https://github.com/dabeaz/sly) for lexical & semantic analysis
    
- :hammer: Builds custom AST for direct translations
    
- :scissors: Impelements backpatching & code optimization
 

## What is it?

![Header](https://github.com/memaddict/CPL-to-QUAD/blob/main/Header.webp)

- Python based implementation of CPL to QUAD compiler
- A testing ground for multiple stages and optimizations of real compilers

## Resourses 

This project is based and inspired by [Compilers: Principles, Techniques, and Tools](https://www.amazon.com/Compilers-Principles-Techniques-Alfred-Aho/dp/0201100886/ref=pd_sbs_sccl_2_2/145-5049614-4878630?pd_rd_w=LWE3A&content-id=amzn1.sym.3676f086-9496-4fd7-8490-77cf7f43f846&pf_rd_p=3676f086-9496-4fd7-8490-77cf7f43f846&pf_rd_r=CV8QDMMJJCARGHBHANDW&pd_rd_wg=G9rTE&pd_rd_r=1f337845-8e6a-42e4-9bf3-c1571225a7e5&pd_rd_i=0201100886&psc=1)

## How to run it

**Standart way:**
- Reqiures Python >= 3.8
- Use command line call with single argument, to run the program:

```sh
$ python cpq.py <file_name>.ou
```

- On success, it will:
    - Generate *.qud file, with compiled QUAD code

- Otherwise, it will:
    - Try to recover, by skipping problematic tokens
    - Output ecountered problems to std.error
    - If possible save partial parse to *.dump file

**Alternative way:**
- You can package *.py files to *.exe, making them portable for windows/mac eco-systems
- Easisest way would be to use PyInstaller & Auto PY to EXE package
- To install via PyPi, type:

```sh
$ pip install auto-py-to-exe
```

- To run it's web interface, use:
```sh
$ auto-py-to-exe
```
