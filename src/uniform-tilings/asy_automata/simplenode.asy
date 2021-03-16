struct node {
    path outline;
    picture stuff;
    pair pos;
    pair E, N, W, S;
    pair dir(pair v)
    {
        path g = shift(pos) * outline;
        pair M = max(g), m = min(g), c = 0.5*(M+m);
        path ray = c -- c + length(M-m)*unit(v);
        return intersectionpoint(g, ray);
    }
    pair angle(real ang)
    {
        return this.dir(dir(ang));
    }
}

void draw(picture pic=currentpicture, node[] nodearr)
{
    for (node nd: nodearr)
        add(pic, shift(nd.pos) * nd.stuff);
}

void draw(picture pic=currentpicture ... node[] nodearr)
{
    draw(pic, nodearr);
}

typedef void draw_t(picture pic, path g);

draw_t compose(... draw_t[] drawfns)
{
    return new void(picture pic, path g) {
        for (draw_t f : drawfns)
            f(pic, g);
    };
}

draw_t none = new void(picture pic, path g){};

draw_t drawer(pen p)
{
    return new void(picture pic, path g) {
        draw(pic, g, p);
    };
}
draw_t drawer=drawer(currentpen);

draw_t filler(pen p)
{
    return new void(picture pic, path g) {
        fill(pic, g, p);
    };
}
draw_t filler=filler(currentpen);

draw_t filldrawer(pen fillpen, pen drawpen=currentpen)
{
    return new void(picture pic, path g) {
        filldraw(pic, g, fillpen, drawpen);
    };
}

draw_t doubledrawer(pen p, pen bg=white)
{
    return compose(drawer(p+linewidth(p)*3), drawer(bg+linewidth(p)));
}
draw_t doubledrawer = doubledrawer(currentpen);

draw_t shadow(pair shift=2SE, real scale=1, pen color=gray)
{
    return new void(picture pic, path g) {
        fill(pic, shift(shift)*scale(scale)*g, color);
    };
}
draw_t shadow=shadow();

node Circle(Label text, pair pos, pen textpen=currentpen,
            draw_t drawfn, real maxrad=0.4cm)
{
    node nd;
    nd.pos = pos;
    label(nd.stuff, text, textpen);
    pair M = max(nd.stuff), m = min(nd.stuff);
    nd.outline = circle(0.5*(M+m), max(0.5*length(M-m), maxrad));
    drawfn(nd.stuff, nd.outline);
    nd.E = nd.dir(E);
    nd.N = nd.dir(N);
    nd.W = nd.dir(W);
    nd.S = nd.dir(S);
    return nd;
}

path operator--(node nd1, node nd2)
{
    path g1 = shift(nd1.pos) * nd1.outline;
    path g2 = shift(nd2.pos) * nd2.outline;
    pair c1 = (max(g1)+min(g1)) / 2;
    pair c2 = (max(g2)+min(g2)) / 2;
    path edge = c1 -- c2;
    edge = firstcut(edge, g1).after;
    edge = lastcut(edge, g2).before;
    return edge;
}

typedef path edgeconnector(node nd1, node nd2);

typedef path edgemaker(node nd);

edgemaker operator..(node nd, edgeconnector con)
{
    return new path(node nd2) {
        return con(nd, nd2);
    };
}

path operator..(edgemaker maker, node nd)
{
    return maker(nd);
}

path operator..(node nd, edgemaker maker)
{
    return maker(nd);
}

edgeconnector bend(real ang)
{
    return new path (node nd1, node nd2) {
        path g1 = shift(nd1.pos) * nd1.outline;
        path g2 = shift(nd2.pos) * nd2.outline;
        pair c1 = (max(g1)+min(g1)) / 2;
        pair c2 = (max(g2)+min(g2)) / 2;
        real deg = degrees(c2 - c1);
        return nd1.angle(deg+ang) {dir(deg+ang)}
            .. {dir(deg-ang)} nd2.angle(180+deg-ang);
    };
}

edgeconnector bendleft = bend(30);
edgeconnector bendright = bend(-30);

edgemaker loop(pair direction, real ratio=1.5)
{
    return new path(node nd) {
        real deg = degrees(direction);
        real angle1 = deg - 15, angle2 = deg + 15;
        pair mid = nd.angle(deg)
            + ratio*fontsize(currentpen)*unit(direction);
        return nd.angle(angle1) {dir(angle1)} .. mid
            .. {-dir(angle2)} nd.angle(angle2);
    };
}

typedef path fpath(path);

path operator@(path p, fpath t)
{
    return t(p);
}

fpath shorten(real pre=0, real post=2)
{
    return new path(path p) {
	return subpath(p, arctime(p, pre), arctime(p, arclength(p)-post));
    };
}
fpath shorten=shorten(2,2);