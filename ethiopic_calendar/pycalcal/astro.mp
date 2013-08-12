% astro.mp
% practically wholly inspired by
% D. Roegel "Spheres, great circles and parallels", TUGBoat,
% Vol 30 (2009), Num. 1
%
% I organised Roegel's macros in a package waiting for him to
% publish his own (probably on CTAN?)

% Don't load this package twice:
if known astro_version: expandafter endinput; fi;

numeric astro_version;string astro_date;
astro_version=0.1;
astro_date="2009/12/25";
% The banner:
message "** astro " & decimal (astro_version) &
  " (c) E. Spinielli (wholly inspired by D. Roegel) (" &
  astro_date & ") **";message "";

tracingstats:=1;



let vector=color;
let Xp=redpart; let Yp=greenpart; let Zp=bluepart;

r=5cm;
theta=70;
phi=-15;

%==== dot product ====
def dotproduct(expr Vi,Vj)=
  (Xp(Vi)*Xp(Vj)+Yp(Vi)*Yp(Vj)+Zp(Vi)*Zp(Vj))
enddef;

%==== vector product ====
def vecproduct(expr Vi,Vj)=
  (Yp(Vi)*Zp(Vj)-Zp(Vi)*Yp(Vj),
      Zp(Vi)*Xp(Vj)-Xp(Vi)*Zp(Vj),
      Xp(Vi)*Yp(Vj)-Yp(Vi)*Xp(Vj))
enddef;


vector V[];
V1=(cosd theta,sind theta,0);
V2=(sind(phi)*sind(theta),-sind(phi)*cosd(theta),cosd(phi));
V3=vecproduct(V1,V2);

%==== unit vector ====
def norm(expr V)= sqrt(dotproduct(V,V)) enddef;
def normed(expr V)= (V/norm(V)) enddef;

%==== projection ====
def project(expr V,Va,Vb)=
  (dotproduct(V,Va),
      dotproduct(V,Vb))
enddef;

%==== equator ====
def f_equator(expr r,t)=
  (r*cosd(t),r*sind(t),0)
enddef;
path equator;
equator=
  project(f_equator(r,0),V1,V2)
  for t=10 step 10 until 350:
  ..project(f_equator(r,t),V1,V2)
endfor ..cycle;

%==== ellipse =====
def ellipse(expr ra,rb,an)=
  (fullcircle xscaled 2ra yscaled 2rb rotated an)
enddef;

%==== major angle ellipse ====
vardef ellipse_major_angle(expr p,a)=
  save pa,pc,pi,ra,rb,rc,an;path pc[];pair pa,pi[];ra=.5a;rb=a;
  forever: %================ split ===============
    rc:=.5[ra,rb];pc0:=subpath(0,4) of fullcircle scaled 2rc;
    pa:=pc0 intersectiontimes p;exitif pa<>(-1,-1);ra:=rc;
  endfor;
    %======= find two intersections ======
  pi1=p intersectiontimes pc0;
  pc1=subpath(0,ypart(pi1)-0.01) of pc0;
  pc2=subpath(ypart(pi1)+0.01,length(pc0)) of pc0;
  pi1:=p intersectionpoint pc0;pi2:=p intersectiontimes pc1;
  if pi2=(-1,-1):pi2:=p intersectionpoint pc2;
  else:pi2:=p intersectionpoint pc1;fi;
  pi3=pi1 rotated 180;pi4=pi2 rotated 180; % other intersections
    %======= orientation ======
  pi5=p intersectionpoint (origin--(unitvector(pi2-pi1)*2a));
  pi6=p intersectionpoint (origin--(unitvector(pi1-pi4)*2a));
  if arclength(origin--pi5)>arclength(origin--pi6):an=angle(pi1-pi2);
  else:an=angle(pi1-pi4);fi;
  an % result
enddef;

%==== minor angle ellipse ====
vardef ellipse_minor_axis(expr p,a,an)=
  save pa;pair pa;
  pa=p intersectionpoint (origin--(dir(an+90)*2a));
  arclength(origin--pa) % result
enddef;

%==== rotate around ====
% rotates Va around Vb by the angle a
vardef rotatearound(expr Va,Vb,a)=
  save v;vector v[];
  v0=normed(Vb);v1=dotproduct(Va,v0)*v0;
  v2=Va-v1;v3=vecproduct(v0,v2);
  v4=v2*cosd(a)+v3*sind(a)+v1;
  v4 % result
