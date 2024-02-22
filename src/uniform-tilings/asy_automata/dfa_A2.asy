import simplenode;

settings.tex="xelatex";
usepackage("mathpazo");
settings.outformat="eps";

real u = 4cm;
Arrow = Arrow(5);
pen text = white;
pen starttext = black;
pen temp = linewidth(1.2) + fontsize(9pt);

pen nodepen = deepgreen;

draw_t Initial = none;
draw_t State = compose(shadow, filldrawer(nodepen, darkgreen+0.6));
draw_t Accepting = compose(shadow, filler(nodepen),
                           drawer(darkgreen+1.8), drawer(white+0.6));
draw_t Starting = compose(shadow, filler(red),
                           drawer(darkgreen+1.8), drawer(white+0.6));

real u2 = u / sqrt(3);

node
     q0 = Circle("$q_{0}$", (0, 0), text, Starting),
     q1 = Circle("$q_{1}$", q0.pos + u2*dir(30), text, Accepting),
     q2 = Circle("$q_{2}$", q0.pos + u2*N, text, Accepting),
     q3 = Circle("$q_{3}$", q0.pos + u2*dir(-30), text, Accepting),
     q4 = Circle("$q_{4}$", q3.pos + u2*S, text, Accepting),
     q5 = Circle("$q_{5}$", q4.pos + u2*S, text, Accepting),
     q6 = Circle("$q_{6}$", q5.pos + u2*dir(30), text, Accepting),
     q7 = Circle("$q_{7}$", q1.pos + u2*dir(-30), text, Accepting),
     q8 = Circle("$q_{8}$", q3.pos + u2*dir(-30), text, Accepting),
     q9 = Circle("$q_{9}$", q8.pos + u2*dir(30), text, Accepting),
     q10 = Circle("$q_{10}$", q9.pos + u2*N, text, Accepting),
     q11 = Circle("$q_{11}$", q10.pos + u2*N, text, Accepting),
     q12 = Circle("$q_{12}$", q10.pos + u2*dir(150), text, Accepting);

currentpen = temp;
node start = Circle("$\mathrm{Start}$", q0.pos + u/2.5*W, starttext, Initial);
draw(start, q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12);
draw(start -- q0 @ shorten(-2, 4), Arrow);

shorten = shorten(4, 4);
currentpen = temp + red*0.8;
draw(Label("$s_0$", LeftSide),  q0 -- q2 @ shorten, Arrow);
draw(Label("$s_0$", LeftSide),  q1 -- q7 @ shorten, Arrow);
draw(Label("$s_0$", RightSide), q3 -- q8 @ shorten, Arrow);
draw(Label("$s_0$", RightSide), q9 -- q7 @ shorten, Arrow);
draw(Label("$s_0$", LeftSide),  q4 -- q6 @ shorten, Arrow);
draw(Label("$s_0$", LeftSide),  q10 -- q12 @ shorten, Arrow);

currentpen = temp + olive;
draw(Label("$s_1$", RightSide), q0 -- q1 @ shorten, Arrow);
draw(Label("$s_1$", LeftSide),  q2 -- q1 @ shorten, Arrow);
draw(Label("$s_1$", RightSide), q3 -- q4 @ shorten, Arrow);
draw(Label("$s_1$", LeftSide),  q5 -- q4 @ shorten, Arrow);
draw(Label("$s_1$", RightSide), q8 -- q9 @ shorten, Arrow);
draw(Label("$s_1$", LeftSide),  q12 -- q11 @ shorten, Arrow);

currentpen = temp + rgb(30, 144, 255);
draw(Label("$s_2$", RightSide), q0 -- q3 @ shorten, Arrow);
draw(Label("$s_2$", RightSide), q1 -- q3 @ shorten, Arrow);
draw(Label("$s_2$", RightSide), q7 -- q3 @ shorten, Arrow);
draw(Label("$s_2$", LeftSide),  q6 -- q5 @ shorten, Arrow);
draw(Label("$s_2$", RightSide), q9 -- q10 @ shorten, Arrow);
draw(Label("$s_2$", LeftSide),  q11 -- q10 @ shorten, Arrow);
draw(Label("$s_2$", RightSide), q2 .. bend(-110) .. q3 @ shorten, Arrow);

currentpen = temp;
shipout(bbox(xmargin=0.3cm, ymargin=0.2cm, FillDraw(fillpen=white, drawpen=white)));
