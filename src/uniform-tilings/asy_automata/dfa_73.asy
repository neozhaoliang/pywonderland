import simplenode;

settings.tex="xelatex";
usepackage("mathpazo");
settings.outformat="eps";

real u = 2cm;
Arrow = Arrow(4);
pen text = white;
pen starttext = black;
pen temp = linewidth(0.8) + fontsize(9pt);

pen nodepen = deepgreen;

draw_t Initial = none;
draw_t State = compose(shadow, filldrawer(nodepen, darkgreen+0.6));
draw_t Accepting = compose(shadow, filler(nodepen),
                           drawer(darkgreen+1.8), drawer(white+0.6));
draw_t Starting = compose(shadow, filler(red),
                           drawer(darkgreen+1.8), drawer(white+0.6));

pair V = dir(60);
pair V_conj = dir(270);
pair V_neg = dir(120);
pair S7 = dir(180/7.0);
real a = 120;
real c = 180*5/7;
real dt = 180/6;
real L = 1.6 * u;
pair U = dir(240);

node q8 = Circle("$q_{8}$", (0,0), text, Accepting),
     q9 = Circle("$q_9$", q8.pos + u*V_conj, text, Accepting),
     q10 = Circle("$q_{10}$", rotate(-a, q9.pos)*q8.pos, text, Accepting),
     q11 = Circle("$q_{11}$", rotate(-a, q10.pos)*q9.pos, text, Accepting),
     q12 = Circle("$q_{12}$", rotate(-a, q11.pos)*q10.pos, text, Accepting),
     q6 = Circle("$q_{6}$",   rotate(-a, q12.pos)*q11.pos , text, Accepting),
     q18 = Circle("$q_{18}$", rotate(-c, q11.pos)*q12.pos, text, Accepting),
     q16 = Circle("$q_{16}$", rotate(-c, q18.pos)*q11.pos, text, Accepting),
     q15 = Circle("$q_{15}$", rotate(-c, q16.pos)*q18.pos, text, Accepting),
     q14 = Circle("$q_{14}$", rotate(-c, q15.pos)*q16.pos, text, Accepting),
     q13 = Circle("$q_{13}$", rotate(-c, q14.pos)*q15.pos, text, Accepting),
     q17 = Circle("$q_{17}$", rotate(-108, q13.pos)*q12.pos, text, Accepting),
     q7 = Circle("$q_{7}$", rotate(-108, q17.pos)*q13.pos, text, Accepting),
     q1 = Circle("$q_{1}$", q8.pos+L*U, text, Accepting),
     q0 = Circle("$q_{0}$", rotate(-dt, q8.pos)*q1.pos, text, Starting),
     q2 = Circle("$q_{2}$", rotate(-dt, q8.pos)*q0.pos, text, Accepting),
     q3 = Circle("$q_{3}$", rotate(-dt, q8.pos)*q2.pos, text, Accepting),
     q4 = Circle("$q_{4}$", rotate(-dt, q8.pos)*q3.pos, text, Accepting),
     q5 = Circle("$q_{5}$", rotate(-dt, q8.pos)*q4.pos, text, Accepting);

currentpen = temp;
node start = Circle("$\mathrm{Start}$", q0.pos + u*W, starttext, Initial);
draw(start, q6, q8, q9, q10, q11, q12, q18, q16, q15,
     q14, q13, q17, q7, q1, q2, q0, q3, q4, q5);

draw(start -- q0 @ shorten(-2, 2), Arrow);

currentpen = temp + red*0.8;
draw("$s_0$", q0 -- q1 @ shorten, Arrow);
draw("$s_0$", q2 -- q3 @ shorten, Arrow);
draw("$s_0$", q4 -- q5 @ shorten, Arrow);
draw("$s_0$", q6 -- q7 @ shorten, Arrow);
draw("$s_0$", q9 -- q10 @ shorten, Arrow);
draw("$s_0$", q11 -- q12 @ shorten, Arrow);
draw("$s_0$", q14 -- q15 @ shorten, Arrow);
draw(Label("$s_0$", LeftSide), q16 .. bend(-80) .. q17 @ shorten, Arrow);

currentpen = temp + olive;
draw("$s_1$", q0 -- q2 @ shorten, Arrow);
draw("$s_1$", q3 -- q4 @ shorten, Arrow);
draw("$s_1$", q12 -- q6 @ shorten, Arrow);
draw("$s_1$", q10 -- q11 @ shorten, Arrow);
draw("$s_1$", q13 -- q14 @ shorten, Arrow);
draw("$s_1$", q15 -- q16 @ shorten, Arrow);
draw(Label("$s_1$", LeftSide), q8 -- q9 @ shorten, Arrow);
draw(Label("$s_1$", LeftSide), q17 -- q7 @ shorten, Arrow);
draw(Label("$s_1$", LeftSide), q1 .. bend(70) .. q2 @ shorten, Arrow);
draw(shift(-0.15*u, 0.1*u)*Label("$s_1$", LeftSide), q5 .. bend(30) .. q6 @ shorten, Arrow);

currentpen = temp + rgb(30, 144, 255);
draw("$s_2$", q0 -- q8 @ shorten, Arrow);
draw("$s_2$", q1 -- q8 @ shorten, Arrow);
draw("$s_2$", q2 -- q8 @ shorten, Arrow);
draw("$s_2$", q3 -- q8 @ shorten, Arrow);
draw("$s_2$", q4 -- q8 @ shorten, Arrow);
draw("$s_2$", q5 -- q8 @ shorten, Arrow);
draw("$s_2$", q6 -- q8 @ shorten, Arrow);
draw("$s_2$", q17 -- q13 @ shorten, Arrow);
draw("$s_2$", q16 -- q18 @ shorten, Arrow);
draw("$s_2$", q12 -- q13 @ shorten, Arrow);
draw(Label("$s_2$", RightSide), q7 .. bend(-25) .. q8 @ shorten, Arrow);
draw(Label("$s_2$", LeftSide), q11 -- q18 @ shorten, Arrow);

//label("$\Delta(7,2,3)=\langle s_{0},s_{1},s_{2} \, |\, s^2_{0}=s^2_{1}=s^2_{2}=(s_{0}s_{1})^7=(s_{0}s_{2})^2=(s_{1}s_{2})^3=1\rangle.$",(-0.8u, -2.5u));

shipout(bbox(xmargin=0.3cm, ymargin=0.2cm, FillDraw(fillpen=white, drawpen=white)));
