function [u,y,x,f] = mpcss(A,B,C,x,u,r,Hp,Hc,P,rho,uc,duc,yc,dyc, arg)
% MPCSS model-based predictive control in MIMO state-space form
%        for the time being, only deterministic model
%
% [u,y,x] = mpcss(A,B,C,x,u,r,Hp,Hc,P,rho,uc,duc,yc,dyc)
%
%       A,B,C  ... model matrices in discrete-time form (m,n,p are the
%                  input, state and output dimensions, respectively)
%       u,x    ... last input, current state
%       r      ... reference matrix [r(k+1), ..., r(k+Hp), ..., r(k+N)]
%       Hp,Hc  ... prediction and control horizon, respectively
%       P,rho  ... output and input weighting matrix, respectively
%                  also a sequence of weighting matrices can be supplied,
%                  e.g. [P(k+1), P(k+2), ..., P(k+Hp)]
%                  Optional, by default P = eye(p), rho = zeros(m).
%       uc,duc ... input level and rate constraints, respectively
%       yc,dyc ... output level and rate constraints, respectively
%                  each constraint is a 2-column matrix with first column
%                  the lower bound and second column the upper bound
%                  All constraints are optional.
%
%       u      ... optimal control input [u(k), ..., u(k+N-Hp)]
%                  if N = Hp, only u(k) is returned, otherwise, the
%                  controller-model series is simulated for N-Hp+1 steps
%                  (single-step and batch mode, respectively)
%       x,y    ... state and output of the simulated model, respectively
%
%  See MPCDEM1, MPCDEM2, MPCDEM3, MPCSIM, SFUNMPC.

% (c) Robert Babuska, 1997-2017

%==================
% make sure x and u are columns
%==================
x = x(:);
u = u(:);

%==================
% get system dimensions
%==================
n = size(A,1); 
m = size(B,2);
p = size(C,1);

%=================================
% take care of default parameters:
%=================================
if nargin < 9,   P = eye(p); end;
if isempty(P),   P = eye(p); end;
if nargin < 10,  rho = zeros(m); end;
if isempty(rho), rho = zeros(m); end;
if nargin < 11,  uc = ones(m,1)*[-inf inf]; end;
if isempty(uc),  uc = ones(m,1)*[-inf inf]; end;
if nargin < 12,  duc = ones(m,1)*[-inf inf]; end;
if isempty(duc), duc = ones(m,1)*[-inf inf]; end;
if nargin < 13,  yc = ones(p,1)*[-inf inf]; end;
if isempty(yc),  yc = ones(p,1)*[-inf inf]; end
if nargin < 14,  dyc = ones(p,1)*[-inf inf]; end;
if isempty(dyc), dyc = ones(p,1)*[-inf inf]; end

%================
% get constraints
%================
umin  = uc(:,1);  umax  = uc(:,2);
dumin = duc(:,1); dumax = duc(:,2);
ymax  = yc(:,2);  ymin  = yc(:,1);
dymin = dyc(:,1); dymax = dyc(:,2);
%omax  = oc(:,2);  omin  = oc(:,1);

%==============================================
% span the weighting matrices over the horizons
%==============================================
if size(rho,1) == m;
  rho1 = zeros(m*Hc);
  for i = 1 : Hc,
    rho1((i-1)*m+(1:m),(i-1)*m+(1:m)) = rho;
  end;
  rho = rho1;
end;

if size(P,1) == p;
  P1 = zeros(p*Hp);
  for i = 1 : Hp,
    P1((i-1)*p+(1:p),(i-1)*p+(1:p)) = P;
  end;
  P = P1;
end;

%=====================
% Make extended system
%=====================
%Ae = [A B;[zeros(m,n) eye(m)]];
%Be = [B;eye(m)];
%Ce = [C zeros(p,m)];
Ae = A;
Be = B;
Ce = C;

n = size(Ae,1); 
m = size(Be,2);
p = size(Ce,1);
N = size(A,1);
%xe= [x;u];
xe = x;
ye= Ce*Ae*xe;

%==================
% Auxilliary variables
%==================
Hp1 = ones(1,Hp);
Hc1 = ones(1,Hc);
ImHc = eye(Hc*m);

RRR = zeros(p*Hp,m);
for i= 1:Hp,
  RRR((i-1)*p+(1:p),:) = Ce*(Ae^(i-1))*Be;
end

%==================
% Construct the Ru matrix
% speed-up possible
%==================
Ru=[];
for i = 1:Hc
  Ru = [Ru [ zeros((i-1)*p,m); RRR(1:p*(Hp+1-i),:) ] ];
end;

%==================
% Construct the Rx matrix
%==================
Rx=zeros(p*Hp,n);
for i = 1:Hp
  Rx((i-1)*p+(1:p),:) = Ce*(Ae^(i-1));
end

%==================
% Auxilliary matrix
%==================
RRR = zeros(p*Hp,m);
for i= 1:Hp+2,
  RRR((i-1)*p+(1:p),:) = Ce*(Ae^(i-1))*Be - sign(i-1)*Ce*(Ae^(i-2))*Be;
end

%==================
% Construct the dRu matrix for delta y constraints
% speed-up possible
%==================
dRu = RRR(2*p+1:size(RRR,1),:);
if Hc > 1,
  dRu = [dRu RRR(p+1:size(RRR,1)-p,:)];
end;
for i = 3:Hc,
  dRu = [dRu [zeros((i-3)*p,m);RRR(1:p*(Hp+3-i),:)]];
end;

%==================
% Construct the dRx matrix for delta y constraints
%==================
dRx=Ce*Ae - Ce;
for i = 1:Hp-1,
  dRx = [dRx; Ce*(Ae^i) - Ce*(Ae^(i-1))];
end;

