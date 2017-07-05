function grl_mpc()
% MPCSS doing steps using zmq communication to environment


%====================
% Initialize ZeroMQ
%====================

% javaclasspath('/home/ivan/matlab/3rdparty/jeromq-0.4.3-SNAPSHOT.jar')
% import org.zeromq.*
% ctx = zmq.Ctx();
% socket = ctx.createSocket(ZMQ.REP);
% socket.bind('tcp://*:7577');
if count(py.sys.path,'') == 0
    insert(py.sys.path,int32(0),'/home/ivan/work/Project/Software/mpc/');
end

socket = py.pyzmq.bind(); % do not block receive


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
r = 5*ones(1,Sl)';

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

%====================
% Call the optimizer:
%====================

trials = 25;
test_interval = 10;
perf = zeros(trials, 1);
for tt = 1:trials
    state = zmq_recv(socket);
    x0 = state(2:3);
    u0 = [0]';		    % intial control input (required for rate constraints)
    
    % run single episode
    [u,y,x, Url] = grl_mpcss(A,B,C,x0,u0,r(2:length(r),:),Hp,Hc,P,rho,uc,duc,yc,dyc, socket);
    
    rr = r(1:size(y,1),:);
    perf(tt) = sum(sum(sqrt((rr-y)*P.*(rr-y)))); % do not account for action since matlab does not know the actual one applied to the system
    if mod(tt-1, test_interval+1) == test_interval
        disp(['> ' num2str(perf(tt))])
    else
        disp(perf(tt))
    end
end

disp(perf)

%=============================
% Make r and y the same length
%=============================
r = r(1:size(y,1),:);
y = y(1:size(y,1),:);

%==================
% PLOT RESULTS
%==================
figure;
for tt = 1:size(u,2),
  subplot(size(u,2),1,tt); 
  [xx,yy] = stairs(Ts*(1:size(u,1)),u(:,tt));
  plot(xx,yy);
end;

figure;
for tt = 1:size(y,2),
  subplot(size(y,2),1,tt); 
  [xx,yy] = stairs(Ts*(1:size(y,1)),r(:,tt));
  plot(xx,yy,'r'); hold on;
  [xx,yy] = stairs(Ts*(1:size(y,1)),y(:,tt));
  plot(xx,yy,'b'); hold off;
end;

% % Simulation
% sz = size(y) - [1 0];
% y = zeros(sz);
% x = x0;
% for i = 1:sz(1)
%     x = A * x + B * u(i, :)';
%     y(i, :) = C * x;
% end
% 
% figure(3),
% for i = 1:size(y,2),
%   subplot(size(y,2),1,i); 
%   [xx,yy] = stairs(Ts*(1:size(y,1)),y(:,i));
%   plot(xx,yy);
% end;


clear xx yy

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
