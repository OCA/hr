verbatimtex
%&latex
\documentclass[12pt]{article}
  \usepackage{wasysym}
\begin{document}
etex

input astro
input textpath
beginfig(0);
draw fullcircle scaled 2r;
draw_equator(1,1);
draw_ecliptic(1,1);


z0=(0,0); % origin
z1=project((r,0,0),V1,V2); % x-axis
z2=project((0,r,0),V1,V2); % y-axis
z3=project((0,0,r),V1,V2); % z-axis
z4=project(North_Ec,V1,V2);
z6=project(f_ecliptic(r,75),V1,V2);
z7=project(f_equator(r,70),V1,V2);

path p[],q[];
vector ra[], dec[];
ra0=f_equator(r,0);
ra1=f_equator(r,15);
ra2=f_equator(r,30);
ra3=f_equator(r,45);
ra4=f_equator(r,60);
ra5=f_equator(r,285);
ra6=f_equator(r,300);
ra7=f_equator(r,315);
ra8=f_equator(r,330);
ra9=f_equator(r,345);
p0:=project(ra0,V1,V2)..project(ra1,V1,V2)..project(ra2,V1,V2)..project(0.5[ra2,ra3],V1,V2);
draw_meridian(0,1,1);
draw project(ra1-(0,0,2),V1,V2)..project(ra1+(0,0,2),V1,V2);
label.bot(btex $1^h$ etex, project(ra1-(0,0,2),V1,V2));
draw project(ra2-(0,0,2),V1,V2)..project(ra2+(0,0,2),V1,V2);
label.bot(btex $2^h$ etex, project(ra2-(0,0,2),V1,V2));
draw project(ra3-(0,0,2),V1,V2)..project(ra3+(0,0,2),V1,V2);
label.bot(btex $3^h$ etex, project(ra3-(0,0,2),V1,V2));
draw project(ra3-(0,0,2),V1,V2)..project(ra3+(0,0,2),V1,V2);

label.bot(btex $19^h$ etex, project(ra5-(0,0,2),V1,V2));
draw project(ra5-(0,0,2),V1,V2)..project(ra5+(0,0,2),V1,V2);
label.bot(btex $20^h$ etex, project(ra6-(0,0,2),V1,V2));
draw project(ra6-(0,0,2),V1,V2)..project(ra6+(0,0,2),V1,V2);
label.bot(btex $21^h$ etex, project(ra7-(0,0,2),V1,V2));
draw project(ra7-(0,0,2),V1,V2)..project(ra7+(0,0,2),V1,V2);
label.bot(btex $22^h$ etex, project(ra8-(0,0,1),V1,V2));
draw project(ra8-(0,0,2),V1,V2)..project(ra8+(0,0,2),V1,V2);
label.bot(btex $23^h$ etex, project(ra9-(0,0,1),V1,V2));
draw project(ra9-(0,0,2),V1,V2)..project(ra9+(0,0,2),V1,V2);

picture pa;
%pa = thelabel.bot(btex $24^h\!\!=\!0^h$ etex, project(ra0-(0,0,2),V1,V2));
pa = thelabel.bot(btex $0^h$ etex, project(ra0-(0,-2.3,2.3),V1,V2));
unfill bbox pa;
draw pa;

dec0=f_meridian(r,90,0);
dec1=f_meridian(r,80,0);
dec2=f_meridian(r,70,0);
dec3=f_meridian(r,60,0);
dec4=f_meridian(r,50,0);
dec5=f_meridian(r,40,0);
dec6=f_meridian(r,30,0);
dec7=f_meridian(r,100,0);
dec8=f_meridian(r,110,0);
dec9=f_meridian(r,120,0);
q0:=project(dec0,V1,V2)..project(dec1,V1,V2)..project(dec2,V1,V2)..project(dec3,V1,V2)..project(0.5[dec3, dec4],V1,V2);
draw project(dec1-(0,2,0),V1,V2)..project(dec1+(0,2,0),V1,V2);
label.rt(btex $10^{\circ}$ etex, project(dec1+(0,0,2),V1,V2));
draw project(dec2-(0,2,0),V1,V2)..project(dec2+(0,2,0),V1,V2);
label.rt(btex $20^{\circ}$ etex, project(dec2+(0,0,2),V1,V2));
draw project(dec3-(0,2,0),V1,V2)..project(dec3+(0,2,0),V1,V2);
label.rt(btex $30^{\circ}$ etex, project(dec3+(0,0,2),V1,V2));
draw project(dec4-(0,2,0),V1,V2)..project(dec4+(0,2,0),V1,V2);
label.rt(btex $40^{\circ}$ etex, project(dec4+(0,0,2),V1,V2));
draw project(dec5-(0,2,0),V1,V2)..project(dec5+(0,2,0),V1,V2);
label.rt(btex $50^{\circ}$ etex, project(dec5+(0,0,2),V1,V2));
draw project(dec6-(0,2,0),V1,V2)..project(dec6+(0,2,0),V1,V2);
label.rt(btex $60^{\circ}$ etex, project(dec6+(0,0,2),V1,V2));
draw project(dec7-(0,2,0),V1,V2)..project(dec7+(0,2,0),V1,V2);
label.lft(btex $-10^{\circ}$ etex, project(dec7+(0,1,0),V1,V2));
draw project(dec8-(0,2,0),V1,V2)..project(dec8+(0,2,0),V1,V2);
label.lft(btex $-20^{\circ}$ etex, project(dec8+(0,1,0),V1,V2));
draw project(dec9-(0,2,0),V1,V2)..project(dec9+(0,2,0),V1,V2);
label.lft(btex $-30^{\circ}$ etex, project(dec9+(0,1,0),V1,V2));