%==================
% These two are also needed for delta y constraints
%==================
Ru1 = Ru(1:p,:);
Rx1 = Rx(1:p,:);

%==================
% Construct the Iu matrix which contains Hp identity-matrices stacked
% on each other.
%==================
e = eye(m);
Iu = zeros(m,Hc*m);
e1 = e(:);
Iu(:) = e1(:,ones(1,Hc));
Iu = Iu';                    

%==================
% Construct the Idu matrix which contains Hp identity-matrices in
% the lower triangular part of the matrix
%==================
xx = zeros(Hc*m);
Idu = Iu(:);
xx(:) = Idu(:,ones(1,Hc));
Idu = triu(xx)';

%==================
% Additional variables needed for constraint handling
%==================
umax1  = umax(:,Hc1); umax1 = umax1(:);
umin1  = umin(:,Hc1); umin1 = umin1(:);
dumax1 = dumax(:,Hc1); dumax1 = dumax1(:);
dumin1 = dumin(:,Hc1); dumin1 = dumin1(:);
ymax1  = ymax(:,Hp1); ymax1 = ymax1(:);
ymin1  = ymin(:,Hp1); ymin1 = ymin1(:);
dymax1 = dymax(:,Hp1); dymax1 = dymax1(:);
dymin1 = dymin(:,Hp1); dymin1 = dymin1(:);
%omax1  = omax(:,Hp1); omax1 = omax1(:);
%omin1  = omin(:,Hp1); omin1 = omin1(:);

%==================
% Construct the gamma matrix 
%==================
Gamma = [Idu;-Idu;ImHc;-ImHc;Ru;-Ru;Ru1;dRu;-Ru1;-dRu];

%==================
% Construct H:
%==================
H = 2*(Ru'*P*Ru + rho);

%==================
% MAIN SIMULATION LOOP
%==================

uu = u(:,1);

f = zeros(size(u));
y = C*x(:, 1);

for k=1:size(r,1)-Hp+1

    w = r(k:k+Hp-1,:)';

    if size(r,1) > Hp, home,disp(k), end;

    %------
    % Construct Omega, Gamma is already available
    %------
    Omega = [ umax1  - Iu*uu
             -umin1  + Iu*uu
          dumax1
         -dumin1		
          ymax1  - Rx*Ae*xe(:,k)
         -ymin1  + Rx*Ae*xe(:,k)
          dymax  - Rx1*Ae*xe(:,k)+ye(:,k)
          dymax1 - dRx*Ae*xe(:,k)
         -dymin  + Rx1*Ae*xe(:,k)-ye(:,k)
         -dymin1 + dRx*Ae*xe(:,k)
        ];

    %----------------------------------------------------------
    % Construct c', based on Ru and Rx, H is already available
    %----------------------------------------------------------
    c = 2*(Ru'*P'*(Rx*Ae*xe(:,k)-w(:)))';

    %------
    % Calculate the Controller output
    %------
    %  du_op(:,k)=qp(H,c,Gamma,Omega);
    opt = optimset;
    opt.Display = 'off';
    warning off;
    ind = ~isinf(Omega);
    Omega1 = Omega(ind,:);
    Gamma1 = Gamma(ind,:);
    du_op(:,k)  = quadprog(H,c,Gamma1,Omega1,[],[],[],[],[],opt);
    %------
    % Calculate the Controller output without constraints
    %------
    %  du_op(:,k)=-inv(0.5*H)*0.5*c';
    %------
    % Integrate u
    %------
    u(:,k)=du_op(1:m,k);
    %u(:,k) = uu + du(:,k);
    uu = u(:,k);

    uf  = u(:,k);

    if arg.model == 1 % real system
        f(:, k) = friction_tanh(x(2,k), uf, 0.5);
        uf = uf - f(:, k);
    end

    x(:,k+1) = A*x(:,k)+B*uf;
    y(:,k+1) = C*x(:,k+1);

    xe(:, k+1) = x(:,k+1);
    ye(:, k+1) = y(:,k+1);

end;
u = u'; x = x'; y = y'; f = f';
end


function F = friction(xd, uc, kc)

    zero_tolerance = 1E-11;
    
    if (xd > zero_tolerance || (abs(xd) <= zero_tolerance && uc > kc))
        F = kc;
    elseif (xd < -zero_tolerance || (abs(xd) <= zero_tolerance && uc < -kc))
        F = -kc;
    elseif (abs(xd) <= zero_tolerance && abs(uc) <= kc)
        F = uc;
    else
        error('unexpected condition');
    end
    
end


function F = friction_new(xd, uc, kc)

    zero_tolerance = 1E-11;

    ridge = 0.1;
    if (abs(xd) < ridge)
        alpha = abs(xd)/ridge;
    else
        alpha = 1;
    end
    
    if (xd > zero_tolerance || (abs(xd) <= zero_tolerance && uc > kc))
        F = kc*alpha;
    elseif (xd < -zero_tolerance || (abs(xd) <= zero_tolerance && uc < -kc))
        F = -kc*alpha;
    elseif (abs(xd) <= zero_tolerance && abs(uc) <= kc)
        F = uc;
    else
        error('unexpected condition');
    end
    
end

function F = friction_tanh(xd, uc, kc)

    zero_tolerance = 1E-11;

    ridge = 2000;
    alpha = tanh(ridge*xd);
    
    if (xd > zero_tolerance || (abs(xd) <= zero_tolerance && uc > kc))
        F = kc*alpha;
    elseif (xd < -zero_tolerance || (abs(xd) <= zero_tolerance && uc < -kc))
        F = -kc*alpha;
    elseif (abs(xd) <= zero_tolerance && abs(uc) <= kc)
        F = uc;
    else
        error('unexpected condition');
    end
    
end

