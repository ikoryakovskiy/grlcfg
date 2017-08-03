function grl_mpc(varargin)
% MPCSS doing steps using zmq communication to environment

close all
%warning off

maxNumCompThreads(4)

%====================
% Initialize ZeroMQ
%====================

% if count(py.sys.path,'') == 0
%     insert(py.sys.path,int32(0),'/home/ivan/work/Project/Software/mpc/');
% end

port = '5557';
if nargin == 1
    port = num2str(varargin{1});
end

socket = py.pyzmq.bind(port); % do not block receive


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

Sl = 430;                % step length
r = pi * ones(Sl, 1);

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

Ts = 0.002;
tau = 0.1111;
km = 18.65;

% state-space model
A = [0 1; 0 -1/tau];
B = [0; km/tau];
C = [1 0];
sys = ss(A,B,C,0);
sysd = c2d(sys,Ts);
A = sysd.A;
B = sysd.B;
C = sysd.C;

% % A car with viscous friction
% Ts = 1;
% m  = 1;
% rr = 1.0;
% ve = exp(-rr*Ts/m);
% A = [1 m*(1-ve)/rr; 0 ve];
% B = [Ts/rr - m*(1-ve)/(rr*rr); (1-ve)/rr];
% C = [1 0];

%====================
% Call the optimizer:
%====================

trials = 60000;
test_interval = 10;
perf = zeros(trials, 1);
for tt = 1:trials
    state = zmq_recv(socket);
    x0 = state(2:3);
    u0 = [0]';		    % intial control input (required for rate constraints)
    
    % run single episode
    [u,y,x] = grl_mpcss(A,B,C,x0,u0,r(2:length(r),:),Hp,Hc,P,rho,uc,duc,yc,dyc, socket);
    
%     rr = r(1:size(y,1),:);
%     perf(tt) = sum(sum(sqrt((rr-y)*P.*(rr-y)))); % do not account for action since matlab does not know the actual one applied to the system
%     if mod(tt-1, test_interval+1) == test_interval
%         disp(['> ' num2str(perf(tt))])
%     else
%         disp(perf(tt))
%     end
end

disp(perf)

%=============================
% Make r and y the same length
%=============================
r = r(1:size(y,1),:);
y = y(1:size(y,1),:);

%====================
% Evaluate performace
%====================
perf = sum(sum(sqrt((r-y)*P.*(r-y))));
disp(perf);

%====================
% ZMQ close
%====================
py.pyzmq.close(socket);

end
