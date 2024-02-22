import simplenode;

settings.tex="xelatex";
usepackage("mathpazo");
settings.outformat = "eps";

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

node q0 = Circle("$q_0$", (0, 0), text, Starting),
     q1 = Circle("$q_1$", q0.pos + u*S, text, Accepting),
     q3 = Circle("$q_3$", q1.pos + u*E, text, Accepting),
     q2 = Circle("$q_2$", q0.pos + u*E, text, Accepting),
     q4 = Circle("$q_4$", q2.pos + u*E + 0.5u*S, text, Accepting),
     q5 = Circle("$q_5$", q4.pos + u*E, text, Accepting),
     q6 = Circle("$q_6$", q5.pos + u*E, text, Accepting);

node start = Circle("$\mathrm{Start}$", q0.pos + 0.7u*W, starttext, Initial);
draw(start, q0, q1, q2, q3, q4, q5, q6);
draw(start -- q0 @ shorten(-2, 2), Arrow);

currentpen = temp + red*0.8;
draw(Label("$s_0$", RightSide), q0 -- q1 @ shorten, Arrow);
draw(Label("$s_0$", RightSide), q2 -- q3 @ shorten, Arrow);
draw("$s_0$", q5 -- q6 @ shorten, Arrow);

currentpen = temp + olive;
draw(Label("$s_1$", LeftSide), q0 -- q2 @ shorten, Arrow);
draw("$s_1$", q4 -- q5 @ shorten, Arrow);
draw(Label("$s_1$", LeftSide), q1 -- q2 @ shorten, Arrow);

currentpen = temp + rgb(30, 144, 255);
draw(Label("$s_2$", LeftSide), q2 -- q4 @ shorten, Arrow);
draw("$s_2$", q3 -- q4 @ shorten, Arrow);
draw(Label("$s_2$", LeftSide), q0 .. bend(60) .. q4 @ shorten, Arrow);
draw("$s_2$", q1 .. bend(-60) .. q4 @ shorten, Arrow);

shipout(bbox(xmargin=0.3cm, ymargin=0.2cm, FillDraw(fillpen=white, drawpen=white)));
