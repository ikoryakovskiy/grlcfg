function perf = mpcdem4()
% demo for the MPCSS function (called in the batch mode)

close all

%====================
% Choose model 0 - no friction, 1 - with friction
%====================
arg.model = 1; 

%====================
% Set MPC parameters:
%====================

Hp = 30;                 % prediction horizon
Hc = 2;                 % control horizon
P = diag(1);         % output (state) weighting matrix
rho = diag(1);        % input (control) weighting matrix


%===============================
% Generate the reference signal:
%===============================

Sl = 1230;                % step length
r = pi * ones(Sl, 1);

%==================
% Constraints
%==================
%        LB  UB
uc  =  [-inf inf		%   level - first input
        ];	%   level - second input
duc =  [-inf inf		% -0.1 0.1		%   rate  - first input
        ];	%   rate  - second input

yc  =  [-inf inf		%   level - first output
        ];	%   level - first output
dyc =  [-inf inf		%   rate  - first output
        ];	%   rate  - first output

%==================
% Define the system matrices:
%==================

Ts = 0.002;
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
[u,y,x,f] = mpcss(A,B,C,x0,u0,r(2:length(r),:),Hp,Hc,P,rho,uc,duc,yc,dyc, arg);

%=============================
% Make r and y the same length
%=============================
r = r(1:size(y,1),:);
y = y(1:size(y,1),:);

%==================
% PLOT RESULTS
%==================
figure;

len = Sl - Hp;

subplot(4,1,1); 
[xx,yy] = stairs(Ts*(1:len), x(1:end-1,1));
plot(xx,yy);
grid on

subplot(4,1,2); 
[xx,yy] = stairs(Ts*(1:len), x(1:end-1,2));
plot(xx,yy);
grid on

subplot(4,1,3); 
[xx,yy] = stairs(Ts*(1:len), u);
plot(xx,yy);
grid on

subplot(4,1,4); 
[xx,yy] = stairs(Ts*(1:len), f);
plot(xx,yy); 
grid on

clear xx yy

%====================
% Evaluate performace
%====================
perf = sum(sum(sqrt((r-y)*P.*(r-y))));
disp(perf);
end
