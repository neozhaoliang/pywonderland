# A Tour in the Wonderland of Math with Python

<p align="center"><img src="http://www.pywonderland.com/polytopes/logo.png"/></p>

> A collection of python scripts for drawing beautiful figures or animating interesting algorithms in mathematics.

## 部分项目的中文文档

+ [用 Python 制作演示迷宫算法的 gif 动画](https://neozhaoliang.github.io/post/%E7%A2%89%E5%A0%A1%E7%9A%84%E5%B0%8F%E7%A8%8B%E5%BA%8F%E7%94%A8-python-%E5%88%B6%E4%BD%9C%E6%BC%94%E7%A4%BA%E8%BF%B7%E5%AE%AB%E7%AE%97%E6%B3%95%E7%9A%84-gif-%E5%8A%A8%E7%94%BB/)
+ [用 Python + POV-Ray 绘制多面体和多胞体](https://neozhaoliang.github.io/post/%E9%AB%98%E9%A2%9C%E5%80%BC%E5%B0%8F%E7%A8%8B%E5%BA%8F%E7%94%A8-python---pov-ray-%E7%BB%98%E5%88%B6%E5%A4%9A%E9%9D%A2%E4%BD%93%E5%92%8C%E5%A4%9A%E8%83%9E%E4%BD%93/)
+ [Möbius 变换的分类与上半双曲空间的等距](https://neozhaoliang.github.io/post/m%C3%B6bius-%E5%8F%98%E6%8D%A2%E7%9A%84%E5%88%86%E7%B1%BB%E4%B8%8E%E4%B8%8A%E5%8D%8A%E5%8F%8C%E6%9B%B2%E7%A9%BA%E9%97%B4%E7%9A%84%E7%AD%89%E8%B7%9D/)
+ [用 Python + glsl 制作 Reaction-Diffusion 动画](https://neozhaoliang.github.io/post/%E7%94%A8-python---glsl-%E5%88%B6%E4%BD%9C-reaction-diffusion-%E5%8A%A8%E7%94%BB/)


## About this repo

Math is beautiful, but to truly enjoy it one has to walk a long and painful way before he could stand on the hill and see the full landscape. I hope this repo could help those people without a strong math background get some intuitive understanding of the beauty of math. The topics are chosen largely due to my personal taste:

1. They should produce appealing results.
2. There should be some non-trivial math behind them.
3. The code should be as simple as possible.

I'll use only popular python libs and build all math stuff from the gound. (`sage`, `sympy` and `mathemetica` are not used here)

You can visit the [website for this repository](http://www.pywonderland.com) to see how to use these scripts and get more information of the math behind them.

I'm still building the docs so that there will be more usage & math explanations for each program.

The history commits are deleted (sorry for this) but will not be deleted any more.

**This repository will be always under construction since there are too many interesting things in math that can be shown by code.** Pull requests, issues, questions, and suggestions are all welcomed!

**Warning:** I'll not maintain support for `python<=2.7` any more, please run the code with `python>=3`.


## Featured images

1. Reaction-Diffusion Simulation

    <p align="center"><img src="http://www.pywonderland.com/grayscott/coral.png"/>
    </p>

2. Polytopes and Todd-Coxeter Algorithm

    <p align="center"><img src="http://pywonderland.com/polytopes/uniform-solids.png"/>
    </p>
    <p align="center"><img src="http://pywonderland.com/polytopes/runcinated-16cell.png"/>
    </p>
    <p align="center"><img src="http://pywonderland.com/polytopes/runcitruncated-120cell.png"/>
    </p>
    <p align="center"><img src="http://pywonderland.com/polytopes/600cell.png"/>
    </p>

3. Wilson's Uniform Spanning Tree Algorithm Animation

    <p align="center"><img src="http://www.pywonderland.com/gifmaze/wilson.gif"/>
    </p>

4. Aperiodic Rhombus Tilings

    <p align="center"><img src="http://www.pywonderland.com/debruijn/penrose-scene.png"/>
    </p>


## Programs to come:

- Fractals with orbit trap
- 2D hyperbolic tilings (Escher's circle limit)
- 3D hyperbolic honeycombs

## Dependencies

Python libs: `pip install -r requirements.txt`.

Softwares:

+ `ImageMagick`
+ `FFmpeg`
+ `POV-Ray`
+ `graphviz`

## License

see the LICENSE file.