enddef;

%==== draw_equator ====
% both is bool to draw bothsides
% side is a bool to decide which side to dash
vardef draw_equator(expr both,side)=
  save pa,pb,pc,alpha,equatorMinorAxis;
  path pa,pb,pc;
  alpha=ellipse_major_angle(equator, r);
  equatorMinorAxis=ellipse_minor_axis(equator, r, alpha);
  pa=ellipse(r,equatorMinorAxis,alpha);
  pb=subpath(0,4) of pa;
  pc=subpath(4,8) of pa;
  if both=1:
    if side=1:
      draw pb dashed evenly; % hidden
      draw pc; % visible
    else:
      draw pc dashed evenly; % hidden
      draw pb; % visible
    fi;
  else:
    if side=1:
      draw pc; % visible
    else:
      draw pb; % visible
    fi;
  fi;
enddef;

%==== draw_parallel ====
% phi=latitude, col=color, side=1 or -1 depending on the dashes
vardef draw_parallel(expr phi,col,side)=
  save p;path p[];p0=project(f_parallel(a,0,phi),V1,V2)
    for t=0 step 10 until 360 :..project(f_parallel(a,t,phi),V1,V2) endfor;
    % we now search for the intersections of this parallel
    % with the projection plane:
    % plane: V3x*x+V3y*y+V3z*z=0
    % parallel: x=r*cos(phi)*cos(theta), y=r*cos(phi)*sin(theta), z=r*sin(phi)
    % we search theta:
  save A,B,C,X,Y,ca,cb,cc,delta,nx,tha,thb;
  numeric X[],Y[];ca=Xp(V3);cb=Yp(V3);cc=Zp(V3);
  if cb=0:X1=-(cc/ca)*sind(phi)/cos(phi);nx=1;
  else:
    A=1+(ca/cb)**2;B=2*ca*cc*sind(phi)/(cb*cb);
    C=((cc/cb)*sind(phi))**2-cosd(phi)*cosd(phi);delta=B*B-4A*C;
    if delta<0:nx=0;% no intersection
    else:
      X1=((-B-sqrt(delta))/(2A))/cosd(phi); % = cos(theta)
      X2=((-B+sqrt(delta))/(2A))/cosd(phi); % = cos(theta)
      Y1=-((ca*X1+cc*sind(phi)/cosd(phi))/cb); % = sin(theta)
      Y2=-((ca*X2+cc*sind(phi)/cosd(phi))/cb); % = sin(theta)
      tha=angle(X1,Y1);thb=angle(X2,Y2);nx=2;
    fi;
  fi;
  if nx=0: % totally (in)visible parallel
    if side=1:draw p0 withcolor col;
    else:draw p0 withcolor col dashed evenly;fi;
    message "NO INTERSECTION";
  elseif nx=1:X10=angle(X1,1+-+X1);X11=360-X10;
  else: % general case
    if tha<thb:X10=tha;X11=thb;else:X10=thb;X11=tha;fi;
  fi;
  if nx>0: % determination of the two paths
    p1=project(f_parallel(a,X10,phi),V1,V2)
      for t=X10+1 step 10 until X11:..project(f_parallel(a,t,phi),V1,V2)
    endfor;
    p2=project(f_parallel(a,X11,phi),V1,V2)
      for t=X11+1 step 10 until X10+360:..project(f_parallel(a,t,phi),V1,V2)
    endfor;
      % drawing the two paths
    if side=1:draw p1 withcolor col;
    else:draw p1 withcolor col dashed evenly;fi;
    if side=1:draw p2 withcolor col dashed evenly;
    else:draw p2 withcolor col;fi;
  fi;
enddef;

%==== ecliptic ====
ec_angle=23.5;
def f_ecliptic(expr r,t)=
  (r*(cosd(t),sind(t)*cosd(ec_angle),
        sind(t)*sind(ec_angle)))
enddef;
path ecliptic;
ecliptic=
  project(f_ecliptic(r,0),V1,V2)
  for t=10 step 10 until 350:
  ..project(f_ecliptic(r,t),V1,V2)
endfor ..cycle;