dec0:=f_meridian(r,130,0);
draw project(dec0-(0,2,0),V1,V2)..project(dec0+(0,2,0),V1,V2);
label.lft(btex $-40^{\circ}$ etex, project(dec0+(0,1,0),V1,V2));

drawarrow z0--0.2z1; label.bot(btex $x$ etex, 0.2z1);
drawarrow z0--0.2z2; label.rt(btex $y$ etex, 0.2z2);
drawarrow z0--0.2z3; label.lft(btex $z$ etex, 0.2z3);
pickup pencircle scaled 1.2pt;
drawarrow p0;
label.top(btex $RA$ etex, (point infinity of p0)+(-1,1));
drawarrow q0;
label.lft(btex $dec$ etex, point infinity of q0);

dotlabel.ulft(btex $\vernal$ etex, z1);
dotlabel.lrt(btex $\libra$ etex, -z1);
dotlabel.llft(btex $N$ etex, z3);
dotlabel.urt(btex $S$ etex, -z3);
dotlabel.llft(btex $E$ etex, z2);
dotlabel.urt(btex $W$ etex, -z2);
dotlabel.llft(btex $N^*$ etex, z4);
dotlabel.urt(btex $S^*$ etex, -z4);
dotlabel.urt(btex $Sol_w$ etex, project(f_ecliptic(r,270),V1,V2));
dotlabel.llft(btex $Sol_s$ etex, project(f_ecliptic(r,90),V1,V2));

pickup defaultpen;
label.rt(btex Ecliptic etex, 1.01z6);
label.rt(btex Celestial equator etex, 1.01z7);
endfig;

beginfig(1);
  draw fullcircle scaled 2r;
  draw_equator(1,1);
  draw_ecliptic(1,1);
  draw_lunar_orbit(1,1);
  draw_meridian(0,1,1);
  
  z0=(0,0); % origin
  z1=project((r,0,0),V1,V2); % x-axis
  z2=project((0,r,0),V1,V2); % y-axis
  z3=project((0,0,r),V1,V2); % z-axis
  z4=project(North_Ec,V1,V2);
  z5=project(f_ecliptic(r,Ln),V1,V2);
  z6=project(f_ecliptic(r,75),V1,V2);
  z7=project(f_equator(r,70),V1,V2);
  z8=project(f_ecliptic(r,310),V1,V2);
  z9=project(f_ecliptic(r,315),V1,V2);

  drawarrow z0--0.2z1; label.bot(btex $x$ etex, 0.2z1);
  drawarrow z0--0.2z2; label.rt(btex $y$ etex, 0.2z2);
  drawarrow z0--0.2z3; label.lft(btex $z$ etex, 0.2z3);
  draw -z1--z1 dashed evenly;
  draw -z3--z3 dashed evenly;

  pickup pencircle scaled 2pt;
  dotlabel.urt(btex $\vernal$ etex, z1);
  dotlabel.bot(btex $\libra$ etex, -z1);
  dotlabel.llft(btex $N$ etex, z3);
  dotlabel.urt(btex $S$ etex, -z3);
  dotlabel.llft(btex $N^*$ etex, z4);
  dotlabel.urt(btex $S^*$ etex, -z4);
  dotlabel.lrt(btex $\ascnode$ etex, z5);

  pickup defaultpen;
  label.rt(btex Celestial equator etex, 1.01z7);
  label.rt(btex Ecliptic etex, 1.01z6);
  label.rt(btex Lunar orbit etex, 1.02*project(f_lunar(r,70),V1,V2));
  drawarrow z8..z9;
endfig;
end