function perf = mpcdem4()
% demo for the MPCSS function (called in the batch mode)

%====================
% Choose model 0 - no friction, 1 - with friction
%====================
arg.model = 0; 

%====================
% Set MPC parameters:
%====================

Hp = 5;                 % prediction horizon
Hc = 2;                 % control horizon
rho = diag(1);          % input weighting matrix
P = diag(0.05);          % output weighting matrix

%===============================
% Generate the reference signal:
%===============================

Sl = 30;                % step length
r = [5*ones(1,Sl) 0*ones(1,Sl) 5*ones(1,Sl) 0*ones(1,Sl)]';% 5*ones(1,Sl) 0*ones(1,Sl)]';

%==================
% Constraints
%==================
%        LB  UB
uc  =  [-inf inf		%   level - first input
        ];	%   level - second input
duc =  [-inf inf		% -0.1 0.1		%   rate  - first input
        ];	%   rate  - second input

yc  =  [-10 10		%   level - first output
        ];	%   level - first output
dyc =  [-inf inf		%   rate  - first output
        ];	%   rate  - first output

%==================
% Define the system matrices:
%==================

Ts = 0.1;
tau = 0.1111;
km = 18.65;
%G = tf(km,[tau 1 0]);

% state-space model
A = [0 1; 0 -1/tau];
B = [0; km/tau];
C = [1 0];
sys = ss(A,B,C,0);
sysd = c2d(sys,Ts);
A = sysd.A;
B = sysd.B;
C = sysd.C;

x0 = [0 0]';        % initial state
u0 = [0]';		    % intial control input (required for rate constraints)

%====================
% Call the optimizer:
%====================
[u,y,x] = mpcss(A,B,C,x0,u0,r(2:length(r),:),Hp,Hc,P,rho,uc,duc,yc,dyc, arg);

%=============================
% Make r and y the same length
%=============================
r = r(1:size(y,1),:);
y = y(1:size(y,1),:);

%==================
% PLOT RESULTS
%==================
figure;
for i = 1:size(u,2),
  subplot(size(u,2),1,i); 
  [xx,yy] = stairs(Ts*(1:size(u,1)),u(:,i));
  plot(xx,yy);
end;

figure;
for i = 1:size(y,2),
  subplot(size(y,2),1,i); 
  [xx,yy] = stairs(Ts*(1:size(y,1)),r(:,i));
  plot(xx,yy,'r'); hold on;
  [xx,yy] = stairs(Ts*(1:size(y,1)),y(:,i));
  plot(xx,yy,'b'); hold off;
end;

clear xx yy

%====================
% Evaluate performace
%====================
perf = sum(sum(sqrt((r-y)*P.*(r-y))));
disp(perf);
end