%==== draw_ecliptic ====
% both 1 to draw both sides
% side is a bool to decide which side to dash
vardef draw_ecliptic(expr both,side)=
  save pd,pe,pf,beta,eclipticMinorAxis;
  path pd,pe,pf;
  beta=ellipse_major_angle(ecliptic, r);
  eclipticMinorAxis=ellipse_minor_axis(ecliptic, r, beta);
  pd=ellipse(r,eclipticMinorAxis,beta);
  pe=subpath(0,4) of pd;
  pf=subpath(4,8) of pd;
  if both=1:
    if side=1:
      draw pe dashed evenly; % hidden
      draw pf; % visible
    else:
      draw pf dashed evenly; % hidden
      draw pe; % visible
    fi;
  else:
    if side=1:
      draw pf; % visible
    else:
      draw pe; % visible
    fi;
  fi;
enddef;

%==== lunar orbit ====
% moon_angle=5.145; % true value
moon_angle=15; % exagerated value
Ln=18; % lunar node (angle)
vector B; B=f_ecliptic(r,Ln);
def f_lunar(expr r,t)=
  rotatearound(r*(cosd(t+Ln),
        sind(t+Ln)*cosd(ec_angle),
        sind(t+Ln)*sind(ec_angle)),B,moon_angle)
enddef;
path lunar;
lunar=
  project(f_lunar(r,0),V1,V2)
  for t=10 step 10 until 350:
  ..project(f_lunar(r,t),V1,V2)
endfor ..cycle;

%==== draw_lunar_orbit ====
% both 1 to draw both sides
% side is a bool to decide which side to dash
vardef draw_lunar_orbit(expr both, side)=
  save pn,po,pp,rho,lunarMinorAxis;
  path pn,po,pp;
  rho=ellipse_major_angle(lunar, r);
  lunarMinorAxis=ellipse_minor_axis(lunar, r, rho);
  pn=ellipse(r,lunarMinorAxis,rho);
  po=subpath(0,4) of pn;
  pp=subpath(4,8) of pn;
  if both=1:
    if side=1:
      draw po dashed evenly; % hidden
      draw pp; % visible
    else:
      draw pp dashed evenly; % hidden
      draw po; % visible
    fi;
  else:
    if side=1:
      draw pp; % visible
    else:
      draw po; % visible
    fi;
  fi;
enddef;

%==== North, North Ecliptic ====
vector North,North_Ec, North_Moon;
North=r*(0,0,1);
North_Ec=rotatearound(North,(1,0,0),ec_angle);
North_Moon=rotatearound(North,(1,0,0),moon_angle);

%==== ecliptic meridian ====
% A is a point in space on the ecliptic
% t is an angle
def f_ec_meridian(expr t,A)=
  (A*cosd(t)+North_Ec*sind(t))
enddef;
path ec_meridian;
vector A; A=f_ecliptic(r,48); % point (in space) on ecliptic
ec_meridian=
  project(f_ec_meridian(0,A),V1,V2)
  for t=10 step 10 until 350:
  ..project(f_ec_meridian(t,A),V1,V2)
endfor ..cycle;

%==== meridian ====
% r radius
% lon is an angle of longitude
% t is an angle (latitude)
def f_meridian(expr r,t,lon)=
  (r*(cosd(lon)*sind(t),sind(lon)*sind(t),cosd(t)))
enddef;

%==== draw_meridian ====
% phi is the longitude of the meridian
% both is bool to draw bothsides
% side is a bool to decide which side to dash
vardef draw_meridian(expr phi,both,side)=
  save pk,pl,pm,meridian,lon,v,lambda,meridianMinorAxis;
  vector v;
  path pk,pl,pm,meridian;
  v=(cosd(phi),sind(phi),0);
  lon=angle(Xp(v),Yp(v));
  meridian=
    project(f_meridian(r,0,lon),V1,V2)
    for t=10 step 10 until 350:
    ..project(f_meridian(r,t,lon),V1,V2)
  endfor ..cycle;
  lambda=ellipse_major_angle(meridian, r);
  meridianMinorAxis=ellipse_minor_axis(meridian, r, lambda);
  pk=ellipse(r,meridianMinorAxis,lambda);
  pl=subpath(0,4) of pk;
  pm=subpath(4,8) of pk;
  if both=1:
    if side=1:
      draw pl dashed evenly; % hidden
      draw pm; % visible
    else:
      draw pm dashed evenly; % hidden
      draw pl; % visible
    fi;
  else:
    if side=1:
      draw pm;
    else:
      draw pl;
    fi;
  fi;
enddef;


endinput